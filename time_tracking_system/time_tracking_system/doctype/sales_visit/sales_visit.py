# Copyright (c) 2026, salu and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from time_tracking_system.utils import get_customer_location

class SalesVisit(Document):
	def before_insert(self):
		self.date = frappe.utils.nowdate()
		# self.sales_person = frappe.session.user
		if self.customer:
			customer_location = get_customer_location(self.customer)
			if customer_location:
				self.latitude = customer_location.custom_lttitude 
				self.longitude = customer_location.custom_longitude
		
	def validate(self):
		# check if travel start time is set before check in
		if self.check_in and not self.travel_start_time:
			frappe.throw("Travel start time is required when check in is set")
		if self.check_in and self.travel_start_time:
			if self.travel_start_time > self.check_in:
				frappe.throw("Travel start time cannot be after check in time")
		if self.check_out and self.check_in:
			if self.check_out < self.check_in:
				frappe.throw("Check out time cannot be before check in time")
		# # check duplicate schedule 
		# if self.customer and self.scheduled_date:
		# 	visit = frappe.db.get_value("Sales Visit", {"customer": self.customer, 
		# 	"scheduled_date": self.scheduled_date,"sales_person": self.sales_person,
		# 	"status": ["not in", ["Cancelled", "Completed"]]}, "name")
		# 	if visit:
		# 		frappe.throw("Sales visit already exists for this customer and scheduled date with status not cancelled or completed")


	def before_save(self):
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.status != self.status:
			if self.status == "In Progress":
				self.check_in = frappe.utils.now()
				if self.travel_start_time:
					self.travel_time = frappe.utils.time_diff_in_hours(self.check_in, self.travel_start_time)
			elif self.status == "Completed":
				self.check_out = frappe.utils.now()
				self.time_spend = frappe.utils.time_diff_in_hours(self.check_out, self.check_in)
		if old_doc and (old_doc.customer != self.customer or old_doc.address != self.address):
			customer_location = get_customer_location(self.customer)
			if customer_location:
				self.latitude = customer_location.custom_lattitude
				self.longitude = customer_location.custom_longitude
			
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
		
