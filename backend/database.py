import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "talent_forge.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Central Leads Table (Section 6 & 7)
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            category TEXT NOT NULL,
            primary_skills TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            current_status TEXT NOT NULL,
            preferred_duration TEXT,
            questions TEXT,
            employee_name TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            employee_designation TEXT NOT NULL,
            funnel_url TEXT,
            lead_source TEXT,
            campaign_source TEXT,
            submission_date TEXT NOT NULL,
            submission_time TEXT NOT NULL,
            lead_status TEXT DEFAULT 'New Enquiry',
            follow_up_notes TEXT,
            next_follow_up_date TEXT,
            enrolment_status TEXT DEFAULT 'Pending'
        )
    """)

    # 2. Analytics Tracking Table (Section 14)
    c.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            traffic_source TEXT,
            campaign TEXT,
            visitor_ip TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # 3. Users Table for Role-Based Authentication
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'employee')),
            employee_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Auto-seed default accounts with hashed credentials if table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        admin_hash = generate_password_hash("Admin@Alpha2026")
        emp_hash = generate_password_hash("Associate@TF2026")

        c.execute("""
            INSERT INTO users (username, password_hash, full_name, role, employee_id)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", admin_hash, "Operations Executive", "admin", None))

        c.execute("""
            INSERT INTO users (username, password_hash, full_name, role, employee_id)
            VALUES (?, ?, ?, ?, ?)
        """, ("TF-EMP-MN01", emp_hash, "Munendra Naick", "employee", "TF-EMP-MN01"))

        print("[DATABASE] Successfully created and seeded 'users' table.")

    # 5. Auto-migration check: ensure funnel_url exists on existing database files
    c.execute("PRAGMA table_info(leads)")
    columns = [row["name"] for row in c.fetchall()]
    if "funnel_url" not in columns:
        c.execute("ALTER TABLE leads ADD COLUMN funnel_url TEXT")
        print("[DATABASE MIGRATION] Added missing funnel_url column to leads table.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()