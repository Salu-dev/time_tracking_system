# Copyright (c) 2026, salu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from time_tracking_system.utils import get_customer_details
from time_tracking_system.api import get_assigned_sales_person

class SalesVisit(Document):
	def before_insert(self):
		if self.customer:
			customer_location = get_customer_details(self.customer)
			if customer_location:
				self.lattitude = customer_location.custom_lttitude
				self.longitude = customer_location.custom_longitude
			self.sales_person = get_assigned_sales_person(self.customer)
		
	def validate(self):
		self.validate_sales_person()
		self.validate_dates()
		self.validate_sales_person_permissions()
		
	def validate_sales_person(self):
		"""Validate sales person assignment"""
		if not self.sales_person:
			frappe.throw("Sales person is required for sales visit, Please assign a sales person")

	def validate_dates(self):
		"""Validate date fields in Sales Visit"""
		# Validate scheduled date is not in the past for new visits
		if self.scheduled_date and (self.is_new() or self.has_value_changed("scheduled_date")):
			today = frappe.utils.nowdate()
			if self.scheduled_date < today and self.status == "Scheduled":
				frappe.throw("Scheduled date cannot be in the past for scheduled visits")
		
		# Validate check-in is not before scheduled date
		if self.check_in and self.scheduled_date and (self.is_new() or self.has_value_changed("check_in") or self.has_value_changed("scheduled_date")):
			if not self.travel_start_time:
				frappe.throw("Travel start time is required when check in is set")
			
			check_in_date = frappe.utils.getdate(self.check_in)
			scheduled_date = frappe.utils.getdate(self.scheduled_date)
			if check_in_date < scheduled_date:
				frappe.throw("Check-in date cannot be before scheduled date")
		
		# Validate check-out is not before check-in
		if self.check_out and self.check_in and (self.is_new() or self.has_value_changed("check_out")):
			if frappe.utils.get_datetime(self.check_out) < frappe.utils.get_datetime(self.check_in):
				frappe.throw("Check-out time cannot be before check-in time")
		

		# Validate travel start time logic
		if self.travel_start_time:
			if self.check_in and frappe.utils.get_datetime(self.travel_start_time) > frappe.utils.get_datetime(self.check_in):
				frappe.throw("Travel start time cannot be after check-in time")
			elif self.scheduled_date:
				travel_date = frappe.utils.getdate(self.travel_start_time)
				scheduled_date = frappe.utils.getdate(self.scheduled_date)
				if travel_date < scheduled_date:
					frappe.throw("Travel start date cannot be before scheduled date")


	def before_save(self):
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.status != self.status:
			if self.status == "In Progress":
				self.check_in = frappe.utils.now_datetime()
				if self.travel_start_time:
					self.travel_time = frappe.utils.time_diff_in_hours(self.check_in, self.travel_start_time)
			elif self.status == "Completed":
				self.time_spent = frappe.utils.time_diff_in_hours(self.check_out, self.check_in)
		if old_doc and (old_doc.customer != self.customer or old_doc.address != self.address):
			customer_location = get_customer_location(self.customer)
			if customer_location:
				self.lattitude = customer_location.custom_lttitude
				self.longitude = customer_location.custom_longitude
		
		# check duplicate schedule 
		if self.customer and self.scheduled_date and self.status == "Scheduled":
			visit = frappe.db.get_value("Sales Visit", {"customer": self.customer, 
			"scheduled_date": self.scheduled_date,"sales_person": self.sales_person,
			"status": ["not in", ["Cancelled", "Completed"]]}, "name")
			if visit:
				frappe.throw("Sales visit already exists for this customer and scheduled date with status not cancelled or completed")

	def validate_sales_person_permissions(self):
		"""Validate that only the assigned sales person can update check-in, check-out, and travel start times"""
		# Allow administrators and sales managers
		if frappe.session.user in ("Administrator"):
			return
			
		old_doc = self.get_doc_before_save()
		if not old_doc:
			return
			
		# Define sensitive fields to monitor
		sensitive_fields = {
			'check_in': self.check_in,
			'check_out': self.check_out,
			'travel_start_time': self.travel_start_time
		}
		
		# Check if any sensitive fields changed
		fields_changed = any(
			getattr(old_doc, field) != value 
			for field, value in sensitive_fields.items()
		)
		
		# Check status changes to specific states
		status_changed = (
			old_doc.status != self.status and 
			self.status in ("In Progress", "Completed", "Traveling")
		)
		
		# If sensitive data changed, validate user permissions
		if fields_changed or status_changed:
			if self.sales_person != frappe.session.user:
				frappe.throw("Only the assigned sales person can update check-in, check-out, travel start time, and status changes")

@frappe.whitelist()
def check_and_update_pending_visits():
    """Check and update pending sales visits"""
    try:
        pending_visits = frappe.get_all("Sales Visit", {"status":["not in", ["Cancelled", "Completed"]], "scheduled_date": ["<", frappe.utils.nowdate()]},pluck="name")
        for visit in pending_visits:
            frappe.db.set_value("Sales Visit", visit, "status", "Pending")
    except Exception as e:
        frappe.log_error(f"Error in check_and_update_pending_visits: {str(e)}")
        frappe.throw(f"Error updating pending visits: {str(e)}")
		
@frappe.whitelist()
def set_sales_visit_permission_query_conditions(user):
    """Set permission query conditions for Sales Visit"""
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    # Allow administrators and sales managers
    if "Administrator" in roles or "Sales Manager" in roles:
        return ""
    if "Sales Person" in roles:
        return "sales_person = '{user}'"
    
    # Sales User → own records
    return f"""
        `tabSales Visit`.`sales_person` = '{user}'
    """