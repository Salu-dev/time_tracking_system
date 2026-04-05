import frappe
import json
from frappe.share import add as add_share
from time_tracking_system.utils import get_user_details

# get assigned customers for current sales person
@frappe.whitelist()
def get_assigned_customers():
    user_details = get_user_details()
    user_roles = user_details.get("roles")
    if frappe.session.user == "Administrator" or "Sales Manager" in user_roles:
        customer_list = frappe.get_all("Customer",  
        fields=["customer_name","customer_primary_address.email_id","customer_primary_address.phone","customer_type"])
    else:
        if "Sales User" in user_roles:
            customer_list = frappe.get_all("Customer", filters={"custom_assigned_sales_user": frappe.session.user}, 
            fields=["customer_name","customer_primary_address.email_id","customer_primary_address.phone","customer_type"])
        else:
            customer_list = []
      
    return customer_list

@frappe.whitelist()
def get_assigned_sales_person(customer):
    sales_person = frappe.db.get_value("Customer", customer, "custom_assigned_sales_user")
    return sales_person

@frappe.whitelist()
def get_sales_persons():
    users = frappe.get_all(
        "Has Role",
        filters={"role": "Sales User"},
        fields=["parent as name"]
    )

    user_list = [u.name for u in users]

    return frappe.get_all(
        "User",
        filters={
            "name": ["in", user_list],
            "enabled": 1
        },
        fields=["name", "full_name"]
    )
    

@frappe.whitelist()
def schedule_visit(customers, scheduled_date=None, sales_person=None):
    """
    Schedule sales visits for given customers.
    """
    try:
        if isinstance(customers, str):
            customers = json.loads(customers)  
        for customer in customers:
            # Create sales visit
            visit_doc = frappe.new_doc("Sales Visit")
            visit_doc.customer = customer
            visit_doc.scheduled_date = scheduled_date or frappe.utils.nowdate()
            visit_doc.date = frappe.utils.nowdate()
            visit_doc.sales_person = sales_person 
            visit_doc.insert()
            # share doc to sales person and send email notification
            add_share("Sales Visit", visit_doc.name, sales_person, write=1, share=1)
            frappe.sendmail(
                recipients=sales_person,
                subject="New Sales Visit Scheduled",
                message=f"A new sales visit has been scheduled for {customer} on {scheduled_date}"
            )
            
        return "Visits scheduled successfully"
    except Exception as e:
        frappe.log_error(f"Error scheduling visits: {str(e)}", "Schedule Visit Error")
        return "Error scheduling visits"

@frappe.whitelist()
def get_todays_scheduled_visits():
    """
    Get sales visits for current sales person.
    """
    try:
        today = frappe.utils.nowdate()
        today_visits = frappe.get_list("Sales Visit", filters={"scheduled_date": today,"status":"Scheduled"}, 
        fields=["name", "customer", "scheduled_date", "status","sales_person"])
        return today_visits
        
    except Exception as e:
        frappe.log_error(f"Error getting scheduled visits: {str(e)}", "Get Scheduled Visits Error")
        return "Error getting scheduled visits"

@frappe.whitelist()
def get_sales_visits_history():
    try:
        visit_filter=[]
        data=frappe.form_dict
        from_date=data.get("from_date")
        to_date=data.get("to_date")
        sales_person=data.get("sales_person")
        customer=data.get("customer")
        status=data.get("status")
        limit=int(data.get("limit", 20))
        limit_start=int(data.get("limit_start", 0))
        
        if from_date and to_date:
            visit_filter.append(["scheduled_date", "between", [from_date, to_date]])
        if status:
            visit_filter.append(["status","=",status])
        if sales_person:
            visit_filter.append(["sales_person","=",sales_person])
        if customer:
            visit_filter.append(["customer","=",customer])

        visits = frappe.get_list("Sales Visit", filters=visit_filter, 
        fields=["name", "customer", "scheduled_date", "status","time_spent","travel_time","sales_person"],
        order_by="creation DESC")
        count=len(visits)
        limited_visits = visits[limit_start:limit_start+limit] 
        return {"visits": limited_visits, "count": count}
    except Exception as e:
        frappe.log_error(f"Error getting scheduled visits: {str(e)}", "Get Scheduled Visits Error")
        return "Error getting scheduled visits"

@frappe.whitelist()
def check_in_visit():
    """
    Check in for a specific visit.
    """
    try:
        data=frappe.form_dict
        visit_name=data.get("visit_name")
        latitude=data.get("latitude")
        longitude=data.get("longitude")
        check_in_time=data.get("check_in_time")
        if check_in_time :
            formatted_check_in_time = format_datetime(check_in_time)
        visit = frappe.get_doc("Sales Visit", visit_name)
        
        # Validate that only assigned sales person can check in
        if frappe.session.user not in ["Administrator", "System Manager"]:
            if visit.sales_person != frappe.session.user:
                frappe.throw("Only the assigned sales person can check in for this visit")
        
        visit.status = "In Progress"
        visit.check_in_coordinates = f"{latitude},{longitude}"
        visit.check_in = formatted_check_in_time
        visit.save(ignore_permissions=True)
        return "Visit checked in successfully"
    except Exception as e:
        frappe.log_error(f"Error checking in visit: {str(e)}", "Check In Visit Error")
        return f"Error checking in visit: {str(e)}"

@frappe.whitelist()
def check_out_visit():
    """
    Check out for a specific visit.
    """
    try:
        data = frappe.form_dict
        visit_name = data.get("visit_name")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        check_out_time = data.get("check_out_time")
        visit = frappe.get_doc("Sales Visit", visit_name)
        
        # Validate that only assigned sales person can check out
        if frappe.session.user not in ["Administrator", "System Manager"]:
            if visit.sales_person != frappe.session.user:
                frappe.throw("Only the assigned sales person can check out for this visit")
        if check_out_time:
            formatted_check_out_time = format_datetime(check_out_time)
        visit.status = "Completed"
        visit.check_out_coordinates = f"{latitude},{longitude}"
        visit.save(ignore_permissions=True)
        return "Visit checked out successfully"
    except Exception as e:
        frappe.log_error(f"Error checking out visit: {str(e)}", "Check Out Visit Error")
        return f"Error checking out visit: {str(e)}"


@frappe.whitelist()
def start_visit(visit_name,travel_start_time):
    """
    Start a visit.
    """
    try:
        visit = frappe.get_doc("Sales Visit", visit_name)
        
        # Validate that only assigned sales person can start visit
        if frappe.session.user not in ("Administrator", "Sales Manager"):
            if visit.sales_person != frappe.session.user:
                frappe.throw("Only the assigned sales person can start this visit")
        
        # Convert ISO format to Frappe datetime format
        if travel_start_time and 'T' in travel_start_time:
           formatted_travel_start_time = format_datetime(travel_start_time)
        visit.status = "Traveling"
        visit.travel_start_time = formatted_travel_start_time
        visit.save(ignore_permissions=True)
        return "Visit started successfully"
    except Exception as e:
        frappe.log_error(f"Error starting visit: {str(e)}", "Start Visit Error")
        return f"Error starting visit: {str(e)}"
    

@frappe.whitelist()
def check_and_update_pending_visits():
    """
    Check and update pending visits.
    """
    try:
        visits = frappe.get_all("Sales Visit", filters={"status": "Scheduled","scheduled_date": ["<", frappe.utils.nowdate()]}, fields=["name", "scheduled_date"])
        for visit in visits:
            frappe.db.set_value("Sales Visit", visit.name, "status", "Pending")
        return "Pending visits checked and updated successfully"
    except Exception as e:
        frappe.log_error(f"Error checking and updating pending visits: {str(e)}", "Check and Update Pending Visits Error")
        return f"Error checking and updating pending visits: {str(e)}"
    
def format_datetime(iso_string):
    """
    Convert ISO format to Frappe datetime format
    """
    if not iso_string:
        return iso_string
        
    if 'T' in iso_string:
        # Remove timezone info if present
        if '+' in iso_string:
            iso_string = iso_string.split('+')[0]
        # Convert from "2026-04-05T12:42" to "2026-04-05 12:42:00"
        formatted_time = iso_string.replace('T', ' ')
        # Add seconds if not present
        if len(formatted_time.split(' ')[1]) == 5:  # HH:MM format
            formatted_time += ':00'
        return formatted_time
    return iso_string