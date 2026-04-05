import frappe

def after_migrate():
    create_users()
    create_customers()
    create_addresses()


# ---------- USERS ----------
def create_users():
    users = [
        {"email": "sales_user@test.com", "first_name": "Sales User", "role": "Sales User"},
        {"email": "sales_user@abc.com", "first_name": "Sales User", "role": "Sales User"},
        {"email": "sales_manager@test.com", "first_name": "Sales Manager", "role": "Sales Manager"},
    ]

    for u in users:
        if not frappe.db.exists("User", u["email"]):
            user = frappe.get_doc({
                "doctype": "User",
                "email": u["email"],
                "first_name": u["first_name"],
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": u["role"]}]
            })
            user.insert(ignore_permissions=True)


# ---------- CUSTOMERS ----------
def create_customers():
    customers = [
        {"name": "GreenLeaf Traders", "user": "sales_user@test.com"},
        {"name": "Tech Solutions Inc", "user": "sales_user@abc.com"},
        {"name": "Global Innovations Ltd", "user": "sales_user@test.com"},
    ]

    for c in customers:
        if not frappe.db.exists("Customer", c["name"]):
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": c["name"],
                "custom_assigned_sales_user": c["user"]
            })
            customer.insert(ignore_permissions=True)


# ---------- ADDRESSES ----------
def create_addresses():
    addresses = [
        {
            "title": "GreenLeaf Traders",
            "line1": "123 Main Street",
            "city": "Los Angeles",
            "state": "California",
            "country": "United States",
            "pincode": "90001",
            "lat": "34.0522",
            "lng": "-118.2437"
        },
        {
            "title": "Tech Solutions Inc",
            "line1": "456 Tech Park",
            "city": "New York",
            "state": "NY",
            "country": "United States",
            "pincode": "10001",
            "lat": "40.7128",
            "lng": "-74.0060"
        },
        {
            "title": "Global Innovations Ltd",
            "line1": "789 Innovation Blvd",
            "city": "Chicago",
            "state": "Illinois",
            "country": "United States",
            "pincode": "60601",
            "lat": "41.8781",
            "lng": "-87.6298"
        }
    ]

    for a in addresses:

        # check using address_title (NOT name)
        if not frappe.db.exists("Address", {"address_title": a["title"]}):

            address = frappe.get_doc({
                "doctype": "Address",
                "address_title": a["title"],
                "address_type": "Billing",
                "address_line1": a["line1"],
                "city": a["city"],
                "state": a["state"],
                "pincode": a["pincode"],
                "country": "United States",
                "custom_lattitude": a["lat"],   
                "custom_longitude": a["lng"],
                "links": [
                    {
                        "link_doctype": "Customer",
                        "link_name": a["title"]
                    }
                ]
            })

            address.insert(ignore_permissions=True)

            # ---------- SET PRIMARY ADDRESS ----------
            frappe.db.set_value(
                "Customer",
                a["title"],
                "customer_primary_address",
                address.name
            )

    frappe.db.commit()