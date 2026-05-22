# SecureTask — Secure Task Management System

SecureTask is a secure web-based task management system developed using Django and MySQL, designed according to OWASP Top 10 and OWASP ASVS security practices.

---

# University Information

**University:** Universiti Kuala Lumpur (UniKL MIIT)  
**Course:** Secure Software Development  
**Technology Stack:** Django 4.2 · MySQL · Bootstrap 5 · Django REST Framework

---

# Team Members

| Name | Student ID | Role |
|------|------------|------|
| Luqmanul Hafiz Bin Ahmad Fairul | 52215125409 | Lead Developer & Security Architect |
| Muhammad Iqbal Bin Ruslan | 52215125730 | Backend Developer & Database Engineer |
| Muhammad Akmal Hakim bin Mohd Yuzlan | 52215125582 | Frontend Developer & UI/UX Designer |
| Muhamad Fareez Aiman bin Rozaiman | 52215125751 | QA Engineer & Security Tester |

---

# Features

- User Registration & Authentication
- Role-Based Access Control (RBAC)
- Secure Task CRUD Operations
- REST API Integration
- File Upload Validation
- Audit Logging
- Session Management
- Brute-force Protection
- Content Security Policy (CSP)
- Secure Password Handling
- Admin Dashboard

---

# Security Controls Implemented

| OWASP Category | Implementation |
|----------------|----------------|
| OWASP A01 | RBAC + IDOR prevention |
| OWASP A02 | PBKDF2 password hashing, secrets stored in `.env` |
| OWASP A03 | ORM-only queries, template autoescaping |
| OWASP A04 | File MIME validation, UUID filenames, upload size limits |
| OWASP A05 | CSP headers, secure production settings |
| OWASP A07 | django-axes lockout, session timeout, strong password policy |
| OWASP A09 | Audit logging without storing passwords/tokens |

---

# Prerequisites

Install the following software before running the project:

- Python 3.10+
- MySQL Server 8.0+
- pip

Optional:
- MySQL Workbench
- Visual Studio Code

---

# Windows Setup Guide

## 1. Extract or Clone the Project

Open PowerShell and navigate into the project folder:

```powershell
cd securetask
```
2. Create Virtual Environment
```powershell
python -m venv venv
```

3. Activate Virtual Environment
```powershell
venv\Scripts\activate
```

You should see:
```powershell
(venv)
```

4. Install Dependencies
```powershell
pip install -r requirements.txt
```

5. Windows Compatibility Fix

Install the Windows-compatible magic package:
```powershell
pip install python-magic-bin
```
6. Configure Environment Variables

Copy the example environment file:
```powershell
copy .env.example .env
```
Edit .env and configure:
```powershell
SECRET_KEY=change-this-secret-key
DEBUG=True

DB_NAME=securetask_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306
```
7. Create MySQL Database

Open MySQL:
```powershell
mysql -u root -p
```
Create database:
```SQL
CREATE DATABASE securetask_db CHARACTER SET utf8mb4;
```

8. Run Database Migrations
```powershell
python manage.py makemigrations accounts tasks
python manage.py migrate
```
9. Create Admin Account
```powershell
python manage.py createsuperuser
```

10. Run Development Server
```powershell
python manage.py runserver
```
Open browser:
```
http://127.0.0.1:8000
```
Linux / macOS Setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

mysql -u root -p -e "CREATE DATABASE securetask_db CHARACTER SET utf8mb4;"

python manage.py makemigrations accounts tasks
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Starting and Stopping the Server
Start Server
```powershell
cd securetask
venv\Scripts\activate
python manage.py runserver
```
Stop Server

Press:
```
CTRL + C
```
Default URLs
Page	URL
Home	/
Login	/accounts/login/
Register	/accounts/register/
Dashboard	/dashboard/
Admin Panel	/admin/
API Endpoints (v1)

Base URL:
```
http://127.0.0.1:8000/api/v1/
```
Method	Endpoint	Description
GET/POST	/tasks/	List/Create tasks
GET/PUT/DELETE	/tasks/{id}/	Retrieve/Update/Delete task
POST	/tasks/{id}/complete/	Mark task complete
GET	/users/	Admin user list
GET	/audit-logs/	Audit log access

Authentication:

Session Authentication
Token Authentication
Project Structure
securetask/
├── config/
├── accounts/
├── tasks/
├── api/
├── templates/
├── static/
├── media/
├── logs/
├── manage.py
├── requirements.txt
└── .env.example
Common Issues & Fixes
1. mysql command not recognized
Fix:

Add MySQL bin folder to Windows PATH.

Example:
```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```
2. No module named 'magic'
Fix:
```
pip install python-magic-bin
```
3. Table does not exist
Fix:
```
python manage.py makemigrations
python manage.py migrate
```
Development Notes
Development mode uses DEBUG=True
Production should use:
DEBUG=False
HTTPS
Secure cookies
HSTS enabled
Security Notes
Never commit .env into version control.
Uploaded profile images use UUID filenames.
User passwords are securely hashed using Django authentication.
Secure session handling is enabled.
Authors

Developed for educational and cybersecurity learning purposes at UniKL MIIT.
