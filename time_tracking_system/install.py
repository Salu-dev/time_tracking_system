import frappe
def after_install():
    # create sales user
    if not frappe.db.exists("User", "sales_user@test.com"):
        user = frappe.get_doc({
            "doctype": "User",
            "email": "sales_user@test.com",
            "first_name": "Sales User",
            "enabled": 1,
            "send_welcome_email": 1,
            "roles": [
                {"role": "Sales User"}
            ]
        })
        user.insert(ignore_permissions=True)

    if not frappe.db.exists("User", "sales_user@abc.com"):
        user = frappe.get_doc({
            "doctype": "User",
            "email": "sales_user@abc.com",
            "first_name": "Sales User",
            "enabled": 1,
            "send_welcome_email": 1,
            "roles": [
                {"role": "Sales User"}
            ]
        })
        user.insert(ignore_permissions=True)

    if not frappe.db.exists("User", "sales_manager@test.com"):
        user = frappe.get_doc({
            "doctype": "User",
            "email": "sales_manager@test.com",
            "first_name": "Sales Manager",
            "enabled": 1,
            "send_welcome_email": 1,
            "roles": [
                {"role": "Sales Manager"}
            ]
        })
        user.insert(ignore_permissions=True)
