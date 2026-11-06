// Universal dialer handler for Mobile & PC
function dialNumber(phone) {
  const cleanPhone = (phone || '+918142559110').replace(/[^\d+]/g, '');

  // 1. Create a temporary hidden link element
  const tempLink = document.createElement('a');
  tempLink.href = 'tel:' + cleanPhone;
  tempLink.style.display = 'none';
  document.body.appendChild(tempLink);

  // 2. Click the link programmatically to trigger system dialer (Phone / Skype / Teams / Phone Link)
  tempLink.click();
  document.body.removeChild(tempLink);
}

// Active plan data dictionary matching official Talent Forge parameters
const PLAN_DATA = {
  "6": {
    p1: { desc: "One-time membership fee · 6 months", fee: "₹7,500 <span>/ 6 mo</span>", monthly: "₹3,000 – ₹4,200", potential: "₹18,000 – ₹25,200", tier: "Starter (Level 1) - 6 Months" },
    p2: { desc: "One-time membership fee · 6 months", fee: "₹13,500 <span>/ 6 mo</span>", monthly: "₹5,500 – ₹8,000", potential: "₹33,000 – ₹48,000", tier: "Professional (Level 2) - 6 Months" },
    p3: { desc: "One-time membership fee · 6 months", fee: "₹22,500 <span>/ 6 mo</span>", monthly: "₹9,500 – ₹14,000", potential: "₹57,000 – ₹84,000", tier: "Specialist (Level 3) - 6 Months" },
    p4: { desc: "One-time membership fee · 6 months", fee: "₹36,500 <span>/ 6 mo</span>", monthly: "₹15,500 – ₹23,000", potential: "₹93,000 – ₹1,38,000", tier: "Elite (Level 4) - 6 Months" },
    p5: { desc: "One-time membership fee · 6 months", fee: "₹56,500 <span>/ 6 mo</span>", monthly: "₹25,000 – ₹35,000", potential: "₹1,50,000 – ₹2,10,000", tier: "Auron (Level 5) - 6 Months" }
  },
  "12": {
    p1: { desc: "One-time membership fee · 12 months", fee: "₹12,000 <span>/ 12 mo</span>", monthly: "₹3,500 – ₹5,000", potential: "₹42,000 – ₹60,000", tier: "Starter (Level 1) - 12 Months" },
    p2: { desc: "One-time membership fee · 12 months", fee: "₹24,000 <span>/ 12 mo</span>", monthly: "₹7,000 – ₹10,000", potential: "₹84,000 – ₹1,20,000", tier: "Professional (Level 2) - 12 Months" },
    p3: { desc: "One-time membership fee · 12 months", fee: "₹42,000 <span>/ 12 mo</span>", monthly: "₹12,500 – ₹17,000", potential: "₹1,50,000 – ₹2,04,000", tier: "Specialist (Level 3) - 12 Months" },
    p4: { desc: "One-time membership fee · 12 months", fee: "₹70,000 <span>/ 12 mo</span>", monthly: "₹20,500 – ₹28,000", potential: "₹2,46,000 – ₹3,36,000", tier: "Elite (Level 4) - 12 Months" },
    p5: { desc: "One-time membership fee · 12 months", fee: "₹1,10,000 <span>/ 12 mo</span>", monthly: "₹32,500 – ₹42,500", potential: "₹3,90,000 – ₹5,10,000", tier: "Auron (Level 5) - 12 Months" }
  }
};

let currentDuration = "12";

// Switch duration on the membership cards
function switchDuration(duration) {
  currentDuration = duration;
  const btn6 = document.getElementById("btnDuration6");
  const btn12 = document.getElementById("btnDuration12");

  if (duration === "6") {
    btn6.style.background = "var(--gradient-brand)";
    btn6.style.color = "#ffffff";
    btn6.style.boxShadow = "0 4px 15px rgba(244, 63, 94, 0.4)";
    btn12.style.background = "transparent";
    btn12.style.color = "var(--text-secondary)";
    btn12.style.boxShadow = "none";
  } else {
    btn12.style.background = "var(--gradient-brand)";
    btn12.style.color = "#ffffff";
    btn12.style.boxShadow = "0 4px 15px rgba(244, 63, 94, 0.4)";
    btn6.style.background = "transparent";
    btn6.style.color = "var(--text-secondary)";
    btn6.style.boxShadow = "none";
  }

  const data = PLAN_DATA[duration];
  for (let i = 1; i <= 5; i++) {
    const key = `p${i}`;
    document.getElementById(`${key}-desc`).innerText = data[key].desc;
    document.getElementById(`${key}-fee`).innerHTML = data[key].fee;
    document.getElementById(`${key}-monthly`).innerText = data[key].monthly;
    document.getElementById(`${key}-potential`).innerText = data[key].potential;
    const btn = document.getElementById(`${key}-btn`);
    if (btn) {
      btn.setAttribute("data-tier", data[key].tier);
    }
  }
}

async function loadConfig() {
  const nameElem = document.getElementById("cardEmpName");
  const desigElem = document.getElementById("cardEmpDesig");
  const mailElem = document.getElementById("cardEmpMail");
  const phoneElem = document.getElementById("cardEmpPhone");
  const waElem = document.getElementById("cardEmpWa");

  // Default fallback data so it NEVER stays stuck on "Loading..."
  let empName = "Munendra Naick";
  let empDesig = "Talent Forge Associate";
  let empEmail = "munikumar@alphaauron.com";
  let rawPhone = "+918142559110";
  let rawWa = "918142559110";

  try {
    const res = await fetch("/api/config/public");
    if (res.ok) {
      const data = await res.json();
      if (data.employee_name) empName = data.employee_name;
      if (data.employee_designation) empDesig = data.employee_designation;
      if (data.employee_email) empEmail = data.employee_email;
      if (data.employee_phone) rawPhone = data.employee_phone;
      if (data.employee_whatsapp !== undefined) rawWa = data.employee_whatsapp;
    }
  } catch (err) {
    console.warn("Using default employee config:", err);
  }

  // 1. Sanitize phone numbers
  const cleanPhone = (rawPhone || "+918142559110").replace(/[^\d+]/g, '');
  const cleanWa = (rawWa || "").replace(/\D/g, '');

  // 2. Render Text
  if (nameElem) nameElem.innerText = empName;
  if (desigElem) desigElem.innerText = `${empDesig} · Alpha Auron Private Limited`;

  // 3. Render Email Button
  if (mailElem) mailElem.href = `mailto:${empEmail}`;
// 4. Guaranteed Call Button Handler
    const phoneElem = document.getElementById("cardEmpPhone");
    if (phoneElem) {
      phoneElem.onclick = function(e) {
        e.preventDefault(); // Stop desktop browser from redirecting to Google Search

        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

        if (isMobile) {
          // On mobile phones, open native phone dialer directly
          window.location.href = `tel:${cleanPhone}`;
        } else {
          // On PC/Laptop, open WhatsApp directly with a request for a voice call
          const callMsg = encodeURIComponent(`Hi ${empName}, I would like to have a voice call with you regarding Talent Forge membership.`);
          const targetWa = cleanWa || cleanPhone.replace(/\D/g, '');
          window.open(`https://api.whatsapp.com/send?phone=${targetWa}&text=${callMsg}`, '_blank');
        }
      };
    }

  // 5. Render WhatsApp Button (Only displayed if valid number exists)
  if (waElem) {
    if (cleanWa) {
      waElem.style.display = "inline-flex";
      waElem.href = `https://wa.me/${cleanWa}?text=Hi%20${encodeURIComponent(empName)},%20I%20have%20an%20enquiry%20regarding%20Talent%20Forge%20membership`;
    } else {
      waElem.style.display = "none";
    }
  }
}

// Ensure the DOM is fully loaded before updating the card
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", loadConfig);
} else {
  loadConfig();
}
// Analytics event dispatcher
function trackEvent(eventName) {
  const urlParams = new URLSearchParams(window.location.search);
  fetch("/api/track", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event: eventName,
      utm_campaign: urlParams.get("utm_campaign") || "Direct"
    })
  }).catch(() => {});
}

// Track page view and section views
trackEvent("page_view");

const planSection = document.getElementById("plans");
if (planSection) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        trackEvent("plan_section_view");
        observer.disconnect();
      }
    });
  }, { threshold: 0.3 });
  observer.observe(planSection);
}

// Bind plan card clicks to auto-select tier in form
document.querySelectorAll(".plan-select-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    trackEvent("plan_clicks");
    const tier = btn.getAttribute("data-tier");
    const tierSelect = document.getElementById("selected_tier");
    if (tierSelect && tier) {
      tierSelect.value = tier;
    }
  });
});

let formStarted = false;
document.getElementById("leadForm").addEventListener("focusin", () => {
  if (!formStarted) {
    trackEvent("form_starts");
    formStarted = true;
  }
});

// Form Submission
document.getElementById("leadForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const submitBtn = e.target.querySelector("button[type='submit']");
  const statusMsg = document.getElementById("statusMsg");

  submitBtn.disabled = true;
  submitBtn.innerText = "Submitting...";
  statusMsg.style.display = "block";
  statusMsg.style.background = "rgba(56, 189, 248, 0.1)";
  statusMsg.style.border = "1px solid #38bdf8";
  statusMsg.style.color = "#38bdf8";
  statusMsg.innerText = "Submitting your enquiry, please wait...";

  const urlParams = new URLSearchParams(window.location.search);

  const payload = {
    full_name: document.getElementById("full_name").value,
    email: document.getElementById("email").value,
    mobile: document.getElementById("mobile").value,
    category: document.getElementById("category").value,
    primary_skills: document.getElementById("primary_skills").value,
    experience_level: document.getElementById("experience_level").value,
    current_status: document.getElementById("current_status").value,
    preferred_duration: document.getElementById("selected_tier").value || "Not Specified",
    questions: document.getElementById("questions").value,
    website_hp_check: document.getElementById("website_hp_check").value,
    funnel_url: window.location.href,
    campaign_source: urlParams.get("utm_campaign") || "Direct",
    lead_source: urlParams.get("utm_source") || "Employee Landing Page"
  };

  try {
    const response = await fetch("/api/submit-lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json();

    if (response.ok) {
      statusMsg.style.background = "rgba(16, 185, 129, 0.15)";
      statusMsg.style.border = "1px solid #10b981";
      statusMsg.style.color = "#10b981";
      statusMsg.innerHTML = `<b>Success!</b> Reference ID: <b>${result.lead_id}</b>.<br>${result.message}`;
      document.getElementById("leadForm").reset();
    } else {
      statusMsg.style.background = "rgba(239, 68, 68, 0.15)";
      statusMsg.style.border = "1px solid #ef4444";
      statusMsg.style.color = "#ef4444";
      statusMsg.innerText = result.message || "Failed to submit enquiry.";
    }
  } catch (err) {
    statusMsg.style.background = "rgba(239, 68, 68, 0.15)";
    statusMsg.style.border = "1px solid #ef4444";
    statusMsg.style.color = "#ef4444";
    statusMsg.innerText = "Error connecting to server.";
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = "Submit Membership Enquiry";
  }
});

// Scroll-reveal animations
document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".disc-card, .step-card, .plan-card, .faq-box");
  
  cards.forEach(el => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)";
  });

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  cards.forEach(el => revealObserver.observe(el));
});