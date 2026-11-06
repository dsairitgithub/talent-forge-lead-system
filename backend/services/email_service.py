import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration from Environment Variables
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", MAIL_USERNAME or "notifications@alphaauron.com")
EXECUTIVE_EMAIL = os.getenv("EXECUTIVE_EMAIL", " bobbykutty2020@gmail.com")


def send_email(to_email, subject, body_html):
    """Low-level helper to send HTML email with fallback error logging."""
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print(f"[EMAIL SIMULATION] SMTP credentials not set. Simulated sending to {to_email} | Subject: '{subject}'")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Talent Forge Operations <{SENDER_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        
        print(f"[EMAIL SUCCESS] Dispatched to {to_email} with subject '{subject}'")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")
        return False


def send_executive_notification(lead):
    """Section 9: Mandatory Notification to santhan@alphaauron.com"""
    subject = f"New Talent Forge Membership Enquiry - {lead.get('lead_id')}"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
        <h2 style="color: #0f172a; border-bottom: 2px solid #f43f5e; padding-bottom: 8px;">New Talent Forge Membership Enquiry</h2>
        <p>A new prospective membership enquiry has been recorded in the funnel:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px; margin-top: 15px;">
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Lead ID</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('lead_id')}</td></tr>
          <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Full Name</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('full_name')}</td></tr>
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Email</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('email')}</td></tr>
          <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Mobile</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('mobile')}</td></tr>
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Category</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('category')}</td></tr>
          <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Primary Skills</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('primary_skills')}</td></tr>
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Experience Level</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('experience_level')}</td></tr>
          <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Current Status</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('current_status')}</td></tr>
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Target Tier / Duration</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('preferred_duration')}</td></tr>
          <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Additional Questions</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('questions') or 'None'}</td></tr>
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Assigned Employee</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('employee_name')} ({lead.get('employee_designation')})</td></tr>
          <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Submission Timestamp</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('submission_date')} at {lead.get('submission_time')}</td></tr>
          <tr style="background: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: bold;">Lead Source / Campaign</td><td style="padding: 8px; border: 1px solid #e2e8f0;">{lead.get('lead_source')} / {lead.get('campaign_source')}</td></tr>
        </table>
        <p style="margin-top: 20px;">
          <a href="{lead.get('base_url', '')}/admin" style="background: #f43f5e; color: #ffffff; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold;">Open Executive Admin Console</a>
        </p>
      </body>
    </html>
    """
    send_email(EXECUTIVE_EMAIL, subject, body)


def send_employee_notification(lead):
    """Section 10: Automatic Notification to Assigned Employee"""
    emp_email = lead.get("employee_email")
    if not emp_email:
        print("[EMAIL WARNING] No employee email found for notification dispatch.")
        return

    subject = f"New Lead Assigned: {lead.get('full_name')} [{lead.get('lead_id')}]"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b;">
        <h2 style="color: #0f172a;">Hello {lead.get('employee_name')},</h2>
        <p>A new prospective membership enquiry has been submitted through your funnel and assigned to you:</p>
        <ul>
          <li><b>Lead ID:</b> {lead.get('lead_id')}</li>
          <li><b>Candidate Name:</b> {lead.get('full_name')}</li>
          <li><b>Email:</b> {lead.get('email')}</li>
          <li><b>Mobile:</b> {lead.get('mobile')}</li>
          <li><b>Category:</b> {lead.get('category')}</li>
          <li><b>Target Track:</b> {lead.get('preferred_duration')}</li>
          <li><b>Submitted At:</b> {lead.get('submission_date')} {lead.get('submission_time')}</li>
        </ul>
        <p>Please review and initiate follow-up inside your dashboard:</p>
        <p>
          <a href="{lead.get('base_url', '')}/employee" style="background: #0284c7; color: #ffffff; padding: 9px 16px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Lead in Employee Dashboard</a>
        </p>
      </body>
    </html>
    """
    send_email(emp_email, subject, body)


def send_prospect_acknowledgement(lead):
    """Section 11: Acknowledgement to Candidate with Sales Page Link"""
    subject = "Thank You for Your Interest in Talent Forge!"
    sales_url = lead.get("sales_url") or f"{lead.get('base_url', '')}/sales"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0f172a; border-bottom: 2px solid #f43f5e; padding-bottom: 6px;">Welcome to Talent Forge</h2>
        <p>Hello <b>{lead.get('full_name')}</b>,</p>
        <p>Thank you for expressing your interest in Talent Forge, operated by <b>Alpha Auron Private Limited</b>.</p>
        <p>We have successfully received your membership enquiry.</p>
        <p>Our representative, <b>{lead.get('employee_name')}</b>, {lead.get('employee_designation')}, will review your enquiry and contact you regarding the next steps.</p>
        
        <div style="background: #f1f5f9; border-left: 4px solid #f43f5e; padding: 14px; margin: 20px 0; border-radius: 4px;">
          <p style="margin: 0; font-weight: bold; color: #0f172a;">Your Enquiry Reference ID: <span style="color: #f43f5e;">{lead.get('lead_id')}</span></p>
        </div>

        <p>In the meantime, you can explore detailed membership information, available tiers, durations, benefits, and enrolment details through the link below:</p>
        
        <p style="margin: 24px 0;">
          <a href="{sales_url}" style="background: #f43f5e; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Explore Talent Forge Membership Details</a>
        </p>

        <p style="font-size: 0.85rem; color: #64748b; margin-top: 30px;">
          * Note: Submitting an enquiry expresses interest and does not finalize enrolment. Terms and KYC conditions apply.
        </p>

        <p style="margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 15px;">
          Regards,<br>
          <b>Talent Forge Team</b><br>
          Alpha Auron Private Limited
        </p>
      </body>
    </html>
    """
    send_email(lead.get("email"), subject, body)


def trigger_all_notifications(lead_record):
    """
    Central dispatcher called asynchronously by app.py:
    1. Executive Notification (Section 9)
    2. Employee Notification (Section 10)
    3. Prospect Acknowledgement (Section 11)
    """
    send_executive_notification(lead_record)
    send_employee_notification(lead_record)
    send_prospect_acknowledgement(lead_record)