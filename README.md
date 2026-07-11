# 🛡️ Cyber Incident Reporting Portal

A secure, production-ready web application for reporting, tracking, and managing cyber security incidents. Built with **Flask**, **MySQL**, **Bootstrap 5**, and **Chart.js**.

---

## Features

- **Citizen Portal** — Register, report cyber incidents, upload evidence, track case status
- **Officer Dashboard** — Review assigned cases, update status, add investigation notes, request evidence
- **Admin Dashboard** — Analytics with Chart.js, user/officer management, case assignment, report generation
- **Evidence Management** — Drag-and-drop upload, file preview, secure download
- **Case Tracking** — Status progress bar, timeline, investigation notes
- **Notifications** — In-app notifications for status updates, case assignments, evidence requests
- **Report Generation** — Downloadable PDF and Excel reports
- **Security** — Password hashing, CSRF protection, parameterized queries, session management, input validation, audit logging

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| Backend | Python Flask (Blueprints) |
| Database | SQLite (Built-in) |
| Auth | Flask-Login (session-based) |
| Charts | Chart.js 4.x |
| Reports | ReportLab (PDF), openpyxl (Excel) |

---

## Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)

---

## Installation & Setup

### 1. Clone / Navigate to the project directory

```bash
cd "cyper incident reporting"
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure database (Optional)

By default, the application uses an SQLite database named `cyber_incident_portal.db` in the project root directory. You can customize this in `config.py`:

```python
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'cyber_incident_portal.db'))
```

### 4. Seed the database

The database schema is automatically created and initialized when you run the seed script:

```bash
python seed.py
```

### 5. Run the application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@portal.com | Admin@123 |
| Officer | officer@portal.com | Officer@123 |

---

## Project Structure

```
├── app.py                  # Flask application factory
├── config.py               # Configuration settings
├── database.py             # MySQL connection helpers
├── schema.sql              # Database schema
├── seed.py                 # Default data seeder
├── requirements.txt        # Python dependencies
│
├── models/                 # Data models
│   ├── user.py
│   ├── incident.py
│   ├── evidence.py
│   └── notification.py
│
├── routes/                 # Flask Blueprints
│   ├── auth.py             # Login, register, profile
│   ├── incident.py         # Report, list, detail
│   ├── evidence.py         # Upload, download, delete
│   ├── dashboard.py        # Role-based dashboards
│   ├── officer.py          # Officer case management
│   └── admin.py            # Admin analytics & management
│
├── templates/              # Jinja2 templates
│   ├── base.html           # Master layout
│   ├── auth/               # Login, register, profile
│   ├── incidents/          # New, list, detail
│   ├── dashboard/          # User, officer, admin
│   ├── admin/              # Users, officers, categories, reports
│   └── errors/             # 404, 500
│
├── static/
│   ├── css/style.css       # Dark theme stylesheet
│   └── js/
│       ├── main.js         # UI interactions
│       └── charts.js       # Chart.js configuration
│
├── uploads/                # Evidence file storage
│   ├── images/
│   ├── documents/
│   └── videos/
│
├── reports/                # Generated PDF/Excel reports
└── utils/
    ├── helpers.py          # Shared utilities
    ├── decorators.py       # Role-based decorators
    └── reports.py          # PDF/Excel generation
```

---

## Security Implementation

| Feature | Implementation |
|---|---|
| Password Hashing | `pbkdf2:sha256` via Werkzeug |
| CSRF Protection | Flask-WTF CSRFProtect |
| SQL Injection | Parameterized queries (PyMySQL) |
| XSS Protection | Jinja2 auto-escaping + bleach |
| Session Security | HTTP-only cookies, SameSite=Lax |
| File Upload | Extension whitelist, 16 MB limit, UUID rename |
| Audit Logging | All sensitive actions logged |
| Input Validation | Server-side + client-side |

---

## License

This project is for educational purposes.
