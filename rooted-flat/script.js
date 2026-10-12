/*
 * script.js — all frontend JavaScript in one file, organized into
 * sections: API calls, login state, theme, font size, notifications,
 * and page-specific behavior. Every HTML page loads this one file.
 */

const API_BASE = "/api";

// ============================================================
// SECTION 1: API — talks to the Flask backend
// ============================================================

function authHeaders() {
  const token = localStorage.getItem("rooted_token");
  return token ? { Authorization: "Bearer " + token } : {};
}

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

const api = {
  signup(body) {
    return fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  login(body) {
    return fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  forgotPassword(body) {
    return fetch(`${API_BASE}/auth/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  resetPassword(body) {
    return fetch(`${API_BASE}/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  getAccount() {
    return fetch(`${API_BASE}/account`, { headers: authHeaders() }).then(handleResponse);
  },
  updateHandle(body) {
    return fetch(`${API_BASE}/account/handle`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  updatePassword(body) {
    return fetch(`${API_BASE}/account/password`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  getDevotionals() {
    return fetch(`${API_BASE}/devotionals`).then(handleResponse);
  },
  getVerseOfDay() {
    return fetch(`${API_BASE}/verse-of-day`).then(handleResponse);
  },
  getAffirmations() {
    return fetch(`${API_BASE}/affirmations`).then(handleResponse);
  },
  getBibleStudies() {
    return fetch(`${API_BASE}/bible-studies`).then(handleResponse);
  },
  getStudySessions(studyId) {
    return fetch(`${API_BASE}/bible-studies/${studyId}/sessions`).then(handleResponse);
  },
  getScripture(ref) {
    return fetch(`${API_BASE}/scripture?ref=${encodeURIComponent(ref)}`).then(handleResponse);
  },
  getStudyGroups(studyId) {
    return fetch(`${API_BASE}/bible-studies/${studyId}/groups`, { headers: authHeaders() }).then(handleResponse);
  },
  createStudyGroup(studyId, body) {
    return fetch(`${API_BASE}/bible-studies/${studyId}/groups`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  toggleGroupSessionComplete(groupId, sessionId) {
    return fetch(`${API_BASE}/study-groups/${groupId}/sessions/${sessionId}/complete`, {
      method: "POST",
      headers: authHeaders(),
    }).then(handleResponse);
  },
  getMoodEmojis() {
    return fetch(`${API_BASE}/mood-emojis`).then(handleResponse);
  },
  getMoodJournal() {
    return fetch(`${API_BASE}/mood-journal`, { headers: authHeaders() }).then(handleResponse);
  },
  postMoodJournal(body) {
    return fetch(`${API_BASE}/mood-journal`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  deleteMoodJournal(id) {
    return fetch(`${API_BASE}/mood-journal/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    }).then(handleResponse);
  },
  getPrayerWall() {
    return fetch(`${API_BASE}/prayer-wall`).then(handleResponse);
  },
  postPrayer(body) {
    return fetch(`${API_BASE}/prayer-wall`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  prayFor(id) {
    return fetch(`${API_BASE}/prayer-wall/${id}/pray`, {
      method: "POST",
      headers: authHeaders(),
    }).then(handleResponse);
  },
  getGist() {
    return fetch(`${API_BASE}/gist`, { headers: authHeaders() }).then(handleResponse);
  },
  postGist(body) {
    return fetch(`${API_BASE}/gist`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  reactToGist(id, reaction) {
    return fetch(`${API_BASE}/gist/${id}/react`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ reaction }),
    }).then(handleResponse);
  },
  getFriends() {
    return fetch(`${API_BASE}/friends`, { headers: authHeaders() }).then(handleResponse);
  },
  getFriendRequests() {
    return fetch(`${API_BASE}/friends/requests`, { headers: authHeaders() }).then(handleResponse);
  },
  sendFriendRequest(handle) {
    return fetch(`${API_BASE}/friends/request`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ handle }),
    }).then(handleResponse);
  },
  acceptFriendRequest(id) {
    return fetch(`${API_BASE}/friends/${id}/accept`, {
      method: "POST",
      headers: authHeaders(),
    }).then(handleResponse);
  },
  declineFriendRequest(id) {
    return fetch(`${API_BASE}/friends/${id}/decline`, {
      method: "POST",
      headers: authHeaders(),
    }).then(handleResponse);
  },
  removeFriend(userId) {
    return fetch(`${API_BASE}/friends/${userId}`, {
      method: "DELETE",
      headers: authHeaders(),
    }).then(handleResponse);
  },
  report(body) {
    return fetch(`${API_BASE}/reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    }).then(handleResponse);
  },
  getNotifications() {
    return fetch(`${API_BASE}/notifications`, { headers: authHeaders() }).then(handleResponse);
  },
  markNotificationRead(id) {
    return fetch(`${API_BASE}/notifications/${id}/read`, { method: "POST", headers: authHeaders() }).then(handleResponse);
  },
  markAllNotificationsRead() {
    return fetch(`${API_BASE}/notifications/read-all`, { method: "POST", headers: authHeaders() }).then(handleResponse);
  },
};

// ============================================================
// SECTION 2: AUTH — tracks who's logged in, using localStorage
// ============================================================

const auth = {
  getHandle() {
    return localStorage.getItem("rooted_handle");
  },
  isLoggedIn() {
    return !!localStorage.getItem("rooted_token");
  },
  setSession(token, handle) {
    localStorage.setItem("rooted_token", token);
    localStorage.setItem("rooted_handle", handle);
  },
  logout() {
    localStorage.removeItem("rooted_token");
    localStorage.removeItem("rooted_handle");
    window.location.href = "index.html";
  },
};

function renderNavAuth() {
  const el = document.getElementById("nav-auth");
  if (!el) return;
  if (auth.isLoggedIn()) {
    el.innerHTML = `
      <li><a href="settings.html" class="nav-handle">@${auth.getHandle()}</a></li>
      <li><button class="report-link" id="signout-btn">Sign out</button></li>
    `;
    document.getElementById("signout-btn").addEventListener("click", auth.logout);
  } else {
    el.innerHTML = `<li><a href="login.html">Sign in</a></li>`;
  }
}

document.addEventListener("DOMContentLoaded", renderNavAuth);

function myUserId() {
  const token = localStorage.getItem("rooted_token");
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return decoded.id;
  } catch (e) {
    return null;
  }
}

// ============================================================
// SECTION 2b: THEME — light/dark mode, saved in localStorage
// ============================================================

const theme = {
  get() {
    return localStorage.getItem("rooted_theme") || "light";
  },
  apply(mode) {
    document.documentElement.setAttribute("data-theme", mode);
    localStorage.setItem("rooted_theme", mode);
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = mode === "dark" ? "☀️" : "🌙";
  },
  toggle() {
    theme.apply(theme.get() === "dark" ? "light" : "dark");
  },
};

document.addEventListener("DOMContentLoaded", () => {
  theme.apply(theme.get());
  const btn = document.getElementById("theme-toggle");
  if (btn) btn.addEventListener("click", theme.toggle);
});

// ============================================================
// SECTION 2c: FONT SIZE — small/medium/large/extra-large, saved
// in localStorage. Uses CSS zoom (supported in Chrome, Edge, Safari)
// so it actually reflows the layout rather than just scaling text.
// ============================================================

const FONT_SIZES = { small: 0.9, medium: 1, large: 1.15, "extra-large": 1.3 };

const fontSize = {
  get() {
    return localStorage.getItem("rooted_fontsize") || "medium";
  },
  apply(key) {
    const zoom = FONT_SIZES[key] || 1;
    document.body.style.zoom = zoom;
    localStorage.setItem("rooted_fontsize", key);
  },
};

document.addEventListener("DOMContentLoaded", () => {
  fontSize.apply(fontSize.get());
});

// ============================================================
// SECTION 2d: NOTIFICATIONS — bell icon with unread badge, shown
// on every page when logged in
// ============================================================

const NOTIF_ICONS = {
  reaction: "💬", prayer: "🙏", friend_request: "👥", friend_accept: "🤝",
};

async function loadNotifications() {
  const bell = document.getElementById("notif-bell");
  if (!bell || !auth.isLoggedIn()) return;
  try {
    const data = await api.getNotifications();
    const badge = document.getElementById("notif-badge");
    if (data.unread_count > 0) {
      badge.style.display = "flex";
      badge.textContent = data.unread_count > 9 ? "9+" : data.unread_count;
    } else {
      badge.style.display = "none";
    }

    const panel = document.getElementById("notif-panel");
    panel.innerHTML = data.notifications.length ? data.notifications.map(n => `
      <div class="notif-row ${n.read ? "" : "unread"}" onclick="markNotifRead('${n.id}')">
        <span class="notif-icon">${NOTIF_ICONS[n.type] || "🔔"}</span>
        <div>
          <div class="notif-message">${n.message}</div>
          <div class="notif-time">${new Date(n.created_at).toLocaleString()}</div>
        </div>
      </div>
    `).join("") : `<div class="notif-empty">Nothing new yet.</div>`;
  } catch (err) {
    // fail quietly — notifications shouldn't block the rest of the page
  }
}

async function markNotifRead(id) {
  try {
    await api.markNotificationRead(id);
    loadNotifications();
  } catch (err) {
    // ignore
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const bell = document.getElementById("notif-bell");
  if (!bell) return;

  if (!auth.isLoggedIn()) {
    bell.parentElement.style.display = "none";
    return;
  }

  loadNotifications();

  bell.addEventListener("click", (e) => {
    e.stopPropagation();
    const panel = document.getElementById("notif-panel");
    const isOpen = panel.style.display === "block";
    panel.style.display = isOpen ? "none" : "block";
    if (!isOpen) api.markAllNotificationsRead().then(() => {
      document.getElementById("notif-badge").style.display = "none";
    });
  });

  document.addEventListener("click", (e) => {
    const panel = document.getElementById("notif-panel");
    const wrap = bell.closest(".notif-wrap");
    if (panel && wrap && !wrap.contains(e.target)) panel.style.display = "none";
  });
});

// ============================================================
// SECTION 3: PAGE BEHAVIOR
// ============================================================

function showError(msg) {
  const box = document.getElementById("error-box");
  if (box) box.innerHTML = `<div class="error-msg">${msg}</div>`;
}

// ---- Home page (index.html) ----
document.addEventListener("DOMContentLoaded", () => {
  const joinBtn = document.getElementById("join-btn");
  if (joinBtn && auth.isLoggedIn()) joinBtn.style.display = "none";
});

// ---- Devotionals page: affirmations + verse of the day ----
async function loadAffirmations() {
  const wrap = document.getElementById("affirmations-wrap");
  if (!wrap) return;
  try {
    const affirmations = await api.getAffirmations();
    wrap.innerHTML = affirmations.map(text => `<div class="affirmation-bubble">${text}</div>`).join("");
  } catch (err) {
    wrap.innerHTML = "";
    showError(err.message);
  }
}
document.addEventListener("DOMContentLoaded", loadAffirmations);

async function loadVerseOfDay() {
  const card = document.getElementById("votd-card");
  if (!card) return;
  try {
    const data = await api.getVerseOfDay();
    card.innerHTML = `
      <div class="votd-date">${new Date(data.date + "T00:00:00").toDateString()}</div>
      <p class="votd-text">"${data.text.trim()}"</p>
      <div class="votd-ref">${data.reference} — ${data.translation}</div>
    `;
  } catch (err) {
    card.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}
document.addEventListener("DOMContentLoaded", loadVerseOfDay);

// ---- Bible study page ----
const loadedSessions = {}; // studyId -> sessions array, cached after first fetch
const openStudyId = { current: null };

async function loadStudies() {
  const list = document.getElementById("study-list");
  if (!list) return;
  try {
    const studies = await api.getBibleStudies();
    list.innerHTML = studies.map(s => `
      <div class="study-block">
        <div class="study-row" onclick="toggleStudy('${s.id}')">
          <div class="study-week">${String(s.week).padStart(2, "0")}</div>
          <div>
            <h3>${s.title}</h3>
            <span>${s.description}</span>
          </div>
          <div class="study-tag">${s.sessions} sessions</div>
        </div>
        <div class="study-sessions" id="sessions-${s.id}" style="display:none;"></div>
      </div>
    `).join("");
  } catch (err) {
    showError(err.message);
    list.innerHTML = "";
  }
}
document.addEventListener("DOMContentLoaded", loadStudies);

async function toggleStudy(studyId) {
  const panel = document.getElementById(`sessions-${studyId}`);
  if (!panel) return;

  if (openStudyId.current === studyId) {
    panel.style.display = "none";
    openStudyId.current = null;
    return;
  }
  if (openStudyId.current) {
    const prev = document.getElementById(`sessions-${openStudyId.current}`);
    if (prev) prev.style.display = "none";
  }
  openStudyId.current = studyId;
  panel.style.display = "block";

  if (loadedSessions[studyId]) return;

  panel.innerHTML = "<p style='padding:16px;'>Loading sessions...</p>";
  try {
    const sessions = await api.getStudySessions(studyId);
    loadedSessions[studyId] = sessions;
    panel.innerHTML = `
      <div class="group-section" id="group-section-${studyId}">
        <p style="font-size:13px; color:var(--plum-soft); margin-bottom:8px;">👯 Doing this with friends?</p>
        <div id="groups-list-${studyId}"><p style="font-size:13px;">Loading groups...</p></div>
        <button class="btn-secondary group-toggle-btn" onclick="showNewGroupForm('${studyId}')">+ Start a group</button>
        <div id="new-group-form-${studyId}"></div>
      </div>
      ${sessions.map(sess => `
        <div class="session-card">
          <div class="session-head">
            <span class="session-number">Session ${sess.session_number}</span>
            <h4>${sess.title}</h4>
          </div>
          <button class="btn-secondary read-scripture-btn" onclick="readScripture('${sess.id}', '${sess.scripture_ref.replace(/'/g, "\\'")}')">
            📖 Read ${sess.scripture_ref}
          </button>
          <div class="scripture-box" id="scripture-${sess.id}" style="display:none;"></div>
          <div class="session-questions">
            <p class="questions-label">Reflect on:</p>
            <ul>
              ${sess.questions.map(q => `<li>${q}</li>`).join("")}
            </ul>
          </div>
        </div>
      `).join("")}
    `;
    loadStudyGroups(studyId);
  } catch (err) {
    panel.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

async function readScripture(sessionId, ref) {
  const box = document.getElementById(`scripture-${sessionId}`);
  if (!box) return;

  if (box.style.display === "block" && box.dataset.loaded === "true") {
    box.style.display = "none";
    return;
  }

  box.style.display = "block";
  box.innerHTML = "<p>Loading passage...</p>";
  try {
    const data = await api.getScripture(ref);
    box.innerHTML = `
      <div class="scripture-ref">${data.reference} <span class="scripture-translation">(${data.translation})</span></div>
      <p class="scripture-text">${data.text.replace(/\n/g, " ").trim()}</p>
    `;
    box.dataset.loaded = "true";
  } catch (err) {
    box.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

// ---- Bible study groups ----
async function loadStudyGroups(studyId) {
  const box = document.getElementById(`groups-list-${studyId}`);
  if (!box) return;
  if (!auth.isLoggedIn()) {
    box.innerHTML = `<p style="font-size:13px; color:var(--plum-soft);">Sign in to study with friends.</p>`;
    return;
  }
  try {
    const groups = await api.getStudyGroups(studyId);
    const sessions = loadedSessions[studyId] || [];
    box.innerHTML = groups.length ? groups.map(g => `
      <div class="group-card">
        <h5>${g.name}</h5>
        <div class="group-members">
          ${g.members.map(m => `<span class="group-member-chip">@${m.handle}</span>`).join("")}
        </div>
        ${sessions.map(sess => {
          const completedBy = g.progress[sess.id] || [];
          const iCompleted = completedBy.includes(myUserId());
          return `
            <label class="group-session-check">
              <input type="checkbox" ${iCompleted ? "checked" : ""} onchange="toggleGroupSession('${g.id}', '${sess.id}', '${studyId}')" />
              Session ${sess.session_number} — ${completedBy.length}/${g.members.length} done
            </label>
          `;
        }).join("")}
      </div>
    `).join("") : `<p style="font-size:13px; color:var(--plum-soft);">No groups yet for this study.</p>`;
  } catch (err) {
    box.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

async function showNewGroupForm(studyId) {
  const box = document.getElementById(`new-group-form-${studyId}`);
  if (!box) return;
  if (box.innerHTML.trim()) {
    box.innerHTML = "";
    return;
  }
  if (!auth.isLoggedIn()) return showError("Sign in to start a group.");

  try {
    const friends = await api.getFriends();
    if (!friends.length) {
      box.innerHTML = `<p style="font-size:13px; color:var(--plum-soft); margin-top:8px;">Add some friends first on the Friends page.</p>`;
      return;
    }
    box.innerHTML = `
      <div class="new-group-form">
        <input type="text" id="group-name-${studyId}" placeholder="Group name (optional)" />
        <div class="new-group-friends">
          ${friends.map(f => `
            <label class="tag-friend-checkbox">
              <input type="checkbox" value="${f.handle}" class="group-member-input-${studyId}" /> @${f.handle}
            </label>
          `).join("")}
        </div>
        <button class="btn-primary" style="align-self:flex-start;" onclick="createGroup('${studyId}')">Create group</button>
      </div>
    `;
  } catch (err) {
    showError(err.message);
  }
}

async function createGroup(studyId) {
  const name = document.getElementById(`group-name-${studyId}`).value;
  const members = Array.from(document.querySelectorAll(`.group-member-input-${studyId}:checked`)).map(el => el.value);
  try {
    await api.createStudyGroup(studyId, { name, member_handles: members });
    document.getElementById(`new-group-form-${studyId}`).innerHTML = "";
    loadStudyGroups(studyId);
  } catch (err) {
    showError(err.message);
  }
}

async function toggleGroupSession(groupId, sessionId, studyId) {
  try {
    await api.toggleGroupSessionComplete(groupId, sessionId);
    loadStudyGroups(studyId);
  } catch (err) {
    showError(err.message);
  }
}

// ---- Mood Help emoji comfort feature ----
let moodEmojisCache = [];
let currentJournalMood = { emoji: "💭", label: "Reflecting" };

async function loadMoodEmojis() {
  const grid = document.getElementById("emoji-grid");
  if (!grid) return;
  try {
    moodEmojisCache = await api.getMoodEmojis();
    grid.innerHTML = moodEmojisCache.map(e => `
      <button class="emoji-btn" onclick="showMoodMessage('${e.id}')" title="${e.label}">
        <span class="emoji-icon">${e.emoji}</span>
        <span class="emoji-label">${e.label}</span>
      </button>
    `).join("");
  } catch (err) {
    grid.innerHTML = "";
    showError(err.message);
  }
}
document.addEventListener("DOMContentLoaded", loadMoodEmojis);

function showMoodMessage(emojiId) {
  const entry = moodEmojisCache.find(e => e.id === emojiId);
  const box = document.getElementById("emoji-message-box");
  if (!entry || !box) return;

  const message = entry.messages[Math.floor(Math.random() * entry.messages.length)];
  box.style.display = "block";
  box.innerHTML = `
    <div class="emoji-message-icon">${entry.emoji}</div>
    <div class="emoji-message-label">Feeling ${entry.label.toLowerCase()}?</div>
    <p class="emoji-message-text">${message}</p>
    ${entry.verses && entry.verses.length ? `
      <div class="emoji-verse-chips" id="verse-chips-${entry.id}">
        ${entry.verses.map((v, i) => `<span class="verse-chip" onclick="revealVerse('${entry.id}', '${v.replace(/'/g, "\\'")}', ${i})">📖 ${v}</span>`).join("")}
      </div>
      <div id="verse-reveal-${entry.id}"></div>
    ` : ""}
    <button class="report-link" onclick="showMoodMessage('${emojiId}')">Show me another</button>
    <br>
    <button class="report-link" style="margin-top:6px;" onclick="prefillJournal('${entry.emoji}', '${entry.label}')">Journal about this feeling</button>
  `;
  box.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function revealVerse(entryId, ref, index) {
  const target = document.getElementById(`verse-reveal-${entryId}`);
  if (!target) return;
  target.innerHTML = `<div class="verse-reveal">Loading...</div>`;
  try {
    const data = await api.getScripture(ref);
    target.innerHTML = `
      <div class="verse-reveal">
        <div class="scripture-ref">${data.reference} <span class="scripture-translation">(${data.translation})</span></div>
        <p class="scripture-text">${data.text.replace(/\n/g, " ").trim()}</p>
      </div>
    `;
  } catch (err) {
    target.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

function prefillJournal(emoji, label) {
  currentJournalMood = { emoji, label };
  const form = document.getElementById("journal-form");
  if (form) {
    form.style.display = "block";
    form.scrollIntoView({ behavior: "smooth", block: "center" });
    document.getElementById("journal-note").focus();
  }
}

// ---- Mood journal ----
async function loadJournal() {
  const entriesBox = document.getElementById("journal-entries");
  const form = document.getElementById("journal-form");
  const hint = document.getElementById("journal-signin-hint");
  if (!entriesBox) return;

  if (!auth.isLoggedIn()) {
    hint.innerHTML = `<div class="hint-box">Sign in to keep a private mood journal.</div>`;
    if (form) form.style.display = "none";
    entriesBox.innerHTML = "";
    return;
  }

  try {
    const entries = await api.getMoodJournal();
    entriesBox.innerHTML = entries.length ? entries.map(e => `
      <div class="journal-card">
        <div class="journal-card-head">
          <span class="journal-emoji-label">${e.emoji} ${e.label}</span>
          <span class="journal-date">${new Date(e.created_at).toLocaleString()}</span>
        </div>
        <p class="journal-note">${e.note}</p>
        <button class="report-link journal-delete" onclick="deleteJournalEntry('${e.id}')">Delete</button>
      </div>
    `).join("") : `<p class="sub">No journal entries yet — your first one will appear here.</p>`;
  } catch (err) {
    entriesBox.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

async function deleteJournalEntry(id) {
  if (!window.confirm("Delete this journal entry?")) return;
  try {
    await api.deleteMoodJournal(id);
    loadJournal();
  } catch (err) {
    showError(err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("journal-form");
  if (!form) return;
  if (auth.isLoggedIn()) form.style.display = "block";
  loadJournal();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const note = document.getElementById("journal-note").value;
    try {
      await api.postMoodJournal({ emoji: currentJournalMood.emoji, label: currentJournalMood.label, note });
      document.getElementById("journal-note").value = "";
      currentJournalMood = { emoji: "💭", label: "Reflecting" };
      loadJournal();
    } catch (err) {
      showError(err.message);
    }
  });
});

// ---- Prayer wall page ----
const prayingIds = new Set();

function renderPrayerCompose() {
  const area = document.getElementById("compose-area");
  if (!area || !document.getElementById("prayer-wall")) return;
  if (auth.isLoggedIn()) {
    area.innerHTML = `
      <form class="compose-box" id="prayer-form">
        <div class="field">
          <label>What's on your heart?</label>
          <textarea id="prayer-content" maxlength="800" placeholder="Share what you'd like prayer for..."></textarea>
        </div>
        <div class="actions">
          <label class="checkbox-row">
            <input type="checkbox" id="prayer-anon" checked />
            Post as anonymous (your display name stays hidden from other users)
          </label>
          <button class="btn-primary" type="submit">Share request</button>
        </div>
      </form>
    `;
    document.getElementById("prayer-form").addEventListener("submit", submitPrayer);
  } else {
    area.innerHTML = `<div class="hint-box">Sign in with your display name to post a prayer request.</div>`;
  }
}

async function submitPrayer(e) {
  e.preventDefault();
  const content = document.getElementById("prayer-content").value;
  const anonymous = document.getElementById("prayer-anon").checked;
  try {
    await api.postPrayer({ content, anonymous });
    document.getElementById("prayer-content").value = "";
    loadPrayerWall();
  } catch (err) {
    showError(err.message);
  }
}

async function prayFor(id) {
  if (!auth.isLoggedIn()) return showError("Sign in to pray over a post.");
  try {
    const res = await api.prayFor(id);
    res.praying ? prayingIds.add(id) : prayingIds.delete(id);
    loadPrayerWall();
  } catch (err) {
    showError(err.message);
  }
}

async function reportPost(id) {
  if (!auth.isLoggedIn()) return showError("Sign in to report a post.");
  const reason = window.prompt("What's going on with this post? (This goes to a moderator only.)");
  if (!reason) return;
  try {
    await api.report({ board: "prayerWall", post_id: id, reason });
  } catch (err) {
    showError(err.message);
  }
}

async function loadPrayerWall() {
  const wall = document.getElementById("prayer-wall");
  if (!wall) return;
  try {
    const posts = await api.getPrayerWall();
    wall.innerHTML = posts.map(p => `
      <div class="note">
        <p>"${p.content}"</p>
        <div>
          <div class="note-handle">— ${p.handle}</div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <button class="note-amen ${prayingIds.has(p.id) ? "active" : ""}" onclick="prayFor('${p.id}')">
              🕊 ${p.prayed_count} prayed
            </button>
            <button class="report-link" onclick="reportPost('${p.id}')">Report</button>
          </div>
        </div>
      </div>
    `).join("");
  } catch (err) {
    showError(err.message);
    wall.innerHTML = "";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("prayer-wall")) {
    renderPrayerCompose();
    loadPrayerWall();
  }
});

// ---- Gist page ----
const REACTION_ICONS = {
  thumbs_up: "👍",
  love: "❤️",
  sad: "😢",
  pray: "🙏",
  clap: "👏",
};

let gistFriendsCache = [];

async function renderGistCompose() {
  const area = document.getElementById("compose-area");
  if (!area || !document.getElementById("gist-feed")) return;
  if (auth.isLoggedIn()) {
    let friendCheckboxes = "";
    try {
      gistFriendsCache = await api.getFriends();
      if (gistFriendsCache.length) {
        friendCheckboxes = `
          <div class="field">
            <label>Tag friends (optional)</label>
            <div class="tag-friend-list">
              ${gistFriendsCache.map(f => `
                <label class="tag-friend-checkbox">
                  <input type="checkbox" value="${f.handle}" class="tag-friend-input" />
                  @${f.handle}
                </label>
              `).join("")}
            </div>
          </div>
        `;
      }
    } catch (err) {
      // if friends can't load, just skip tagging UI rather than blocking posting
    }

    area.innerHTML = `
      <form class="compose-box" id="gist-form">
        <div class="field">
          <textarea id="gist-content" maxlength="500" placeholder="What's on your mind?"></textarea>
        </div>
        ${friendCheckboxes}
        <div class="actions">
          <span></span>
          <button class="btn-primary" type="submit">Post</button>
        </div>
      </form>
    `;
    document.getElementById("gist-form").addEventListener("submit", submitGist);
  } else {
    area.innerHTML = `<div class="hint-box">Sign in with your display name to join the conversation.</div>`;
  }
}

async function submitGist(e) {
  e.preventDefault();
  const content = document.getElementById("gist-content").value;
  const tags = Array.from(document.querySelectorAll(".tag-friend-input:checked")).map(el => el.value);
  try {
    await api.postGist({ content, tags });
    document.getElementById("gist-content").value = "";
    loadGistFeed();
  } catch (err) {
    showError(err.message);
  }
}

async function reportMsg(id) {
  if (!auth.isLoggedIn()) return showError("Sign in to report a message.");
  const reason = window.prompt("What's going on with this message? (This goes to a moderator only.)");
  if (!reason) return;
  try {
    await api.report({ board: "gist", post_id: id, reason });
  } catch (err) {
    showError(err.message);
  }
}

async function reactToMessage(id, reaction) {
  if (!auth.isLoggedIn()) return showError("Sign in to react to a message.");
  try {
    await api.reactToGist(id, reaction);
    loadGistFeed();
  } catch (err) {
    showError(err.message);
  }
}

async function loadGistFeed() {
  const feed = document.getElementById("gist-feed");
  if (!feed) return;
  try {
    const messages = await api.getGist();
    const myHandle = auth.getHandle();
    feed.innerHTML = messages.map(m => `
      <div class="gist-msg ${m.handle === myHandle ? "mine" : ""}">
        <div class="gist-handle">${m.handle}</div>
        <p>${m.content}</p>
        ${m.tags && m.tags.length ? `<div class="gist-tags">with ${m.tags.map(t => `@${t}`).join(", ")}</div>` : ""}
        <div class="gist-reactions">
          ${Object.entries(REACTION_ICONS).map(([key, icon]) => `
            <button
              class="reaction-btn ${m.my_reaction === key ? "active" : ""}"
              onclick="reactToMessage('${m.id}', '${key}')"
              title="${key.replace('_', ' ')}"
            >
              ${icon}${m.reactions[key] > 0 ? ` ${m.reactions[key]}` : ""}
            </button>
          `).join("")}
        </div>
        <div class="gist-time">
          ${new Date(m.created_at).toLocaleString()} ·
          <button class="report-link" onclick="reportMsg('${m.id}')">Report</button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    showError(err.message);
    feed.innerHTML = "";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("gist-feed")) {
    renderGistCompose();
    loadGistFeed();
  }
});

// ---- Friends page ----
document.addEventListener("DOMContentLoaded", () => {
  if (!document.getElementById("friends-list")) return;

  if (!auth.isLoggedIn()) {
    document.getElementById("friends-content").style.display = "none";
    document.getElementById("not-logged-in").style.display = "block";
    return;
  }

  loadFriendRequests();
  loadFriendsList();

  document.getElementById("add-friend-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("add-friend-handle");
    const errBox = document.getElementById("add-friend-error");
    const okBox = document.getElementById("add-friend-success");
    errBox.innerHTML = "";
    okBox.innerHTML = "";
    try {
      const result = await api.sendFriendRequest(input.value.trim());
      okBox.innerHTML = `<div class="success-msg">${result.message}</div>`;
      input.value = "";
    } catch (err) {
      errBox.innerHTML = `<div class="error-msg">${err.message}</div>`;
    }
  });
});

async function loadFriendRequests() {
  const box = document.getElementById("friend-requests");
  if (!box) return;
  try {
    const requests = await api.getFriendRequests();
    box.innerHTML = requests.length ? requests.map(r => `
      <div class="friend-request-row">
        <span>@${r.handle} wants to be friends</span>
        <div class="friend-request-actions">
          <button class="btn-primary" style="padding:8px 16px;font-size:13px;" onclick="respondToRequest('${r.id}', true)">Accept</button>
          <button class="btn-secondary" style="padding:8px 16px;font-size:13px;" onclick="respondToRequest('${r.id}', false)">Decline</button>
        </div>
      </div>
    `).join("") : "<p class='sub'>No pending requests.</p>";
  } catch (err) {
    box.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

async function respondToRequest(id, accept) {
  try {
    if (accept) await api.acceptFriendRequest(id);
    else await api.declineFriendRequest(id);
    loadFriendRequests();
    loadFriendsList();
  } catch (err) {
    showError(err.message);
  }
}

async function loadFriendsList() {
  const list = document.getElementById("friends-list");
  if (!list) return;
  try {
    const friends = await api.getFriends();
    list.innerHTML = friends.length ? friends.map(f => `
      <div class="friend-row">
        <span>@${f.handle}</span>
        <button class="report-link" onclick="removeFriendConfirm('${f.user_id}', '${f.handle}')">Remove</button>
      </div>
    `).join("") : "<p class='sub'>No friends yet — add someone by their display name above.</p>";
  } catch (err) {
    list.innerHTML = `<div class="error-msg">${err.message}</div>`;
  }
}

async function removeFriendConfirm(userId, handle) {
  if (!window.confirm(`Remove @${handle} from your friends?`)) return;
  try {
    await api.removeFriend(userId);
    loadFriendsList();
  } catch (err) {
    showError(err.message);
  }
}

// ---- Signup page ----
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signup-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "Creating account...";
    try {
      const data = await api.signup({
        handle: document.getElementById("handle").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      });
      auth.setSession(data.token, data.handle);
      window.location.href = "index.html";
    } catch (err) {
      showError(err.message);
      btn.disabled = false;
      btn.textContent = "Create account";
    }
  });
});

// ---- Login page ----
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "Signing in...";
    try {
      const data = await api.login({
        identifier: document.getElementById("identifier").value,
        password: document.getElementById("password").value,
      });
      auth.setSession(data.token, data.handle);
      window.location.href = "index.html";
    } catch (err) {
      showError(err.message);
      btn.disabled = false;
      btn.textContent = "Sign in";
    }
  });
});

// ---- Forgot password page (two steps: request code, then reset) ----
document.addEventListener("DOMContentLoaded", () => {
  const requestForm = document.getElementById("request-code-form");
  const resetForm = document.getElementById("reset-form");
  if (!requestForm || !resetForm) return;

  requestForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("request-code-btn");
    btn.disabled = true;
    btn.textContent = "Sending...";
    try {
      const email = document.getElementById("forgot-email").value;
      await api.forgotPassword({ email });
      document.getElementById("reset-email").value = email;
      document.getElementById("step-1").style.display = "none";
      document.getElementById("step-2").style.display = "block";
    } catch (err) {
      showError(err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "Send reset code";
    }
  });

  resetForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("reset-btn");
    btn.disabled = true;
    btn.textContent = "Resetting...";
    try {
      await api.resetPassword({
        email: document.getElementById("reset-email").value,
        code: document.getElementById("reset-code").value,
        new_password: document.getElementById("reset-new-password").value,
      });
      window.location.href = "login.html";
    } catch (err) {
      showError(err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = "Reset password";
    }
  });
});
