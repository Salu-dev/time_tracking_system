import frappe

# get customer details
def get_customer_location(customer):
    primary_address = frappe.db.get_value("Customer", {"name": customer}, "customer_primary_address")
    if primary_address:
        return frappe.get_doc("Address", primary_address)
    return None