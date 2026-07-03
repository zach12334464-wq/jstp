// TODO: Replace hardcoded password with Supabase admin auth when DB is set up
const ADMIN_PASSWORD = "JSTP_ADMIN_2026";

// ── DEFAULT PERSISTENT MOCK DATASETS ──
const defaultStudents = [
  {
    id: "stud_1",
    name: "Jerome Brown",
    school: "University of the West Indies",
    parish: "Kingston",
    level: "Undergraduate",
    status: "active",
    joined: "May 24, 2026",
    email: "jerome.brown@uwi.edu",
    phone: "+1 (876) 555-0123",
    bio: "Computer Science major passionate about frontend development and building accessible tools."
  },
  {
    id: "stud_2",
    name: "Alicia Morgan",
    school: "University of Technology",
    parish: "St Andrew",
    level: "Undergraduate",
    status: "active",
    joined: "May 23, 2026",
    email: "alicia.m@utech.edu.jm",
    phone: "+1 (876) 555-0199",
    bio: "Marketing enthusiast. Experienced in social media coordination and event photography."
  },
  {
    id: "stud_3",
    name: "Kemar Thompson",
    school: "Campion College",
    parish: "Kingston",
    level: "Sixth Form",
    status: "active",
    joined: "May 22, 2026",
    email: "kemar.thompson@campion.edu.jm",
    phone: "+1 (876) 555-0188",
    bio: "Mathematics and Physics CAPE student seeking a summer internship in data entry or tutor roles."
  }
];

const defaultBusinesses = [
  {
    id: "biz_1",
    company: "Island Co.",
    industry: "Business",
    parish: "Kingston",
    verified: true,
    status: "active",
    joined: "May 20, 2026",
    email: "hr@islandco.com",
    phone: "+1 (876) 555-9000",
    desc: "A premier local business services firm in Jamaica specializing in customer operations and outreach."
  },
  {
    id: "biz_2",
    company: "Tech Wave",
    industry: "Technology",
    parish: "Kingston",
    verified: false,
    status: "active",
    joined: "May 21, 2026",
    email: "careers@techwave.io",
    phone: "+1 (876) 555-4040",
    desc: "Innovative software development agency building web and mobile apps for the Caribbean and beyond."
  }
];

const defaultJobs = [
  {
    id: "job_1",
    title: "Marketing Intern",
    company: "Island Co.",
    source: "scraper",
    posted: "May 24, 2026",
    status: "active",
    desc: "Support our marketing team with campaign coordination, social media content, and email newsletter management. Unpaid. 3 months duration."
  },
  {
    id: "job_2",
    title: "Junior Web Developer",
    company: "Tech Wave",
    source: "direct",
    posted: "May 23, 2026",
    status: "active",
    desc: "Looking for a student or fresh graduate to maintain and extend React client websites. Knowledge of HTML, CSS, and basic JavaScript required."
  },
  {
    id: "job_3",
    title: "Work from Home $50k/week",
    company: "Unknown",
    source: "scraper",
    posted: "May 23, 2026",
    status: "flagged",
    desc: "EASY WORK! Make 50k per week folding envelopes from the comfort of your home. No experience needed. Upfront fee of $2,000 JMD required for starter materials."
  },
  {
    id: "job_4",
    title: "Data Entry Specialist",
    company: "Appen",
    source: "scraper",
    posted: "May 24, 2026",
    status: "active",
    desc: "Part-time task-based remote work training AI models. Annotate text datasets and translate short English phrases to Jamaican Patois."
  }
];

const defaultReports = [
  {
    id: 1,
    type: 'JOB REPORT',
    time: '1 hour ago',
    subject: 'Reported listing: "Work from Home $50k/week"',
    reportedBy: 'Alicia Morgan (student)',
    reason: 'Possible scam — unrealistic salary promise and vague company',
    score: 0.91
  },
  {
    id: 2,
    type: 'BUSINESS REPORT',
    time: '3 hours ago',
    subject: 'Reported business: "QuickCash Jobs JA"',
    reportedBy: 'Kemar Thompson (student)',
    reason: 'Asked for bank account info during application — suspicious behaviour',
    score: 0.87
  },
  {
    id: 3,
    type: 'STUDENT REPORT',
    time: '5 hours ago',
    subject: 'Reported student: "testuser123@mail.com"',
    reportedBy: 'Island Co. (business)',
    reason: 'Submitted 40 applications in 2 minutes — bulk spam behaviour',
    score: 0.55
  }
];

// Seed databases if they are missing
if (!localStorage.getItem('jstp_students')) localStorage.setItem('jstp_students', JSON.stringify(defaultStudents));
if (!localStorage.getItem('jstp_businesses')) localStorage.setItem('jstp_businesses', JSON.stringify(defaultBusinesses));
if (!localStorage.getItem('jstp_jobs')) localStorage.setItem('jstp_jobs', JSON.stringify(defaultJobs));
if (!localStorage.getItem('jstp_reports')) localStorage.setItem('jstp_reports', JSON.stringify(defaultReports));
if (!localStorage.getItem('jstp_history')) localStorage.setItem('jstp_history', JSON.stringify([]));

// Seed admins if missing with Master Admin
const defaultAdmins = [
  {
    id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : 'admin_' + Math.random().toString(36).substr(2, 9),
    email: "zach12334464@gmail.com",
    password: "JSTP_ADMIN_2026",
    role: "master",
    createdAt: new Date().toISOString()
  }
];
if (!localStorage.getItem('jstp_admins')) {
  localStorage.setItem('jstp_admins', JSON.stringify(defaultAdmins));
}

function toggleAdminTabVisibility(role) {
  const link = document.getElementById('tabAdminsLink');
  if (link) {
    if (role === 'master') {
      link.classList.remove('hidden');
    } else {
      link.classList.add('hidden');
      const activeLink = document.querySelector('.sb-link.active');
      if (activeLink && activeLink.dataset.tab === 'admins') {
        document.querySelector('.sb-link[data-tab="overview"]')?.click();
      }
    }
  }
}

// ── LOGIN ──
document.getElementById('loginBtn').addEventListener('click', function() {
  const emailInput = document.getElementById('adminEmail').value.trim();
  const passwordInput = document.getElementById('adminPassword').value;
  
  const admins = JSON.parse(localStorage.getItem('jstp_admins') || '[]');
  const matchedAdmin = admins.find(a => a.email.toLowerCase() === emailInput.toLowerCase() && a.password === passwordInput);
  
  if (matchedAdmin) {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('adminDashboard').classList.remove('hidden');
    sessionStorage.setItem('jstp_admin', JSON.stringify({
      id: matchedAdmin.id,
      email: matchedAdmin.email,
      role: matchedAdmin.role
    }));
    toggleAdminTabVisibility(matchedAdmin.role);
    renderAll();
  } else {
    document.getElementById('loginError').classList.remove('hidden');
    document.getElementById('adminPassword').value = '';
  }
});

document.getElementById('adminEmail')?.addEventListener('keydown', function(e) {
  if (e.key === 'Enter') document.getElementById('loginBtn').click();
});
document.getElementById('adminPassword').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') document.getElementById('loginBtn').click();
});

// Auto-login if already authenticated this session
const loggedInAdmin = JSON.parse(sessionStorage.getItem('jstp_admin') || 'null');
if (loggedInAdmin) {
  document.getElementById('loginScreen').classList.add('hidden');
  document.getElementById('adminDashboard').classList.remove('hidden');
  toggleAdminTabVisibility(loggedInAdmin.role);
}

// ── LOGOUT ──
document.getElementById('logoutBtn').addEventListener('click', function() {
  sessionStorage.removeItem('jstp_admin');
  document.getElementById('adminDashboard').classList.add('hidden');
  document.getElementById('loginScreen').classList.remove('hidden');
  document.getElementById('adminEmail').value = '';
  document.getElementById('adminPassword').value = '';
});

// ── TAB NAVIGATION ──
const tabTitles = {
  overview: 'Overview',
  students: 'Students',
  businesses: 'Businesses',
  jobs: 'Job Posts',
  reports: 'Reports',
  breaches: 'Data Breach',
  admins: 'Admins'
};

document.querySelectorAll('.sb-link').forEach(function(link) {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    const tab = this.dataset.tab;
    
    // Check master admin permission for admins tab
    const currentAdmin = JSON.parse(sessionStorage.getItem('jstp_admin') || 'null');
    if (tab === 'admins' && (!currentAdmin || currentAdmin.role !== 'master')) {
      alert('Access denied: Master admin role required.');
      return;
    }

    document.querySelectorAll('.sb-link').forEach(l => l.classList.remove('active'));
    this.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.getElementById('tab-' + tab).classList.remove('hidden');
    document.getElementById('topbarTitle').textContent = tabTitles[tab] || tab;
    
    // Refresh tab content dynamically
    renderAll();
  });
});

// ── SEARCH REGISTER ──
document.getElementById('studentSearch')?.addEventListener('input', renderStudents);
document.getElementById('businessSearch')?.addEventListener('input', renderBusinesses);
document.getElementById('jobSearch')?.addEventListener('input', renderJobs);
document.getElementById('historySearch')?.addEventListener('input', renderHistory);

// ── JOB FILTER CHIPS ──
let currentJobFilter = 'all';
document.querySelectorAll('.filter-chip').forEach(function(chip) {
  chip.addEventListener('click', function() {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    this.classList.add('active');
    currentJobFilter = this.dataset.filter;
    renderJobs();
  });
});

// ── STUDENTS RENDERER ──
function renderStudents() {
  const tbody = document.getElementById('studentTableBody');
  if (!tbody) return;
  const students = JSON.parse(localStorage.getItem('jstp_students') || '[]');
  const q = document.getElementById('studentSearch')?.value.toLowerCase() || '';
  
  const filtered = students.filter(s => 
    s.name.toLowerCase().includes(q) ||
    s.school.toLowerCase().includes(q) ||
    s.parish.toLowerCase().includes(q) ||
    s.level.toLowerCase().includes(q) ||
    (s.id || '').toLowerCase().includes(q)
  );

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#888;padding:24px;">No students found.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(s => {
    const isSuspended = s.status === 'suspended';
    const statusBadge = isSuspended 
      ? '<span class="suspended-badge">SUSPENDED</span>'
      : '<span class="verified-badge">ACTIVE</span>';
    
    return `
      <tr>
        <td><code style="font-size: 11px; background: #eee; padding: 2px 4px; border-radius: 3px;">${s.id || 'N/A'}</code></td>
        <td><strong>${s.name}</strong></td>
        <td>${s.school}</td>
        <td>${s.parish}</td>
        <td>${s.level}</td>
        <td>${statusBadge}</td>
        <td>${s.joined}</td>
        <td>
          <button class="action-btn view" onclick="viewItem('student', '${s.id}')">View</button>
          <button class="action-btn suspend" onclick="toggleSuspend('student', '${s.id}')">${isSuspended ? 'Unsuspend' : 'Suspend'}</button>
          <button class="action-btn remove" onclick="confirmRemoveItem('student', '${s.id}', '${s.name}')">Remove</button>
        </td>
      </tr>
    `;
  }).join('');
}

// ── BUSINESS RENDERER ──
function renderBusinesses() {
  const tbody = document.getElementById('businessTableBody');
  if (!tbody) return;
  const businesses = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
  const q = document.getElementById('businessSearch')?.value.toLowerCase() || '';

  const filtered = businesses.filter(b =>
    b.company.toLowerCase().includes(q) ||
    b.industry.toLowerCase().includes(q) ||
    b.parish.toLowerCase().includes(q) ||
    (b.id || '').toLowerCase().includes(q)
  );

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#888;padding:24px;">No businesses found.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(b => {
    const isSuspended = b.status === 'suspended';
    const statusBadge = isSuspended 
      ? '<span class="suspended-badge">SUSPENDED</span>'
      : '<span class="verified-badge">ACTIVE</span>';
    
    const verifyBadge = b.verified 
      ? '<span class="verified-badge">VERIFIED</span>'
      : '<span class="unverified-badge">UNVERIFIED</span>';

    return `
      <tr>
        <td><code style="font-size: 11px; background: #eee; padding: 2px 4px; border-radius: 3px;">${b.id || 'N/A'}</code></td>
        <td><strong>${b.company}</strong></td>
        <td>${b.industry}</td>
        <td>${b.parish}</td>
        <td>${verifyBadge}</td>
        <td>${statusBadge}</td>
        <td>${b.joined}</td>
        <td>
          <button class="action-btn view" onclick="viewItem('business', '${b.id}')">View</button>
          <button class="action-btn warn" onclick="openWarnModal('business', '${b.company}', '${b.id}')">Warn</button>
          <button class="action-btn suspend" onclick="toggleSuspend('business', '${b.id}')">${isSuspended ? 'Unsuspend' : 'Suspend'}</button>
          <button class="action-btn remove" onclick="confirmRemoveItem('business', '${b.id}', '${b.company}')">Remove</button>
        </td>
      </tr>
    `;
  }).join('');
}

// ── JOBS RENDERER ──
function renderJobs() {
  const tbody = document.getElementById('jobTableBody');
  if (!tbody) return;
  const jobs = JSON.parse(localStorage.getItem('jstp_jobs') || '[]');
  const q = document.getElementById('jobSearch')?.value.toLowerCase() || '';

  const filtered = jobs.filter(j => {
    const matchSearch = j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q);
    if (!matchSearch) return false;

    if (currentJobFilter === 'all') return true;
    if (currentJobFilter === 'flagged') return j.status === 'flagged';
    return j.source === currentJobFilter;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#888;padding:24px;">No job posts found.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(j => {
    const isFlagged = j.status === 'flagged';
    const statusBadge = isFlagged 
      ? '<span class="status-flagged">FLAGGED</span>'
      : '<span class="status-active">ACTIVE</span>';

    const sourceBadge = j.source === 'scraper'
      ? '<span class="source-tag scraper">SYSTEM</span>'
      : '<span class="source-tag direct">DIRECT</span>';

    return `
      <tr data-source="${j.source}">
        <td><strong>${j.title}</strong></td>
        <td>${j.company}</td>
        <td>${sourceBadge}</td>
        <td>${j.posted}</td>
        <td>${statusBadge}</td>
        <td>
          <button class="action-btn view" onclick="viewItem('job', '${j.id}')">View</button>
          <button class="action-btn remove" onclick="confirmRemoveItem('job', '${j.id}', '${j.title}')">Remove</button>
        </td>
      </tr>
    `;
  }).join('');
}

// ── REPORTS RENDERER ──
function renderReports() {
  const reportList = document.getElementById('reportList');
  if (!reportList) return;
  const reports = JSON.parse(localStorage.getItem('jstp_reports') || '[]');
  
  // Update badge count
  const badge = document.getElementById('reportBadge');
  if (badge) {
    badge.textContent = reports.length;
  }
  const overviewBadge = document.querySelector('.metric-card.alert .metric-value');
  if (overviewBadge) {
    overviewBadge.textContent = reports.length;
  }

  if (reports.length === 0) {
    reportList.innerHTML = '<div style="padding:32px;text-align:center;color:#888;font-size:14px;">No open reports.</div>';
    return;
  }

  reportList.innerHTML = reports.map(r => {
    let scoreClass = 'score-low';
    let riskLevel = 'Low Risk';
    if (r.score >= 0.8) {
      scoreClass = 'score-high';
      riskLevel = 'High Risk';
    } else if (r.score >= 0.5) {
      scoreClass = 'score-medium';
      riskLevel = 'Medium Risk';
    }
    
    return `
      <div class="report-card" id="report-${r.id}">
        <div class="report-card-top">
          <span class="report-type ${r.type.toLowerCase().includes('job') ? 'job' : r.type.toLowerCase().includes('business') ? 'business' : 'student'}">${r.type}</span>
          <span class="report-time">${r.time}</span>
        </div>
        <div class="report-subject">${r.subject}</div>
        <div class="report-body">
          <div class="report-row"><span class="report-label">REPORTED BY</span><span>${r.reportedBy}</span></div>
          <div class="report-row"><span class="report-label">REASON</span><span>${r.reason}</span></div>
          <div class="report-row"><span class="report-label">AI FLAG / SCORE</span><span class="${scoreClass}">${r.score} &mdash; ${riskLevel}</span></div>
        </div>
        <div class="report-actions">
          <button class="action-btn remove" onclick="resolveReport('${r.id}', 'remove')">${r.type === 'JOB REPORT' ? 'Remove Listing' : r.type === 'BUSINESS REPORT' ? 'Remove Business' : 'Suspend Account'}</button>
          <button class="action-btn warn" onclick="resolveReport('${r.id}', 'warn')">Send Warning</button>
          <button class="action-btn view" onclick="resolveReport('${r.id}', 'dismiss')">Dismiss</button>
        </div>
      </div>
    `;
  }).join('');
}

// ── OVERVIEW METRICS RENDERER ──
function renderOverviewMetrics() {
  const students = JSON.parse(localStorage.getItem('jstp_students') || '[]');
  const businesses = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
  const jobs = JSON.parse(localStorage.getItem('jstp_jobs') || '[]');
  const reports = JSON.parse(localStorage.getItem('jstp_reports') || '[]');

  const totalStudentsEl = document.getElementById('metricTotalStudents');
  const totalBusinessesEl = document.getElementById('metricTotalBusinesses');
  const activeJobsEl = document.getElementById('metricActiveJobs');
  const openReportsEl = document.getElementById('metricOpenReports');

  if (totalStudentsEl) totalStudentsEl.textContent = students.length;
  if (totalBusinessesEl) totalBusinessesEl.textContent = businesses.length;
  if (activeJobsEl) activeJobsEl.textContent = jobs.length;
  if (openReportsEl) openReportsEl.textContent = reports.length;
}

// ── HISTORY HELPERS ──
function pushHistory(action, target) {
  const history = JSON.parse(localStorage.getItem('jstp_history') || '[]');
  const currentAdmin = JSON.parse(sessionStorage.getItem('jstp_admin') || 'null');
  const adminEmail = currentAdmin ? currentAdmin.email : 'system@jstp.com';

  history.unshift({
    adminEmail,
    action,
    target,
    timestamp: new Date().toLocaleString('en-JM', { dateStyle: 'medium', timeStyle: 'short' })
  });
  localStorage.setItem('jstp_history', JSON.stringify(history));
}

// ── HISTORY RENDERER ──
function renderHistory() {
  const list = document.getElementById('historyLogList');
  if (!list) return;
  const history = JSON.parse(localStorage.getItem('jstp_history') || '[]');
  const q = (document.getElementById('historySearch')?.value || '').toLowerCase();

  const filtered = history.filter(h =>
    h.action.toLowerCase().includes(q) ||
    h.target.toLowerCase().includes(q) ||
    (h.adminEmail || '').toLowerCase().includes(q)
  );

  if (filtered.length === 0) {
    list.innerHTML = '<div class="activity-row" style="color:#888;font-size:13px;padding:16px 0;">No history recorded yet.</div>';
    return;
  }

  list.innerHTML = filtered.map(h => {
    const author = h.adminEmail || 'system@jstp.com';
    return `
      <div class="activity-row">
        <span class="activity-type" style="background:#e0e0e0;color:#444;">${h.action.split(' ')[0].toUpperCase()}</span>
        <span class="activity-text"><strong>${author}</strong> ${h.action} — <strong>${h.target}</strong></span>
        <span class="activity-time">${h.timestamp}</span>
      </div>
    `;
  }).join('');
}

// ── CLEAR HISTORY ──
function clearHistory() {
  if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) return;
  localStorage.setItem('jstp_history', JSON.stringify([]));
  renderHistory();
}

// ── ADMINS RENDERER ──
function renderAdmins() {
  const tbody = document.getElementById('adminTableBody');
  if (!tbody) return;
  const admins = JSON.parse(localStorage.getItem('jstp_admins') || '[]');
  
  tbody.innerHTML = admins.map(admin => {
    const currentAdmin = JSON.parse(sessionStorage.getItem('jstp_admin') || 'null');
    const isSelf = currentAdmin && currentAdmin.id === admin.id;
    const deleteBtn = isSelf 
      ? '<span style="color: #888; font-size: 12px; font-weight: 600;">(Current Admin)</span>'
      : `<button class="action-btn remove" onclick="removeAdmin('${admin.id}', '${admin.email}')">Remove</button>`;
      
    const formattedDate = admin.createdAt ? new Date(admin.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A';
    
    return `
      <tr>
        <td><strong>${admin.email}</strong></td>
        <td><span class="source-tag ${admin.role === 'master' ? 'direct' : 'scraper'}">${admin.role.toUpperCase()}</span></td>
        <td>${formattedDate}</td>
        <td>${deleteBtn}</td>
      </tr>
    `;
  }).join('');
}

// ── ADMIN ACTIONS ──
function removeAdmin(id, email) {
  const currentAdmin = JSON.parse(sessionStorage.getItem('jstp_admin') || 'null');
  if (currentAdmin && currentAdmin.id === id) {
    alert("You cannot remove your own admin account.");
    return;
  }
  if (!confirm(`Are you sure you want to remove admin account "${email}"? This action cannot be undone.`)) {
    return;
  }
  let admins = JSON.parse(localStorage.getItem('jstp_admins') || '[]');
  admins = admins.filter(a => a.id !== id);
  localStorage.setItem('jstp_admins', JSON.stringify(admins));
  
  pushHistory('removed admin', email);
  
  renderAdmins();
}
window.removeAdmin = removeAdmin;

function openAddAdminModal() {
  document.getElementById('newAdminEmail').value = '';
  document.getElementById('newAdminPassword').value = '';
  document.getElementById('newAdminRole').value = 'regular';
  document.getElementById('addAdminError').classList.add('hidden');
  document.getElementById('addAdminModal').classList.remove('hidden');
}
window.openAddAdminModal = openAddAdminModal;

function closeAddAdminModal() {
  document.getElementById('addAdminModal').classList.add('hidden');
}
window.closeAddAdminModal = closeAddAdminModal;

// Close add admin modal on overlay click
document.getElementById('addAdminModal')?.addEventListener('click', function(e) {
  if (e.target === this) closeAddAdminModal();
});

document.getElementById('addAdminConfirm')?.addEventListener('click', function() {
  const email = document.getElementById('newAdminEmail').value.trim();
  const password = document.getElementById('newAdminPassword').value;
  const role = document.getElementById('newAdminRole').value;
  const errorEl = document.getElementById('addAdminError');
  
  errorEl.classList.add('hidden');
  
  if (!email || !password) {
    errorEl.textContent = 'Please fill in all fields.';
    errorEl.classList.remove('hidden');
    return;
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errorEl.textContent = 'Please enter a valid email address.';
    errorEl.classList.remove('hidden');
    return;
  }
  
  const admins = JSON.parse(localStorage.getItem('jstp_admins') || '[]');
  if (admins.some(a => a.email.toLowerCase() === email.toLowerCase())) {
    errorEl.textContent = 'An admin account with this email already exists.';
    errorEl.classList.remove('hidden');
    return;
  }
  
  const newAdmin = {
    id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : 'admin_' + Math.random().toString(36).substr(2, 9),
    email,
    password,
    role,
    createdAt: new Date().toISOString()
  };
  
  admins.push(newAdmin);
  localStorage.setItem('jstp_admins', JSON.stringify(admins));
  
  pushHistory('added new admin', email);
  
  renderAdmins();
  closeAddAdminModal();
});

function renderAll() {
  renderStudents();
  renderBusinesses();
  renderJobs();
  renderReports();
  renderOverviewMetrics();
  renderHistory();
  renderAdmins();
}

// ── VIEW ITEM MODAL logic ──
function viewItem(type, id) {
  let title = '';
  let content = '';

  if (type === 'student') {
    const list = JSON.parse(localStorage.getItem('jstp_students') || '[]');
    const item = list.find(x => x.id === id);
    if (!item) return;
    title = 'Student Profile: ' + item.name;
    content = `
      <div class="detail-row"><span class="detail-label">Name</span><span class="detail-val">${item.name}</span></div>
      <div class="detail-row"><span class="detail-label">School</span><span class="detail-val">${item.school}</span></div>
      <div class="detail-row"><span class="detail-label">Parish</span><span class="detail-val">${item.parish}</span></div>
      <div class="detail-row"><span class="detail-label">Academic Level</span><span class="detail-val">${item.level}</span></div>
      <div class="detail-row"><span class="detail-label">Email Address</span><span class="detail-val">${item.email}</span></div>
      <div class="detail-row"><span class="detail-label">WhatsApp/Tel</span><span class="detail-val">${item.phone}</span></div>
      <div class="detail-row"><span class="detail-label">Joined Date</span><span class="detail-val">${item.joined}</span></div>
      <div class="detail-row"><span class="detail-label">Account Status</span><span class="detail-val">${item.status.toUpperCase()}</span></div>
      <div class="detail-row"><span class="detail-label">Biography</span><span class="detail-val" style="font-weight: normal;">${item.bio || 'No biography written.'}</span></div>
    `;
  } else if (type === 'business') {
    const list = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
    const item = list.find(x => x.id === id);
    if (!item) return;
    title = 'Business Profile: ' + item.company;
    content = `
      <div class="detail-row"><span class="detail-label">Company Name</span><span class="detail-val">${item.company}</span></div>
      <div class="detail-row"><span class="detail-label">Industry</span><span class="detail-val">${item.industry}</span></div>
      <div class="detail-row"><span class="detail-label">Parish</span><span class="detail-val">${item.parish}</span></div>
      <div class="detail-row"><span class="detail-label">Verification Status</span><span class="detail-val">${item.verified ? 'VERIFIED' : 'UNVERIFIED'}</span></div>
      <div class="detail-row"><span class="detail-label">Email Address</span><span class="detail-val">${item.email}</span></div>
      <div class="detail-row"><span class="detail-label">Contact Number</span><span class="detail-val">${item.phone}</span></div>
      <div class="detail-row"><span class="detail-label">Joined Date</span><span class="detail-val">${item.joined}</span></div>
      <div class="detail-row"><span class="detail-label">Account Status</span><span class="detail-val">${item.status.toUpperCase()}</span></div>
      <div class="detail-row"><span class="detail-label">Company Overview</span><span class="detail-val" style="font-weight: normal;">${item.desc || 'No overview written.'}</span></div>
    `;
  } else if (type === 'job') {
    const list = JSON.parse(localStorage.getItem('jstp_jobs') || '[]');
    const item = list.find(x => x.id === id);
    if (!item) return;
    title = 'Job Listing: ' + item.title;
    content = `
      <div class="detail-row"><span class="detail-label">Job Title</span><span class="detail-val">${item.title}</span></div>
      <div class="detail-row"><span class="detail-label">Company</span><span class="detail-val">${item.company}</span></div>
      <div class="detail-row"><span class="detail-label">Posting Source</span><span class="detail-val">${item.source.toUpperCase()}</span></div>
      <div class="detail-row"><span class="detail-label">Date Posted</span><span class="detail-val">${item.posted}</span></div>
      <div class="detail-row"><span class="detail-label">Listing Status</span><span class="detail-val">${item.status.toUpperCase()}</span></div>
      <div class="detail-row"><span class="detail-label">Job Description</span><span class="detail-val" style="font-weight: normal;">${item.desc}</span></div>
    `;
  }

  document.getElementById('viewModalTitle').textContent = title;
  document.getElementById('viewModalBody').innerHTML = content;
  document.getElementById('viewModal').classList.remove('hidden');
}

function closeViewModal() {
  document.getElementById('viewModal').classList.add('hidden');
}

// Close on overlay click
document.getElementById('viewModal')?.addEventListener('click', function(e) {
  if (e.target === this) closeViewModal();
});

// ── WARNING MODAL logic ──
let pendingWarning = null;

function openWarnModal(targetType, targetName, targetId, reportId = null) {
  pendingWarning = { targetType, targetName, targetId, reportId };
  document.getElementById('warnModalSubtitle').textContent = 'Compose warning message to ' + targetType + ' "' + targetName + '":';
  document.getElementById('warnMessage').value = '';
  document.getElementById('warnModal').classList.remove('hidden');
}

function closeWarnModal() {
  document.getElementById('warnModal').classList.add('hidden');
  pendingWarning = null;
}

document.getElementById('warnModalConfirm')?.addEventListener('click', function() {
  if (!pendingWarning) return;
  const msg = document.getElementById('warnMessage').value.trim();
  if (!msg) {
    alert('Please enter a warning message.');
    return;
  }
  
  // Alert and simulate sending
  alert('Warning message sent successfully to ' + pendingWarning.targetName + ':\n\n"' + msg + '"');
  
  // If warning came from a report card, resolve the report
  if (pendingWarning.reportId) {
    completeResolveReport(pendingWarning.reportId, 'warn');
  }

  closeWarnModal();
});

// Close on overlay click
document.getElementById('warnModal')?.addEventListener('click', function(e) {
  if (e.target === this) closeWarnModal();
});

// ── SUSPEND / UNSUSPEND account toggling ──
let pendingSuspend = null;

function toggleSuspend(type, id) {
  if (type === 'student') {
    const list = JSON.parse(localStorage.getItem('jstp_students') || '[]');
    const item = list.find(x => x.id === id);
    if (!item) return;
    const action = item.status === 'suspended' ? 'unsuspend' : 'suspend';
    pendingSuspend = { type, id, name: item.name, action };
  } else if (type === 'business') {
    const list = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
    const item = list.find(x => x.id === id);
    if (!item) return;
    const action = item.status === 'suspended' ? 'unsuspend' : 'suspend';
    pendingSuspend = { type, id, name: item.company, action };
  }

  if (pendingSuspend) {
    const actionLabel = pendingSuspend.action === 'suspend' ? 'Suspend Account' : 'Unsuspend Account';
    document.getElementById('suspendModalTitle').textContent = actionLabel;
    document.getElementById('suspendModalSubtitle').textContent = `Are you sure you want to ${pendingSuspend.action} ${type} "${pendingSuspend.name}"?`;
    document.getElementById('suspendReason').value = '';
    document.getElementById('suspendModalConfirm').textContent = actionLabel;
    document.getElementById('suspendModal').classList.remove('hidden');
  }
}

function closeSuspendModal() {
  document.getElementById('suspendModal').classList.add('hidden');
  pendingSuspend = null;
}
window.closeSuspendModal = closeSuspendModal;

document.getElementById('suspendModalConfirm')?.addEventListener('click', function() {
  if (!pendingSuspend) return;
  const { type, id, name, action } = pendingSuspend;

  if (type === 'student') {
    const list = JSON.parse(localStorage.getItem('jstp_students') || '[]');
    const item = list.find(x => x.id === id);
    if (item) {
      item.status = action === 'suspend' ? 'suspended' : 'active';
      localStorage.setItem('jstp_students', JSON.stringify(list));
      pushHistory(item.status === 'suspended' ? 'Suspended student' : 'Unsuspended student', name);
      renderStudents();
    }
  } else if (type === 'business') {
    const list = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
    const item = list.find(x => x.id === id);
    if (item) {
      item.status = action === 'suspend' ? 'suspended' : 'active';
      localStorage.setItem('jstp_businesses', JSON.stringify(list));
      pushHistory(item.status === 'suspended' ? 'Suspended business' : 'Unsuspended business', name);
      renderBusinesses();
    }
  }

  renderHistory();
  closeSuspendModal();
});

// Close suspend modal on overlay click
document.getElementById('suspendModal')?.addEventListener('click', function(e) {
  if (e.target === this) closeSuspendModal();
});

// ── CONFIRM REMOVE MODAL logic ──
let pendingRemove = null;

function confirmRemoveItem(type, id, name) {
  pendingRemove = { type, id, name };
  document.getElementById('modalTitle').textContent = 'Confirm Removal';
  document.getElementById('modalBody').textContent =
    'Are you sure you want to remove ' + type + ': "' + name + '"? This action cannot be undone.';
  document.getElementById('confirmModal').classList.remove('hidden');
}

document.getElementById('modalConfirm').addEventListener('click', function() {
  if (!pendingRemove) return;
  const { type, id, name } = pendingRemove;

  if (type === 'student') {
    let list = JSON.parse(localStorage.getItem('jstp_students') || '[]');
    list = list.filter(x => x.id !== id);
    localStorage.setItem('jstp_students', JSON.stringify(list));
  } else if (type === 'business') {
    let list = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
    list = list.filter(x => x.id !== id);
    localStorage.setItem('jstp_businesses', JSON.stringify(list));
  } else if (type === 'job') {
    let list = JSON.parse(localStorage.getItem('jstp_jobs') || '[]');
    list = list.filter(x => x.id !== id);
    localStorage.setItem('jstp_jobs', JSON.stringify(list));
  }

  pushHistory('Removed ' + type, name);
  alert('Successfully removed ' + type + ': "' + name + '".');
  closeModal();
  renderAll();
});

function closeModal() {
  document.getElementById('confirmModal').classList.add('hidden');
  pendingRemove = null;
}

// Close modal on overlay click
document.getElementById('confirmModal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

// ── RESOLVE REPORTS ──
function resolveReport(id, action) {
  const card = document.getElementById('report-' + id);
  if (!card) return;
  
  if (action === 'dismiss') {
    alert('Report dismissed.');
    completeResolveReport(id, 'dismiss');
  } else if (action === 'warn') {
    const reports = JSON.parse(localStorage.getItem('jstp_reports') || '[]');
    const report = reports.find(r => String(r.id) === String(id));
    const name = report ? report.reportedBy : 'Reported Party';
    openWarnModal('reported party', name, 'report_target', id);
  } else if (action === 'remove') {
    const reports = JSON.parse(localStorage.getItem('jstp_reports') || '[]');
    const report = reports.find(r => String(r.id) === String(id));
    if (report) {
      if (report.type === 'JOB REPORT') {
        const jobTitle = report.subject.replace('Reported listing: "', '').replace('"', '').replace('Reported listing: “', '').replace('”', '').trim();
        const jobs = JSON.parse(localStorage.getItem('jstp_jobs') || '[]');
        const jobObj = jobs.find(j => j.title === jobTitle);
        if (jobObj) {
          confirmRemoveItem('job', jobObj.id, jobObj.title);
          completeResolveReport(id, 'remove');
          return;
        }
      } else if (report.type === 'STUDENT REPORT') {
        const studentEmail = report.subject.replace('Reported student: "', '').replace('"', '').replace('Reported student: “', '').replace('”', '').trim();
        const students = JSON.parse(localStorage.getItem('jstp_students') || '[]');
        const studObj = students.find(s => s.email === studentEmail);
        if (studObj) {
          toggleSuspend('student', studObj.id);
          completeResolveReport(id, 'remove');
          return;
        }
      } else if (report.type === 'BUSINESS REPORT') {
        const bizName = report.subject.replace('Reported business: "', '').replace('"', '').replace('Reported business: “', '').replace('”', '').trim();
        const businesses = JSON.parse(localStorage.getItem('jstp_businesses') || '[]');
        const bizObj = businesses.find(b => b.company === bizName);
        if (bizObj) {
          toggleSuspend('business', bizObj.id);
          completeResolveReport(id, 'remove');
          return;
        }
      }
    }
    
    alert('Action taken successfully.');
    completeResolveReport(id, 'remove');
  }
}

function completeResolveReport(id, action) {
  const card = document.getElementById('report-' + id);
  if (!card) return;
  const messages = {
    remove: 'Listing/account removed.',
    warn: 'Warning sent to the account.',
    dismiss: 'Report dismissed.'
  };
  card.style.opacity = '0.4';
  card.style.pointerEvents = 'none';
  
  // Prevent duplicate messages if Warn confirms multiple times
  const existingNote = card.querySelector('.resolution-note');
  if (existingNote) existingNote.remove();

  const note = document.createElement('div');
  note.className = 'resolution-note';
  note.style.cssText = 'font-size:12px;color:#2e7d32;font-weight:700;margin-top:12px;text-transform:uppercase;letter-spacing:0.05em;';
  note.textContent = '\u2713 ' + messages[action];
  card.appendChild(note);
  
  // Record in history
  const allReports = JSON.parse(localStorage.getItem('jstp_reports') || '[]');
  const resolvedReport = allReports.find(r => String(r.id) === String(id));
  const reportTarget = resolvedReport ? resolvedReport.subject : 'Report #' + id;
  const actionLabels = { remove: 'Resolved report (action taken)', warn: 'Resolved report (warning sent)', dismiss: 'Dismissed report' };
  pushHistory(actionLabels[action] || 'Resolved report', reportTarget);

  // Remove from localStorage
  let reports = allReports.filter(r => String(r.id) !== String(id));
  localStorage.setItem('jstp_reports', JSON.stringify(reports));

  setTimeout(() => {
    const badge = document.getElementById('reportBadge');
    if (badge) badge.textContent = reports.length;
    
    const metricVal = document.querySelector('.metric-card.alert .metric-value');
    if (metricVal) metricVal.textContent = reports.length;
    renderHistory();
  }, 1000);
}

// ── DATA BREACH SIMULATION FLOW ──
let simulationActive = false;
let currentBreachStep = 1;

document.getElementById('breachSimBtn').addEventListener('click', function() {
  if (simulationActive) {
    alert('A simulation is already active.');
    return;
  }
  
  simulationActive = true;
  currentBreachStep = 1;

  // Change system status to DANGER
  const status = document.getElementById('breachStatus');
  status.classList.remove('safe');
  status.classList.add('danger');
  status.querySelector('.breach-status-title').textContent = 'SIMULATION ACTIVE ── Mock Breach Detected';
  status.querySelector('.breach-status-sub').textContent = 'Please follow the Breach Response Protocol step-by-step to contain and report the incident.';

  // Hide the "No incidents recorded" label
  const logEmpty = document.getElementById('breachLogEmpty');
  if (logEmpty) logEmpty.style.display = 'none';

  // Log breach started
  logBreachIncident('Mock security breach detected. Target: Job listings API endpoint. Status: Uncontained.');

  // Initialize steps UI
  activateBreachStep(1);
});

function activateBreachStep(stepNum) {
  for (let i = 1; i <= 5; i++) {
    const card = document.getElementById('step-card-' + i);
    const btn = document.getElementById('step-btn-' + i);
    if (!card || !btn) continue;
    
    card.classList.remove('active-step', 'completed-step');
    btn.classList.add('hidden', 'disabled');
    
    if (i < stepNum) {
      card.classList.add('completed-step');
      btn.classList.remove('hidden', 'disabled');
      btn.classList.add('completed');
      btn.textContent = 'Completed \u2713';
    } else if (i === stepNum) {
      card.classList.add('active-step');
      btn.classList.remove('hidden', 'disabled', 'completed');
      btn.textContent = getBreachButtonText(i);
    } else {
      btn.classList.add('hidden');
    }
  }
}

function getBreachButtonText(step) {
  const texts = {
    1: 'Run Security Scan & Audit',
    2: 'Rotate API Keys & Revoke Sessions',
    3: 'Send User Notifications',
    4: 'Apply Security Patches',
    5: 'File Authority Report'
  };
  return texts[step] || 'Execute';
}

function executeBreachStep(stepNum) {
  if (!simulationActive || stepNum !== currentBreachStep) return;

  const logs = {
    1: 'Security audit complete. Scope: 14 mock job scraper listings flagged. No student credentials exposed.',
    2: 'Supabase anon keys rotated successfully. Containment status: Secured. 12 active sessions revoked.',
    3: 'Breach notification emails successfully queue-dispatched to all 247 student and 34 business users.',
    4: 'Vulnerability patch applied. Reviewed RLS policies and restricted access control permissions on public tables.',
    5: 'Incident report filed with Office of Information Commissioner (Jamaica) within the 72-hour window. Incident closed.'
  };

  logBreachIncident(logs[stepNum]);

  if (stepNum < 5) {
    currentBreachStep++;
    activateBreachStep(currentBreachStep);
  } else {
    // Simulation complete
    simulationActive = false;
    currentBreachStep = 1;

    // Reset status to safe
    const status = document.getElementById('breachStatus');
    status.classList.remove('danger');
    status.classList.add('safe');
    status.querySelector('.breach-status-title').textContent = 'System Status ── Safe (Resolved)';
    status.querySelector('.breach-status-sub').textContent = 'Simulation complete. System secured and reported. Incident Log stored locally.';

    // Make all buttons look completed
    for (let i = 1; i <= 5; i++) {
      const card = document.getElementById('step-card-' + i);
      const btn = document.getElementById('step-btn-' + i);
      if (card && btn) {
        card.classList.add('completed-step');
        btn.classList.add('completed');
        btn.textContent = 'Completed \u2713';
      }
    }
    
    alert('Security Breach Response Simulation completed successfully! The platform has been fully secured and documented.');
  }
}

function logBreachIncident(message) {
  const logList = document.getElementById('breachLogList');
  if (!logList) return;
  const entry = document.createElement('div');
  entry.className = 'breach-log-entry';
  entry.textContent = '[SIMULATION] ' + new Date().toLocaleTimeString() + ' ── ' + message;
  logList.prepend(entry);
}

// Render all on page load
renderAll();
