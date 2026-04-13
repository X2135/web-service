const API_BASE_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "habit_api_token";

const loginForm = document.getElementById("loginForm");
const categoryForm = document.getElementById("categoryForm");
const recordForm = document.getElementById("recordForm");
const loginStatus = document.getElementById("loginStatus");
const categoriesList = document.getElementById("categoriesList");
const recordsList = document.getElementById("recordsList");
const summaryCards = document.getElementById("summaryCards");
const debugPanel = document.getElementById("debugPanel");
const categoryCount = document.getElementById("categoryCount");
const recordCount = document.getElementById("recordCount");
const kpiCategories = document.getElementById("kpiCategories");
const kpiRecords = document.getElementById("kpiRecords");
const kpiAuth = document.getElementById("kpiAuth");
const logoutBtn = document.getElementById("logoutBtn");

let authToken = localStorage.getItem(TOKEN_KEY) || "";

function setLoginStatus(message, type = "neutral") {
  loginStatus.textContent = message;
  loginStatus.className = `status-message ${type}`;
  kpiAuth.textContent = authToken ? "Authenticated" : "Guest";
}

function writeDebug(title, payload) {
  const body = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  debugPanel.textContent = `[${new Date().toLocaleTimeString()}] ${title}\n${body}`;
}

async function apiRequest(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  let data;
  try {
    data = await response.json();
  } catch {
    data = { message: "No JSON response" };
  }

  writeDebug(`${options.method || "GET"} ${path} -> ${response.status}`, data);

  if (!response.ok) {
    const error = new Error(data.detail || "Request failed");
    error.status = response.status;
    error.payload = data;
    throw error;
  }

  return data;
}

function renderCategories(categories) {
  categoryCount.textContent = String(categories.length);
  kpiCategories.textContent = String(categories.length);

  if (!categories.length) {
    categoriesList.innerHTML = "<p>No categories found.</p>";
    return;
  }

  categoriesList.innerHTML = categories
    .map(
      (item) => `
      <div class="item-card">
        <strong>#${item.id} - ${item.name}</strong>
        <div class="meta-line"><span class="tag">Category</span>${item.description || "No description"}</div>
      </div>
    `
    )
    .join("");
}

function renderRecords(records) {
  recordCount.textContent = String(records.length);
  kpiRecords.textContent = String(records.length);

  if (!records.length) {
    recordsList.innerHTML = "<p>No records found.</p>";
    return;
  }

  recordsList.innerHTML = records
    .map(
      (item) => `
      <div class="item-card">
        <strong>#${item.id} - ${item.habit_name}</strong>
        <div class="meta-line"><span class="tag">Date</span>${item.record_date}</div>
        <div class="meta-line"><span class="tag">Category ID</span>${item.category_id}</div>
        <div class="meta-line"><span class="tag ${item.completed ? "success" : "error"}">${item.completed ? "Completed" : "Not Completed"}</span></div>
        <div class="meta-line"><span class="tag">Duration</span>${item.duration_minutes ?? "N/A"} min</div>
        <div class="meta-line"><span class="tag">Notes</span>${item.notes || "-"}</div>
      </div>
    `
    )
    .join("");
}

function renderSummary(summary) {
  const cards = [
    { key: "Total Entries", value: summary.total_entries ?? "-" },
    { key: "Summary Note", value: summary.note ?? "Ready for extension" },
    { key: "Auth Status", value: authToken ? "Logged in" : "Guest" },
    { key: "API Base URL", value: API_BASE_URL },
  ];

  summaryCards.innerHTML = cards
    .map(
      (item) => `
      <div class="summary-card">
        <div class="k">${item.key}</div>
        <div class="v">${item.value}</div>
      </div>
    `
    )
    .join("");
}

async function loadCategories() {
  try {
    const data = await apiRequest("/habits/categories");
    renderCategories(data);
  } catch (error) {
    renderCategories([]);
    writeDebug("GET /habits/categories failed", error.payload || error.message);
  }
}

async function loadRecords() {
  try {
    const data = await apiRequest("/habits/records?limit=50");
    renderRecords(data);
  } catch (error) {
    renderRecords([]);
    writeDebug("GET /habits/records failed", error.payload || error.message);
  }
}

async function loadSummary() {
  try {
    const data = await apiRequest("/analytics/summary");
    renderSummary(data);
  } catch (error) {
    renderSummary({});
    writeDebug("GET /analytics/summary failed", error.payload || error.message);
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  try {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    authToken = data.access_token;
    localStorage.setItem(TOKEN_KEY, authToken);
    setLoginStatus(`Logged in as ${username}`, "success");
    await Promise.all([loadCategories(), loadRecords(), loadSummary()]);
  } catch (error) {
    setLoginStatus(`Login failed: ${error.message}`, "error");
  }
});

categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = document.getElementById("categoryName").value.trim();
  const description = document.getElementById("categoryDescription").value.trim();

  try {
    await apiRequest("/habits/categories", {
      method: "POST",
      body: JSON.stringify({ name, description: description || null }),
    });
    categoryForm.reset();
    await loadCategories();
    setLoginStatus("Category created successfully.", "success");
  } catch (error) {
    const message = error.status === 401 ? "Please login first." : error.message;
    setLoginStatus(`Create category failed: ${message}`, "error");
  }
});

recordForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const recordDate = document.getElementById("recordDate").value;
  const habitName = document.getElementById("habitName").value.trim();
  const categoryId = Number(document.getElementById("categoryId").value);
  const completed = document.getElementById("completed").value === "true";
  const durationValue = document.getElementById("durationMinutes").value;
  const notes = document.getElementById("recordNotes").value.trim();

  const payload = {
    record_date: recordDate,
    habit_name: habitName,
    category_id: categoryId,
    completed,
    duration_minutes: durationValue === "" ? null : Number(durationValue),
    notes: notes || null,
  };

  try {
    await apiRequest("/habits/records", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    recordForm.reset();
    await Promise.all([loadRecords(), loadSummary()]);
    setLoginStatus("Record created successfully.", "success");
  } catch (error) {
    const message = error.status === 401 ? "Please login first." : error.message;
    setLoginStatus(`Create record failed: ${message}`, "error");
  }
});

document.getElementById("refreshCategories").addEventListener("click", loadCategories);
document.getElementById("refreshRecords").addEventListener("click", loadRecords);
document.getElementById("refreshSummary").addEventListener("click", loadSummary);

function init() {
  if (authToken) {
    setLoginStatus("Token loaded from localStorage. Authenticated session ready.", "success");
  } else {
    setLoginStatus("Not logged in", "neutral");
  }

  loadCategories();
  loadRecords();
  loadSummary();
}

logoutBtn.addEventListener("click", () => {
  authToken = "";
  localStorage.removeItem(TOKEN_KEY);
  setLoginStatus("Logged out. Token cleared.", "neutral");
  writeDebug("Auth", { message: "Logged out" });
});

init();
