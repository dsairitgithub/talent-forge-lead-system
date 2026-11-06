let allLeads = [];

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function fetchLeads() {
  try {
    const res = await fetch("/api/admin/leads", { credentials: "include" });
    if (res.status === 401) {
      window.location.href = "/login";
      return;
    }
    if (!res.ok) {
      const tbody = document.getElementById("leadsTableBody");
      if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color: #f43f5e;">Failed to load leads (HTTP ${res.status}).</td></tr>`;
      return;
    }
    const data = await res.json();
    allLeads = data.leads || [];
    renderDashboard();
  } catch (err) {
    const tbody = document.getElementById("leadsTableBody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color: #f43f5e;">Network error connecting to backend API.</td></tr>`;
  }
}

function renderDashboard() {
  renderMetrics();
  filterAndRenderTable();
}

function setSafeText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

function renderMetrics() {
  const total = allLeads.length;
  const newCount = allLeads.filter(l => l.lead_status === "New Enquiry").length;
  const contacted = allLeads.filter(l => l.lead_status === "Contacted").length;
  const followUpsPending = allLeads.filter(l => l.next_follow_up_date && String(l.next_follow_up_date).trim() !== "").length;
  const inProgress = allLeads.filter(l => l.lead_status === "Enrolment in Progress").length;
  const verified = allLeads.filter(l => l.lead_status === "Verified").length;
  const conversionRate = total > 0 ? ((verified / total) * 100).toFixed(1) + "%" : "0%";

  setSafeText("mTotal", total);
  setSafeText("mNew", newCount);
  setSafeText("mContacted", contacted);
  setSafeText("mFollowUpPending", followUpsPending);
  setSafeText("mInProgress", inProgress);
  setSafeText("mVerified", verified);
  setSafeText("mConversion", conversionRate);
}

function filterAndRenderTable() {
  const searchEl = document.getElementById("searchInput");
  const query = searchEl ? searchEl.value.toLowerCase().trim() : "";
  const statusEl = document.getElementById("statusFilter");
  const status = statusEl ? statusEl.value : "ALL";
  const dateEl = document.getElementById("dateFilter");
  const dateFilter = dateEl ? dateEl.value : "";
  const tbody = document.getElementById("leadsTableBody");

  if (!tbody) return;

  const filtered = allLeads.filter(l => {
    const matchQuery = (l.full_name || "").toLowerCase().includes(query) ||
                       (l.email || "").toLowerCase().includes(query) ||
                       (l.mobile || "").includes(query) ||
                       (l.lead_id || "").toLowerCase().includes(query);
    const matchStatus = (status === "ALL" || l.lead_status === status);
    const matchDate = (!dateFilter || l.submission_date === dateFilter);
    return matchQuery && matchStatus && matchDate;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 40px; color: #9f758f;">No matching enquiries found.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(l => `
    <tr>
      <td>
        <span class="lead-id-badge">${escapeHtml(l.lead_id)}</span>
        <span class="lead-time">${escapeHtml(l.submission_date)} ${escapeHtml(l.submission_time)}</span>
      </td>
      <td>
        <div class="candidate-name">${escapeHtml(l.full_name)}</div>
        <div class="candidate-contact">${escapeHtml(l.email)}<br>${escapeHtml(l.mobile)}</div>
      </td>
      <td>
        <div class="category-tag">${escapeHtml(l.category)}</div>
        <span class="skills-pill">${escapeHtml(l.primary_skills)}</span>
        <small style="color:#fb7185; display:block; font-weight:600; font-size:0.78rem;">${escapeHtml(l.preferred_duration || 'Standard Plan')}</small>
        <small style="color:#9f758f;">${escapeHtml(l.experience_level)} &bull; ${escapeHtml(l.current_status)}</small>
      </td>
      <td>
        <select class="status-dropdown" onchange="updateStatus('${escapeHtml(l.lead_id)}', this.value)">
          ${[
            "New Enquiry", "Contacted", "Interested", "Official Website Shared",
            "Follow-Up Required", "Enrolment in Progress", "Enrolled", "Verified", "Not Interested", "Closed"
          ].map(opt => `<option value="${opt}" ${l.lead_status === opt ? "selected" : ""}>${opt}</option>`).join("")}
        </select>
      </td>
      <td>
        <input type="text" class="notes-input" id="notes-${escapeHtml(l.lead_id)}" value="${escapeHtml(l.follow_up_notes || '')}" placeholder="Add follow-up notes...">
        <input type="date" class="date-input" id="date-${escapeHtml(l.lead_id)}" value="${escapeHtml(l.next_follow_up_date || '')}">
      </td>
      <td>
        <div class="action-cluster">
          <button class="btn-ctrl btn-ctrl-save" title="Save notes and date" onclick="saveNotes('${escapeHtml(l.lead_id)}')">Save</button>
          <button class="btn-ctrl btn-ctrl-view" title="Edit full dossier" onclick="openEditModal('${escapeHtml(l.lead_id)}')">Edit</button>
          <button class="btn-ctrl btn-ctrl-view" title="View full dossier" onclick="openViewModal('${escapeHtml(l.lead_id)}')">View</button>
          <button class="btn-ctrl btn-ctrl-del" title="Delete lead" onclick="deleteLead('${escapeHtml(l.lead_id)}')">Delete</button>
        </div>
      </td>
    </tr>
  `).join("");
}

async function saveNotes(leadId) {
  const notesEl = document.getElementById(`notes-${leadId}`);
  const dateEl = document.getElementById(`date-${leadId}`);
  const notes = notesEl ? notesEl.value : "";
  const nextDate = dateEl ? dateEl.value : "";

  try {
    const res = await fetch(`/api/admin/lead/${leadId}`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ follow_up_notes: notes, next_follow_up_date: nextDate })
    });
    if (res.status === 401) { window.location.href = "/login"; return; }
    if (res.ok) {
      await fetchLeads();
    } else {
      alert("Failed to save notes.");
    }
  } catch (err) {
    alert("Connection error while saving.");
  }
}

async function updateStatus(leadId, newStatus) {
  try {
    const res = await fetch(`/api/admin/lead/${leadId}`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lead_status: newStatus })
    });
    if (res.status === 401) { window.location.href = "/login"; return; }
    if (res.ok) {
      await fetchLeads();
    } else {
      alert("Failed to update status.");
    }
  } catch (err) {
    console.error("Error updating status:", err);
  }
}

async function deleteLead(leadId) {
  if (!confirm(`Permanently delete lead ${leadId}? This action cannot be undone.`)) return;
  try {
    const res = await fetch(`/api/admin/lead/${leadId}`, {
      method: "DELETE",
      credentials: "include"
    });
    if (res.status === 401) { window.location.href = "/login"; return; }
    if (res.ok) {
      await fetchLeads();
    } else {
      alert("Failed to delete lead.");
    }
  } catch (err) {
    console.error("Error deleting lead:", err);
  }
}

function openViewModal(leadId) {
  const lead = allLeads.find(l => l.lead_id === leadId);
  if (!lead) return;

  const content = document.getElementById("viewContent");
  if (!content) return;

  content.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 14px;">
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Lead Reference ID</span>
        <span style="font-family: monospace; font-weight: 800; color: #ff007f; font-size: 15px;">${escapeHtml(lead.lead_id)}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Pipeline Stage</span>
        <span style="font-weight: 800; color: #059669; font-size: 14px;">${escapeHtml(lead.lead_status)}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Candidate Name</span>
        <span style="font-weight: 700; color: #0f172a; font-size: 14px;">${escapeHtml(lead.full_name)}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Mobile</span>
        <span style="font-weight: 600; color: #0f172a;">${escapeHtml(lead.mobile)}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Email</span>
        <span style="font-weight: 600; color: #0f172a; word-break: break-all;">${escapeHtml(lead.email)}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Track Discipline</span>
        <span style="font-weight: 600; color: #0f172a;">${escapeHtml(lead.category)}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; grid-column: span 2;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Target Plan & Duration</span>
        <span style="font-weight: 700; color: #ff007f;">${escapeHtml(lead.preferred_duration || 'Standard Plan')}</span>
      </div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 10px;">
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Primary Skills</span>
        <span style="font-size: 13px; color: #334155;">${escapeHtml(lead.primary_skills || 'None')}</span>
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px;">
        <span style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; display: block; margin-bottom: 4px;">Follow-Up Notes</span>
        <span style="font-size: 13px; color: #334155;">${escapeHtml(lead.follow_up_notes || 'No follow-up notes yet.')}</span>
      </div>
      <div style="display: flex; justify-content: space-between; font-size: 12px; color: #64748b; padding: 4px 6px;">
        <span><b>Associate:</b> ${escapeHtml(lead.employee_name || 'Unassigned')}</span>
        <span><b>Submitted:</b> ${escapeHtml(lead.submission_date)} ${escapeHtml(lead.submission_time)}</span>
      </div>
    </div>
  `;

  const modal = document.getElementById("viewModal");
  if (modal) modal.style.display = "flex";
}

function openEditModal(leadId) {
  const lead = allLeads.find(l => l.lead_id === leadId);
  if (!lead) return;

  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val || "";
  };

  setVal("editLeadId", lead.lead_id);
  setVal("editFullName", lead.full_name);
  setVal("editMobile", lead.mobile);
  setVal("editEmail", lead.email);
  setVal("editCategory", lead.category);
  setVal("editPrimarySkills", lead.primary_skills);
  setVal("editPreferredDuration", lead.preferred_duration || "Starter (Level 1) - 12 Months");
  setVal("editExperienceLevel", lead.experience_level || "Beginner");
  setVal("editLeadStatus", lead.lead_status || "New Enquiry");
  setVal("editFollowUpNotes", lead.follow_up_notes);
  setVal("editNextDate", lead.next_follow_up_date);

  const modal = document.getElementById("editModal");
  if (modal) modal.style.display = "flex";
}

async function handleEditSubmit(event) {
  event.preventDefault();
  const leadId = document.getElementById("editLeadId").value;
  if (!leadId) return;

  const currentLead = allLeads.find(l => l.lead_id === leadId) || {};

  const candidatePayload = {
    full_name: document.getElementById("editFullName").value,
    email: document.getElementById("editEmail").value,
    mobile: document.getElementById("editMobile").value,
    category: document.getElementById("editCategory").value,
    primary_skills: document.getElementById("editPrimarySkills").value,
    preferred_duration: document.getElementById("editPreferredDuration").value,
    experience_level: document.getElementById("editExperienceLevel").value,
    current_status: currentLead.current_status || "Student",
    questions: currentLead.questions || ""
  };

  const statusNotesPayload = {
    lead_status: document.getElementById("editLeadStatus").value,
    follow_up_notes: document.getElementById("editFollowUpNotes").value,
    next_follow_up_date: document.getElementById("editNextDate").value
  };

  try {
    const putRes = await fetch(`/api/admin/lead/${leadId}`, {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(candidatePayload)
    });

    const patchRes = await fetch(`/api/admin/lead/${leadId}`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(statusNotesPayload)
    });

    if (putRes.ok && patchRes.ok) {
      closeModal("editModal");
      await fetchLeads();
    } else {
      alert("Failed to update candidate record.");
    }
  } catch (err) {
    alert("Network error updating candidate record.");
  }
}

function closeModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.style.display = "none";
}

async function handleLogout() {
  if (!confirm("Are you sure you want to end your active administrative session?")) return;
  try {
    await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
  } finally {
    window.location.href = "/login";
  }
}

// Bind live search & filter listeners
const searchInputEl = document.getElementById("searchInput");
if (searchInputEl) searchInputEl.addEventListener("input", filterAndRenderTable);

const statusFilterEl = document.getElementById("statusFilter");
if (statusFilterEl) statusFilterEl.addEventListener("change", filterAndRenderTable);

const dateFilterEl = document.getElementById("dateFilter");
if (dateFilterEl) dateFilterEl.addEventListener("change", filterAndRenderTable);

window.onclick = function(event) {
  if (event.target.classList && event.target.classList.contains("modal-backdrop")) {
    event.target.style.display = "none";
  }
};

// Bootstrap Leads on load
fetchLeads();

function fetchAnalytics() {
  fetch('/api/analytics')
    .then(res => res.json())
    .then(data => {
      // 1. Update Core Metric Counters
      const elUnique = document.getElementById('anaUnique');
      const elPlanViews = document.getElementById('anaPlanViews');
      const elPlanClicks = document.getElementById('anaPlanClicks');
      const elAbandons = document.getElementById('anaAbandons');
      const elTotalTag = document.getElementById('telTotalViewsTag');

      if (elUnique) elUnique.innerText = (data.unique_visitors || 0).toLocaleString();
      if (elPlanViews) elPlanViews.innerText = (data.plan_section_views || 0).toLocaleString();
      if (elPlanClicks) elPlanClicks.innerText = (data.plan_clicks || 0).toLocaleString();
      if (elAbandons) elAbandons.innerText = (data.form_abandonment || 0).toLocaleString();
      if (elTotalTag) elTotalTag.innerText = `${(data.total_visitors || 0).toLocaleString()} Views`;

      // 2. Render Traffic Sources with Progress Bars
      const tList = document.getElementById('anaTrafficList');
      if (tList && data.traffic_sources) {
        if (!data.traffic_sources.length) {
          tList.innerHTML = '<li class="tel-empty-row">No traffic sources logged yet.</li>';
        } else {
          const maxTraffic = Math.max(...data.traffic_sources.map(s => s.count), 1);
          tList.innerHTML = data.traffic_sources.map(s => {
            const pct = Math.round((s.count / maxTraffic) * 100);
            return `
              <li class="tel-list-item">
                <div class="tel-item-top">
                  <span class="tel-item-name">${escapeHtml(s.traffic_source)}</span>
                  <span class="tel-item-count">${s.count.toLocaleString()} hits</span>
                </div>
                <div class="tel-progress-bg">
                  <div class="tel-progress-fill-cyan" style="width: ${pct}%;"></div>
                </div>
              </li>
            `;
          }).join('');
        }
      }

      // 3. Render Campaign Attribution with Progress Bars
      const cList = document.getElementById('anaCampaignList');
      if (cList && data.campaigns) {
        if (!data.campaigns.length) {
          cList.innerHTML = '<li class="tel-empty-row">No active campaign attribution logged.</li>';
        } else {
          const maxCamp = Math.max(...data.campaigns.map(c => c.count), 1);
          cList.innerHTML = data.campaigns.map(c => {
            const pct = Math.round((c.count / maxCamp) * 100);
            return `
              <li class="tel-list-item">
                <div class="tel-item-top">
                  <span class="tel-item-name">${escapeHtml(c.campaign)}</span>
                  <span class="tel-item-count">${c.count.toLocaleString()} leads/clicks</span>
                </div>
                <div class="tel-progress-bg">
                  <div class="tel-progress-fill-rose" style="width: ${pct}%;"></div>
                </div>
              </li>
            `;
          }).join('');
        }
      }
    })
    .catch(err => console.error("Telemetry fetch error:", err));
}

// Hook into initial page boot and refresh buttons
document.addEventListener('DOMContentLoaded', fetchAnalytics);
if (window.fetchLeads) {
  const _prevFetchLeads = window.fetchLeads;
  window.fetchLeads = function() {
    _prevFetchLeads();
    fetchAnalytics();
  };
}
window.fetchLeads = async function() {
  try {
    const res = await fetch("/api/admin/leads", { credentials: "include" });
    if (res.status === 401) {
      window.location.href = "/login";
      return;
    }
    if (!res.ok) {
      const tbody = document.getElementById("leadsTableBody");
      if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color: #f43f5e;">Failed to load leads (HTTP ${res.status}).</td></tr>`;
      return;
    }
    const data = await res.json();
    allLeads = data.leads || [];
    renderDashboard();
    if (typeof fetchAnalytics === "function") {
      fetchAnalytics();
    }
  } catch (err) {
    const tbody = document.getElementById("leadsTableBody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color: #f43f5e;">Network error connecting to backend API.</td></tr>`;
  }
};
async function refreshData() {
  const refreshBtn = document.getElementById("refreshBtn") || document.querySelector(".btn-refresh-nav");
  const originalHtml = refreshBtn ? refreshBtn.innerHTML : "Refresh Data";

  if (refreshBtn) {
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 0.8s linear infinite;">
        <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
      </svg> Refreshing...
    `;
  }

  try {
    await window.fetchLeads();
  } catch (err) {
    console.error("Refresh error:", err);
  } finally {
    if (refreshBtn) {
      refreshBtn.disabled = false;
      refreshBtn.innerHTML = originalHtml;
    }
  }
}
window.refreshData = refreshData;