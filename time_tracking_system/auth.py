import frappe
from frappe.sessions import get_csrf_token

# #get csrf token
@frappe.whitelist(allow_guest=True)
def get_user_csrf_token():
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            return {"authenticated": False}
        
        return {
            "authenticated": True,
            "user": user,

            "csrf_token": get_csrf_token(),
        }
    except Exception as e:
        frappe.log_error(f"Error getting CSRF token: {str(e)}", "CSRF Token Error")
        return {"authenticated": False, "error": str(e)}

@frappe.whitelist()
def get_logged_user():
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            return {"authenticated": False}
        
        return {
            "authenticated": True,
            "user": user,
            "roles": frappe.get_roles(user),
        }
    except Exception as e:
        frappe.log_error(f"Error getting user roles: {str(e)}", "User Roles Error")
        return {"authenticated": False, "error": str(e)}
