# Sales Person Time Tracking System (Frappe / ERPNext)

This project is a custom application built on the **Frappe Framework with ERPNext customization** to manage and track sales person visits, time spent, and location details.

---

## 🚀 Features

- Custom **Sales Visit** Doctype
- ERPNext Customization:
  - Customer (assigned_sales_user)
  - Address (latitude, longitude)
- Role-based access:
  - Sales Manager
  - Sales User
- Visit lifecycle:
  - Scheduled → Traveling → In Progress → Completed / Pending / Cancelled
- Time tracking:
  - Travel time
  - Visit duration
- Location tracking:
  - Customer location
  - Check-in / Check-out coordinates
- 📅 Scheduler:
  - Automatically marks overdue visits as **Pending**
- APIs:
  - Frappe Resource API
  - Custom APIs

---

## 🏗️ Tech Stack

- Frappe Framework  
- ERPNext (Customized)

---

## ⚙️ Installation Guide

### 1. Setup Bench

```bash
pip install frappe-bench
bench init frappe-bench
cd frappe-bench
2. Create Site
bench new-site site-name

3. Install ERPNext
bench get-app erpnext
bench --site site-name install-app erpnext

4. Install Time Tracking App
bench get-app time_tracking_system <https://github.com/Salu-dev/time_tracking_system.git>
bench --site site-name install-app time_tracking_system

5. Run Migrate (IMPORTANT ⚠️)
bench --site site-name migrate

👉 This will:

Apply custom fields
Create doctypes
Insert demo users, customers, and addresses
👤 Demo Users
Role	Email
Sales Manager	manager@abc.com

Sales User	sales_user@test.com

Sales User	sales_user@abc.com

🔐 Set Password for Demo Users (Manual Step)

Passwords are not set automatically.

After installation, set passwords manually using:

bench --site site-name set-password manager@abc.com
bench --site site-name set-password sales_user@test.com
bench --site site-name set-password sales_user@abc.com

You will be prompted to enter a password (e.g., 1234).