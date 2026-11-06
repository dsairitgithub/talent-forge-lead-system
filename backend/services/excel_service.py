import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

EXCEL_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Talent_Forge_Membership_Leads.xlsx")

HEADERS = [
    "Lead ID", "Full Name", "Email Address", "Mobile Number", "Professional Category",
    "Primary Skills", "Experience Level", "Current Status", "Preferred Membership Duration",
    "Additional Questions", "Assigned Employee", "Employee ID", "Employee Designation",
    "Funnel URL", "Lead Source", "Campaign Source", "Submission Date", "Submission Time",
    "Lead Status", "Follow-Up Notes", "Next Follow-Up Date", "Enrolment Status"
]

def ensure_workbook_initialized():
    os.makedirs(os.path.dirname(EXCEL_FILE_PATH), exist_ok=True)
    if not os.path.exists(EXCEL_FILE_PATH):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Membership Leads"
        ws.append(HEADERS)

        # Style headers with corporate navy
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        for col_num in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        wb.save(EXCEL_FILE_PATH)
        return wb
    return openpyxl.load_workbook(EXCEL_FILE_PATH)

def append_lead_to_excel(lead):
    wb = ensure_workbook_initialized()
    ws = wb["Membership Leads"] if "Membership Leads" in wb.sheetnames else wb.active

    target_id = str(lead.get("lead_id", "")).strip()
    target_email = str(lead.get("email", "")).strip().lower()
    target_mobile = str(lead.get("mobile", "")).strip()

    row_data = [
        lead.get("lead_id"), lead.get("full_name"), lead.get("email"), lead.get("mobile"),
        lead.get("category"), lead.get("primary_skills"), lead.get("experience_level"),
        lead.get("current_status"), lead.get("preferred_duration"), lead.get("questions"),
        lead.get("employee_name"), lead.get("employee_id"), lead.get("employee_designation"),
        lead.get("funnel_url"), lead.get("lead_source"), lead.get("campaign_source"),
        lead.get("submission_date"), lead.get("submission_time"), lead.get("lead_status", "New Enquiry"),
        lead.get("follow_up_notes", ""), lead.get("next_follow_up_date", ""), lead.get("enrolment_status", "Pending")
    ]

    # Deduplication check: verify if lead ID, email, or mobile is already in Excel
    row_to_update = None
    for row in range(2, ws.max_row + 1):
        cell_id = str(ws.cell(row=row, column=1).value or "").strip()
        cell_email = str(ws.cell(row=row, column=3).value or "").strip().lower()
        cell_mobile = str(ws.cell(row=row, column=4).value or "").strip()

        if cell_id == target_id or (target_email and cell_email == target_email) or (target_mobile and cell_mobile == target_mobile):
            row_to_update = row
            break

    if row_to_update:
        for col_idx, val in enumerate(row_data, start=1):
            ws.cell(row=row_to_update, column=col_idx, value=val)
    else:
        ws.append(row_data)

    wb.save(EXCEL_FILE_PATH)

def sync_lead_update_to_excel(lead):
    """Updates an existing row in Excel when status or notes change."""
    wb = ensure_workbook_initialized()
    ws = wb["Membership Leads"] if "Membership Leads" in wb.sheetnames else wb.active

    target_lead_id = str(lead.get("lead_id", "")).strip()
    for row in range(2, ws.max_row + 1):
        if str(ws.cell(row=row, column=1).value or "").strip() == target_lead_id:
            ws.cell(row=row, column=19, value=lead.get("lead_status"))
            ws.cell(row=row, column=20, value=lead.get("follow_up_notes"))
            ws.cell(row=row, column=21, value=lead.get("next_follow_up_date"))
            ws.cell(row=row, column=22, value=lead.get("enrolment_status"))
            wb.save(EXCEL_FILE_PATH)
            return True
    return False