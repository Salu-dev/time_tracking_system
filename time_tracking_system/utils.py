import frappe

# get customer details
def get_customer_details(customer):
    primary_address = frappe.db.get_value("Customer", {"name": customer}, "customer_primary_address")
    if primary_address:
        return frappe.get_doc("Address", primary_address)
    return None

@frappe.whitelist()
def get_user_details():
    user_roles = frappe.get_roles(frappe.session.user)
    return {
        "user": frappe.session.user,
        "roles": user_roles
    }