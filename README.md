# CareHospital - Hospital Management System
### Python Full Stack Development Internship Project

A simple, complete, and functional web-based Hospital Management System developed using **Python**, **Django**, **SQLite**, **HTML5**, **CSS3**, **Bootstrap 5**, and **JavaScript**.

---

## 1. Project Overview
CareHospital is a centralized hospital appointment management platform designed to streamline doctor consultations. It provides two key user interfaces:
- **Patient Portal:** Allows patients to register, log in, browse doctors by department, and schedule appointments with real-time slot validation.
- **Admin Portal:** Enables hospital administrators to manage doctor profiles (CRUD), review registered patients, view hospital analytics, and approve or reject appointment requests.

---

## 2. Project Objective
- To demonstrate core Python Full Stack development using Django's MTV (Model-Template-View) architecture.
- To manage relational data with an SQLite database using Django ORM.
- To implement secure user authentication, role-based access control, and form validation.
- To build a clean, responsive medical UI using Bootstrap 5 and vanilla JavaScript without unnecessary complexity.

---

## 3. Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Backend** | Python 3 | Core programming language |
| **Framework** | Django 6 | High-level Python web framework (MTV architecture) |
| **Database** | SQLite3 | Default lightweight relational database |
| **Frontend** | HTML5 & CSS3 | Web page structure and custom styling |
| **UI Library** | Bootstrap 5 | Modern, responsive grid system and components |
| **Interactivity** | Vanilla JavaScript | Show/hide passwords, cancellation alerts, live doctor search |
| **Templating** | Django Templates | Dynamic backend HTML rendering with template inheritance |

---

## 4. Key Features

### A. Patient Features
1. **User Registration & Authentication:** Secure account creation with password hashing and duplicate username prevention.
2. **Interactive Home Page:** Hero banner, hospital overview, departments, and doctor previews.
3. **Doctor Directory:** Browse doctors, filter by medical department, and live search by name using JavaScript.
4. **Appointment Booking:** Schedule appointments by selecting doctor, date, and time slot.
   - Automatically prevents booking past dates.
   - Prevents booking unavailable doctors.
   - Prevents duplicate bookings for the same doctor, date, and time.
5. **Dynamic Dashboard:** Real-time statistics showing Total, Pending, Approved, and Rejected bookings.
6. **Appointment Management:** View booking history and cancel pending appointments with confirmation popups.

### B. Administrator Features
1. **Custom Staff Dashboard:** High-level analytics (Total Doctors, Registered Patients, Total Appointments, Pending Reviews) and recent booking logs.
2. **Doctor Management (CRUD):**
   - **Create:** Add new doctors via form modal.
   - **Read:** Search and view all doctors.
   - **Update:** Toggle doctor availability status instantly.
   - **Delete:** Remove doctor profiles.
3. **Patient Directory:** View registered patient details and consultation histories (passwords remain encrypted and hidden).
4. **Appointment Control:** One-click Approve or Reject status updates for patient requests.
5. **Django Admin Integration:** Complete database access via `/admin/` with batch actions and filters.

---

## 5. Database Architecture

The application uses **Django's built-in User model** plus **TWO custom models**:

```
+-----------------------------------+         +----------------------------------+
|               User                |         |              Doctor              |
+-----------------------------------+         +----------------------------------+
| id (PK)                           |         | id (PK)                          |
| username                          |         | name                             |
| first_name, last_name             |         | department                       |
| email, password                   |         | email, phone                     |
| is_staff                          |         | consultation_fee                 |
+-----------------------------------+         | available (Boolean)              |
                  \                           +----------------------------------+
                   \                                      /
                    \                                    /
                     \       +--------------------+     /
                      +----> |    Appointment     | <--+
                             +--------------------+
                             | id (PK)            |
                             | patient (FK->User) |
                             | doctor (FK->Doctor)|
                             | appointment_date   |
                             | appointment_time   |
                             | status (Pending,   |
                             |  Approved, etc.)   |
                             | created_at         |
                             +--------------------+
```

---

## 6. Project Folder Structure

```
hsm/
│
├── manage.py                          # Django management script
├── db.sqlite3                         # SQLite database file
├── README.md                          # Project documentation
│
├── hospital/                          # Project configuration package
│   ├── __init__.py
│   ├── settings.py                    # Installed apps, templates, database settings
│   ├── urls.py                        # Root URL router
│   ├── wsgi.py
│   └── asgi.py
│
└── management/                        # Main hospital application
    ├── __init__.py
    ├── admin.py                       # Model registration & Django admin actions
    ├── apps.py
    ├── forms.py                       # UserRegistration, Appointment, & Doctor forms
    ├── models.py                      # Doctor & Appointment database models
    ├── views.py                       # Function-based views for patient & admin logic
    ├── urls.py                        # Application route definitions
    ├── tests.py                       # 19 automated unit & integration tests
    ├── migrations/                    # Database migration files
    │   └── 0001_initial.py
    │
    ├── management/commands/           # Custom management commands
    │   └── load_sample_data.py        # Populates 5 sample doctors & test patient
    │
    ├── templates/management/          # Django HTML templates
    │   ├── base.html                  # Shared layout, navbar, messages, footer
    │   ├── home.html                  # Public home page
    │   ├── login.html                 # Login page with password toggle
    │   ├── register.html              # Registration page with validation
    │   ├── doctors.html               # Doctor directory with live search/filter
    │   ├── dashboard.html             # Patient dashboard with dynamic counters
    │   ├── book_appointment.html      # Appointment booking form
    │   ├── my_appointments.html       # Patient appointments & cancellation
    │   ├── admin_dashboard.html       # Staff dashboard with analytics
    │   ├── admin_doctors.html         # Staff doctor management (CRUD)
    │   ├── admin_patients.html        # Staff patient directory
    │   └── admin_appointments.html    # Staff appointment approval/rejection
    │
    └── static/management/             # Static assets
        ├── css/
        │   └── style.css              # Custom hospital styling & Bootstrap themes
        └── js/
            └── script.js              # JavaScript for search, password toggle & alerts
```

---

## 7. How to Setup and Run the Project

### Prerequisites
- Python 3.10+ installed on your computer.

### Step 1: Open Terminal in the Project Directory
```powershell
cd c:\Users\samda\OneDrive\Pictures\Documents\Desktop\hsm
```

### Step 2: (Optional) Create & Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Django
```powershell
pip install django
```

### Step 4: Apply Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Load Sample Data
Loads 5 departmental doctors and a demo patient account:
```powershell
python manage.py load_sample_data
```

### Step 6: Create Admin Superuser (If needed)
A default superuser is already pre-configured:
- **Admin Username:** `admin`
- **Admin Password:** `admin123`

To create your own superuser:
```powershell
python manage.py createsuperuser
```

### Step 7: Start Development Server
```powershell
python manage.py runserver
```

Open your browser and navigate to:
- **Website Home:** `http://127.0.0.1:8000/`
- **Custom Admin Dashboard:** `http://127.0.0.1:8000/custom-admin/`
- **Django Admin Panel:** `http://127.0.0.1:8000/admin/`

---

## 8. Demo Credentials

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full access to Custom Admin & Django Admin |
| **Patient** | `patient1` | `patient123` | Pre-loaded patient with existing appointments |

---

## 9. Running Automated Tests
Run the test suite covering 19 unit & integration test cases:
```powershell
python manage.py test
```
All 19 tests test authentication, booking validation, duplicate slot prevention, patient isolation, cancellation, and admin operations.

