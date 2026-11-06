# Talent Forge Membership Lead Generation Funnel

Production-grade, employee-specific lead acquisition, automated tracking, and membership sales funnel engineered for **Alpha Auron Private Limited**.

## 1. Executive Summary & Attribution

* **Client Organization:** Alpha Auron Private Limited

* **Project Scope:** Talent Forge Membership Lead Generation Funnel

* **Dedicated Associate:** Munendra Naick (`TF-EMP-MN01`)

* **Associate Title:** Talent Forge Associate

* **Department:** Talent Forge Operations

* **System Status:** 🟢 100% Verified & Deployment Ready (22/22 Tests Passed)

* **Core Technology Stack:**

  * **Backend:** Python 3.10+, Flask, SQLite3, OpenPyXL, Jinja2, Werkzeug

  * **Frontend:** Vanilla HTML5, CSS3 Custom Properties (Neon Pink/Obsidian Palette), ES6+ JavaScript

  * **Integrations:** Multi-channel Email Dispatch (SMTP), Asynchronous Background Workers, Real-Time Excel Synchronization

## 2. Business Model & Funnel Architecture

### 2.1 The Talent Forge Funnel Journey

The system implements a strictly controlled two-page lead acquisition journey:

```
Prospective Candidate
       │
       ▼
[ Page 1: Lead Gen Landing Page (/) ]
  ├── 14 Professional Discipline Tracks
  ├── 8-Step Membership Roadmap
  ├── Dynamic 6 vs 12-Month Membership Plan Switcher
  ├── Configurable Representative Contact Card (Munendra Naick)
  └── Protected Enquiry Form (Honeypot + Deduplication)
       │
       ▼ (Form Submission - HTTP 201)
  ├── 1. SQLite Database Primary Commit (TF-xxxx sequential ID)
  ├── 2. Background Thread Launch:
  │      ├── Auto-append to Talent_Forge_Membership_Leads.xlsx (20 columns)
  │      ├── Executive Notification (santhan@alphaauron.com)
  │      ├── Associate Notification (munikumar@alphaauron.com)
  │      └── Acknowledgement Email with Link to Page 2
  └── 3. Statutory In-Page Confirmation (No auto-redirect)
       │
       ▼
[ Page 2: Membership Sales Page (/sales) ]
  ├── Detailed 5-Tier Comparison Matrix
  ├── Scope & Allocation Criteria
  ├── Standalone Membership Terms & Conditions (01–05)
  └── Official Enrollment Call-to-Action (https://alphaauron.com/talent-forge)

```

### 2.2 Statutory Compliance & No-Salary Disclaimers

In compliance with Alpha Auron business terms:

* Membership fees grant verified network onboarding, capability evaluation, and project eligibility.

* The funnel explicitly disclaims fixed monthly incomes, permanent salaries, or automatic project allocations.

* Project compensation is strictly deliverable-based, disbursed upon successful milestone review, QA testing, and client approval.

## 3. Directory Layout

```
TalentForge/
│
├── backend/
│   ├── app.py                            # Flask application core, auth & API endpoints
│   ├── database.py                       # SQLite connection, schema migrations & models
│   ├── services/
│   │   ├── email_service.py              # Tri-partite notification & SMTP handler
│   │   └── excel_service.py              # 20-column OpenPyXL synchronization service
│   ├── run_compliance_tests.py           # 22-point automated compliance verification suite
│   ├── TESTING_REPORT.md                 # Formal verification documentation (100% Pass)
│   ├── Talent_Forge_Membership_Leads.xlsx # Master lead workbook (auto-synced)
│   ├── requirements.txt                  # Frozen dependency manifest
│   └── .env.example                      # Production environment configuration template
│
├── frontend/
│   ├── index.html                        # Page 1: Lead Generation Landing Page
│   ├── sales.html                        # Page 2: Membership Sales Landing Page
│   ├── admin.html                        # Executive Intelligence Console
│   ├── employee.html                     # Munendra Naick Associate Workspace
│   ├── login.html                        # Secure Corporate Operations Gate
│   ├── css/
│   │   ├── styles.css                    # Design tokens, gradients, layouts & media queries
│   │   └── admin.css                     # Workspace table, modals & telemetry styling
│   └── js/
│       ├── main.js                       # UI interactions, phone dialer & telemetry tracking
│       └── admin.js                      # Lead table renderer, search/filter & edit modals
│
└── README.md                             # Comprehensive technical documentation

```

## 4. Local Setup & Quickstart

### Prerequisites

* Python 3.10 or higher

* `pip` package manager

* Modern web browser (Chrome, Edge, Firefox, Safari)

### Step-by-Step Installation

1. **Open your terminal and navigate to the backend:**

   ```
   cd TalentForge/backend
   
   ```

2. **Activate your Python virtual environment:**

   * **Windows:**

     ```
     .\venv\Scripts\activate
     
     ```

   * **macOS / Linux:**

     ```
     source venv/bin/activate
     
     ```

3. **Install dependencies:**

   ```
   pip install -r requirements.txt
   
   ```

4. **Configure your Environment (`.env`):**
   Copy `.env.example` to `.env` inside `backend/`:

   ```
   SECRET_KEY=alpha_auron_talentforge_key_2026
   BASE_URL=http://127.0.0.1:5000
   SESSION_COOKIE_SECURE=False
   
   # SMTP Dispatch Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_verified_account@alphaauron.com
   SMTP_PASS=your_app_specific_password
   
   # Target Notification Mailboxes
   EXECUTIVE_EMAIL=santhan@alphaauron.com
   EMPLOYEE_EMAIL=munikumar@alphaauron.com
   
   ```

5. **Start the server:**

   ```
   python app.py
   
   ```

   The application will boot at `http://127.0.0.1:5000/`.

## 5. Endpoints & API Reference

| Endpoint | Method | Access | Description | 
| ----- | ----- | ----- | ----- | 
| `/` | `GET` | Public | Page 1: Associate Lead Gen Landing Page | 
| `/sales` | `GET` | Public | Page 2: Membership Sales Landing Page | 
| `/login` | `GET` | Public | Secure Corporate Access Gateway | 
| `/admin` | `GET` | Admin Role | Executive Intelligence & Telemetry Dashboard | 
| `/employee` | `GET` | Employee Role | Munendra Naick Workspace (`TF-EMP-MN01`) | 
| `/api/submit-lead` | `POST` | Public | Submits lead, triggers DB write, Excel sync & emails | 
| `/api/track` | `POST` | Public | Ingests telemetry metrics (views, clicks, drops) | 
| `/api/config/public` | `GET` | Public | Exposes active associate dynamic details | 
| `/api/admin/leads` | `GET` | Authenticated | Retrieves lead pipeline (scoped by user role) | 
| `/api/admin/lead/<id>` | `PATCH` / `PUT` | Authenticated | Updates pipeline status, notes, or candidate profile | 
| `/api/admin/lead/<id>` | `DELETE` | Admin Role | Permanently removes lead record | 
| `/api/admin/download-excel` | `GET` | Authenticated | Securely downloads `Talent_Forge_Membership_Leads.xlsx` | 

## 6. Automated Testing & Compliance Verification

The project includes an automated test harness (`run_compliance_tests.py`) validating the entire funnel against the 17 sections of `TASK-ASSIGNMENT.pdf`.

### Running the Test Suite

```
python run_compliance_tests.py

```

### Verification Highlights (22/22 Tests Passing)

* **Frontend Verifications:** Page 1 (`/`) and Page 2 (`/sales`) HTTP 200, exact hero headlines, all 14 disciplines, 8-step roadmap, 5-tier plan matrix, and terms section.

* **Form & Security:** Server-side validation (HTTP 400), honeypot trap (`website_hp_check`), duplicate submission block (HTTP 409), sequential reference ID (`TF-xxxx`).

* **Database & Attribution:** Reliable SQLite persistence before asynchronous worker dispatch; immutable server-side binding to Munendra Naick (`TF-EMP-MN01`).

* **Excel Ledger:** Master workbook (`Talent_Forge_Membership_Leads.xlsx`) with 20 ordered columns auto-appended in real time.

* **Access Control:** Unauthenticated calls to `/api/admin/leads` and `/api/admin/download-excel` blocked with HTTP 401.

*Full audit records are documented in `TESTING_REPORT.md`.*

## 7. Security & Telemetry Features

1. **Honeypot Anti-Spam Protection:** Silent input field detects and traps malicious form bots without requiring invasive CAPTCHAs.

2. **Session Hardening:** HTTP-only cryptographically signed session cookies with role-based access control (Admin vs. Associate).

3. **Telemetry & Funnel Drop-off Tracking:** Real-time tracking of:

   * Unique IP visitors

   * Pricing section views (`IntersectionObserver`)

   * Plan CTA click conversions

   * Form abandonment rates

   * UTM campaign & referrer channel attribution

## 8. Production Deployment Guide

When moving to a public production server (Ubuntu/Linux):

1. **Update `.env`:**

   ```
   BASE_URL=https://alphaauron.com/talent-forge
   SESSION_COOKIE_SECURE=True
   
   ```

2. **Run with Production WSGI Server (Gunicorn):**

   ```
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   
   ```

3. **Nginx Reverse Proxy Configuration:**
   Forward standard HTTPS port 443 traffic to the local Gunicorn socket (`127.0.0.1:5000`) with appropriate SSL headers.

*Alpha Auron Private Limited · Talent Forge Engineering Operations*