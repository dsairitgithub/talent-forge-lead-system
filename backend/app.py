import os
import threading
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, send_file, session, redirect
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from database import init_db, get_db_connection

from services.excel_service import append_lead_to_excel, sync_lead_update_to_excel, EXCEL_FILE_PATH
from services.email_service import trigger_all_notifications

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "alpha-auron-secret-key-prod-2026")
CORS(app, supports_credentials=True)

# Cookie Security & Session Settings
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Set to True on HTTPS in production
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12)
)

# Central dynamic settings store (falls back to env vars)
SETTINGS_DEFAULTS = {
    "employee_name": os.getenv("EMPLOYEE_NAME", "Munendra Naick"),
    "employee_id": os.getenv("EMPLOYEE_ID", "TF-EMP-MN01"),
    "employee_designation": os.getenv("EMPLOYEE_DESIGNATION", "Talent Forge Associate"),
    "employee_email": os.getenv("EMPLOYEE_EMAIL", "munikumar@alphaauron.com"),
    "employee_phone": os.getenv("EMPLOYEE_PHONE", "+918142559110"),
    "employee_whatsapp": os.getenv("EMPLOYEE_WHATSAPP", "918142559110"),
    "executive_email": os.getenv("EXECUTIVE_EMAIL", "santhan@alphaauron.com"),
}

# --- AUTHENTICATION & RBAC DECORATOR ---
def require_auth(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get("user")
            if not user:
                return jsonify({"status": "error", "message": "Unauthorized: Please sign in"}), 401

            if allowed_roles and user.get("role") not in allowed_roles:
                return jsonify({"status": "error", "message": "Forbidden: Insufficient privileges"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- AUTHENTICATION API ROUTES ---
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required."}), 400

    conn = get_db_connection()
    c = conn.cursor()
    user_row = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user_row and check_password_hash(user_row["password_hash"], password):
        session.clear()
        session.permanent = True
        session["user"] = {
            "id": user_row["id"],
            "username": user_row["username"],
            "full_name": user_row["full_name"],
            "role": user_row["role"],
            "employee_id": user_row["employee_id"]
        }
        return jsonify({"status": "success", "user": session["user"]})

    return jsonify({"status": "error", "message": "Invalid corporate credentials."}), 401

@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    user = session.get("user")
    if not user:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "user": user})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "success"})

# --- STATIC PAGE ROUTES WITH SERVER-SIDE GUARDS ---
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/sales")
def sales_page():
    return send_from_directory(app.static_folder, "sales.html")

@app.route("/login")
def login_page():
    user = session.get("user")
    if user:
        if user.get("role") == "admin":
            return redirect("/admin")
        return redirect("/employee")
    return send_from_directory(app.static_folder, "login.html")

@app.route("/admin")
def admin_page():
    user = session.get("user")
    if not user:
        return redirect("/login")
    if user.get("role") != "admin":
        return redirect("/employee")
    return send_from_directory(app.static_folder, "admin.html")

@app.route("/employee")
def employee_page():
    user = session.get("user")
    if not user:
        return redirect("/login")
    return send_from_directory(app.static_folder, "employee.html")

# --- CONFIGURABLE SETTINGS ---
@app.route("/api/config/public", methods=["GET"])
def get_public_config():
    return jsonify({
        "employee_name": SETTINGS_DEFAULTS["employee_name"],
        "employee_id": SETTINGS_DEFAULTS["employee_id"],
        "employee_designation": SETTINGS_DEFAULTS["employee_designation"],
        "employee_email": SETTINGS_DEFAULTS["employee_email"],
        "employee_phone": SETTINGS_DEFAULTS["employee_phone"],
        "employee_whatsapp": SETTINGS_DEFAULTS["employee_whatsapp"]
    })

@app.route("/api/admin/config", methods=["GET", "POST"])
@require_auth(allowed_roles=["admin"])
def manage_config():
    if request.method == "POST":
        data = request.json or {}
        for key in SETTINGS_DEFAULTS.keys():
            if key in data and data[key]:
                SETTINGS_DEFAULTS[key] = data[key]
        return jsonify({"status": "success", "config": SETTINGS_DEFAULTS})
    return jsonify({"config": SETTINGS_DEFAULTS})

# --- ADVANCED ANALYTICS ---
@app.route("/api/track", methods=["POST"])
def track_event():
    data = request.json or {}
    event_name = data.get("event")
    traffic_source = request.headers.get("Referer", "Direct")
    campaign = data.get("utm_campaign", "Direct")
    visitor_ip = request.remote_addr or "anonymous"

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO analytics_events (event_name, traffic_source, campaign, visitor_ip, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (event_name, traffic_source, campaign, visitor_ip, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/api/analytics", methods=["GET"])
@require_auth(allowed_roles=["admin", "employee"])
def get_analytics():
    conn = get_db_connection()
    c = conn.cursor()

    total_leads = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    verified_leads = c.execute("SELECT COUNT(*) FROM leads WHERE lead_status = 'Verified'").fetchone()[0]

    total_views = c.execute("SELECT COUNT(*) FROM analytics_events WHERE event_name = 'page_view'").fetchone()[0]
    unique_visitors = c.execute("SELECT COUNT(DISTINCT visitor_ip) FROM analytics_events").fetchone()[0]
    plan_views = c.execute("SELECT COUNT(*) FROM analytics_events WHERE event_name = 'plan_section_view'").fetchone()[0]
    plan_clicks = c.execute("SELECT COUNT(*) FROM analytics_events WHERE event_name = 'plan_clicks'").fetchone()[0]
    form_starts = c.execute("SELECT COUNT(*) FROM analytics_events WHERE event_name = 'form_starts'").fetchone()[0]
    form_abandons = max(0, form_starts - total_leads)

    views = max(total_views, 1)
    conversion_rate = round((total_leads / views) * 100, 2)

    traffic_sources = [dict(r) for r in c.execute("SELECT traffic_source, COUNT(*) as count FROM analytics_events GROUP BY traffic_source ORDER BY count DESC LIMIT 5").fetchall()]
    campaigns = [dict(r) for r in c.execute("SELECT campaign, COUNT(*) as count FROM analytics_events GROUP BY campaign ORDER BY count DESC LIMIT 5").fetchall()]
    conn.close()

    return jsonify({
        "total_visitors": total_views,
        "unique_visitors": unique_visitors,
        "plan_section_views": plan_views,
        "plan_clicks": plan_clicks,
        "form_starts": form_starts,
        "form_abandonment": form_abandons,
        "total_leads": total_leads,
        "verified_leads": verified_leads,
        "conversion_rate": f"{conversion_rate}%",
        "traffic_sources": traffic_sources,
        "campaigns": campaigns
    })

# --- ASYNC BACKGROUND WORKFLOW DISPATCHER ---
def async_storage_and_notifications(lead_record):
    try:
        append_lead_to_excel(lead_record)
    except Exception as e:
        print(f"[WORKFLOW ERROR] Excel append failed for {lead_record['lead_id']}: {e}")

    try:
        trigger_all_notifications(lead_record)
    except Exception as e:
        print(f"[WORKFLOW ERROR] Notification dispatch failed for {lead_record['lead_id']}: {e}")

# --- LEAD SUBMISSION (SEQUENTIAL ID & STRICT DEDUPLICATION) ---
@app.route("/api/submit-lead", methods=["POST"])
def submit_lead():
    data = request.json or {}

    # Anti-bot honeypot check
    if data.get("website_hp_check"):
        return jsonify({"status": "error", "message": "Bot submission detected"}), 400

    required = ["full_name", "email", "mobile", "category", "primary_skills", "experience_level", "current_status"]
    for field in required:
        if not data.get(field):
            return jsonify({"status": "error", "message": f"{field.replace('_', ' ').capitalize()} is required."}), 400

    email = data.get("email").strip().lower()
    mobile = data.get("mobile").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Deduplication Guard: Disallow duplicate email or mobile submissions
    existing_lead = cursor.execute(
        "SELECT lead_id FROM leads WHERE LOWER(email) = ? OR mobile = ?",
        (email, mobile)
    ).fetchone()

    if existing_lead:
        conn.close()
        return jsonify({
            "status": "error",
            "message": f"An enquiry with this email or mobile number already exists (Ref ID: {existing_lead['lead_id']})."
        }), 409

    # 2. Sequential Reference ID generation starting from 1 (TF-0001, TF-0002, ...)
    last_lead = cursor.execute("SELECT MAX(id) FROM leads").fetchone()
    next_num = 1 if not last_lead or last_lead[0] is None else (last_lead[0] + 1)
    lead_id = f"TF-{str(next_num).zfill(4)}"

    now = datetime.now()
    detected_base = request.host_url.rstrip("/")
    base_url = os.getenv("BASE_URL", detected_base).rstrip("/")
    sales_url = f"{base_url}/sales"

    lead_record = {
        "lead_id": lead_id,
        "full_name": data.get("full_name").strip(),
        "email": email,
        "mobile": mobile,
        "category": data.get("category"),
        "primary_skills": data.get("primary_skills").strip(),
        "experience_level": data.get("experience_level"),
        "current_status": data.get("current_status"),
        "preferred_duration": data.get("preferred_duration", "Not Specified"),
        "questions": data.get("questions", "").strip(),
        "employee_name": SETTINGS_DEFAULTS["employee_name"],
        "employee_id": SETTINGS_DEFAULTS["employee_id"],
        "employee_designation": SETTINGS_DEFAULTS["employee_designation"],
        "employee_email": SETTINGS_DEFAULTS["employee_email"],
        "funnel_url": data.get("funnel_url", request.headers.get("Referer", request.host_url)),
        "base_url": base_url,
        "sales_url": sales_url,
        "lead_source": data.get("lead_source", "Employee Landing Page"),
        "campaign_source": data.get("campaign_source", "Direct"),
        "submission_date": now.strftime("%Y-%m-%d"),
        "submission_time": now.strftime("%H:%M:%S"),
        "lead_status": "New Enquiry",
        "follow_up_notes": "",
        "next_follow_up_date": "",
        "enrolment_status": "Pending"
    }

    # 3. Database persistence
    cursor.execute("""
        INSERT INTO leads (
            lead_id, full_name, email, mobile, category, primary_skills,
            experience_level, current_status, preferred_duration, questions,
            employee_name, employee_id, employee_designation, funnel_url, lead_source,
            campaign_source, submission_date, submission_time, lead_status,
            follow_up_notes, next_follow_up_date, enrolment_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_record["lead_id"], lead_record["full_name"], lead_record["email"],
        lead_record["mobile"], lead_record["category"], lead_record["primary_skills"],
        lead_record["experience_level"], lead_record["current_status"],
        lead_record["preferred_duration"], lead_record["questions"],
        lead_record["employee_name"], lead_record["employee_id"],
        lead_record["employee_designation"], lead_record["funnel_url"],
        lead_record["lead_source"], lead_record["campaign_source"],
        lead_record["submission_date"], lead_record["submission_time"],
        lead_record["lead_status"], lead_record["follow_up_notes"],
        lead_record["next_follow_up_date"], lead_record["enrolment_status"]
    ))
    conn.commit()
    conn.close()

    # 4. Asynchronous worker thread for Excel append and Email triggers
    threading.Thread(target=async_storage_and_notifications, args=(lead_record,), daemon=True).start()

    return jsonify({
        "status": "success",
        "message": "Enquiry submitted successfully. Submitting an enquiry does not mean membership enrolment is complete.",
        "lead_id": lead_id
    }), 201

# --- SINGLE CLEAN DECLARATION FOR GET LEADS ---
@app.route("/api/admin/leads", methods=["GET"])
@require_auth(allowed_roles=["admin", "employee"])
def get_all_leads():
    current_user = session.get("user")
    conn = get_db_connection()

    if current_user and current_user.get("role") == "employee":
        rows = conn.cursor().execute("SELECT * FROM leads WHERE employee_id = ? ORDER BY id DESC", (current_user["employee_id"],)).fetchall()
    else:
        emp_filter = request.args.get("employee_id")
        if emp_filter:
            rows = conn.cursor().execute("SELECT * FROM leads WHERE employee_id = ? ORDER BY id DESC", (emp_filter,)).fetchall()
        else:
            rows = conn.cursor().execute("SELECT * FROM leads ORDER BY id DESC").fetchall()

    conn.close()
    return jsonify({"leads": [dict(r) for r in rows]})

@app.route("/api/admin/lead/<lead_id>", methods=["GET"])
@require_auth(allowed_roles=["admin", "employee"])
def get_single_lead(lead_id):
    conn = get_db_connection()
    row = conn.cursor().execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"status": "error", "message": "Lead not found"}), 404
    return jsonify({"lead": dict(row)})

@app.route("/api/admin/lead/<lead_id>", methods=["PATCH"])
@require_auth(allowed_roles=["admin", "employee"])
def update_lead_notes(lead_id):
    data = request.json or {}
    conn = get_db_connection()
    c = conn.cursor()

    existing = c.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"status": "error", "message": "Lead not found"}), 404

    c.execute("""
        UPDATE leads
        SET lead_status = COALESCE(?, lead_status),
            follow_up_notes = COALESCE(?, follow_up_notes),
            next_follow_up_date = COALESCE(?, next_follow_up_date),
            enrolment_status = COALESCE(?, enrolment_status),
            employee_id = COALESCE(?, employee_id)
        WHERE lead_id = ?
    """, (
        data.get("lead_status"),
        data.get("follow_up_notes"),
        data.get("next_follow_up_date"),
        data.get("enrolment_status"),
        data.get("employee_id"),
        lead_id
    ))
    conn.commit()

    updated = dict(c.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,)).fetchone())
    conn.close()

    threading.Thread(target=sync_lead_update_to_excel, args=(updated,), daemon=True).start()

    return jsonify({"status": "success", "lead": updated})

@app.route("/api/admin/lead/<lead_id>", methods=["PUT"])
@require_auth(allowed_roles=["admin"])
def edit_full_lead(lead_id):
    data = request.json or {}
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE leads
        SET full_name = ?, email = ?, mobile = ?, category = ?, primary_skills = ?,
            experience_level = ?, current_status = ?, preferred_duration = ?, questions = ?
        WHERE lead_id = ?
    """, (
        data.get("full_name"), data.get("email"), data.get("mobile"), data.get("category"),
        data.get("primary_skills"), data.get("experience_level"), data.get("current_status"),
        data.get("preferred_duration"), data.get("questions"), lead_id
    ))
    conn.commit()
    updated = dict(c.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,)).fetchone())
    conn.close()

    threading.Thread(target=sync_lead_update_to_excel, args=(updated,), daemon=True).start()
    return jsonify({"status": "success", "lead": updated})

@app.route("/api/admin/lead/<lead_id>", methods=["DELETE"])
@require_auth(allowed_roles=["admin"])
def delete_lead(lead_id):
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM leads WHERE lead_id = ?", (lead_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/api/admin/download-excel", methods=["GET"])
@require_auth(allowed_roles=["admin", "employee"])
def download_excel():
    if os.path.exists(EXCEL_FILE_PATH):
        return send_file(EXCEL_FILE_PATH, as_attachment=True, download_name="Talent_Forge_Membership_Leads.xlsx")
    return jsonify({"status": "error", "message": "Excel file not found"}), 404

init_db()
if __name__ == "__main__":
    app.run(port=5000, debug=True)