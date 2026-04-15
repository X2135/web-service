const API_BASE_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "habit_api_token";

const state = {
  token: localStorage.getItem(TOKEN_KEY) || "",
  categories: [],
  records: [],
  username: "demo",
};

const elements = {
  backendUrl: document.getElementById("backendUrl"),
  apiStatus: document.getElementById("apiStatus"),
  authStatus: document.getElementById("authStatus"),
  summaryAuth: document.getElementById("summaryAuth"),
  globalMessage: document.getElementById("globalMessage"),
  debugPanel: document.getElementById("debugPanel"),
  loginStatus: document.getElementById("loginStatus"),

  totalCategories: document.getElementById("totalCategories"),
  totalRecords: document.getElementById("totalRecords"),
  completedRecords: document.getElementById("completedRecords"),
  analyticsTotal: document.getElementById("analyticsTotal"),
  analyticsCompleted: document.getElementById("analyticsCompleted"),
  analyticsRate: document.getElementById("analyticsRate"),

  categoryCount: document.getElementById("categoryCount"),
  categoriesList: document.getElementById("categoriesList"),
  recordCount: document.getElementById("recordCount"),
  recordsBody: document.getElementById("recordsBody"),

  loginForm: document.getElementById("loginForm"),
  categoryForm: document.getElementById("categoryForm"),
  recordForm: document.getElementById("recordForm"),
  findCategoryForm: document.getElementById("findCategoryForm"),
  findRecordForm: document.getElementById("findRecordForm"),

  refreshCategories: document.getElementById("refreshCategories"),
  refreshRecords: document.getElementById("refreshRecords"),
  refreshSummary: document.getElementById("refreshSummary"),
  refreshDataBtn: document.getElementById("refreshDataBtn"),
  testProtectedBtn: document.getElementById("testProtectedBtn"),
  triggerErrorBtn: document.getElementById("triggerErrorBtn"),
  clearDebugBtn: document.getElementById("clearDebugBtn"),
  logoutBtn: document.getElementById("logoutBtn"),
};

elements.backendUrl.textContent = API_BASE_URL;

function now() {
  return new Date().toLocaleTimeString();
}

function setApiStatus(type, text) {
  elements.apiStatus.className = `pill ${type}`;
  elements.apiStatus.textContent = text;
}

function setAuthStatus() {
  const loggedIn = Boolean(state.token);
  elements.authStatus.className = `pill ${loggedIn ? "success" : "neutral"}`;
  elements.authStatus.textContent = loggedIn ? "Logged in" : "Not logged in";
  elements.summaryAuth.textContent = loggedIn ? "Logged in" : "Guest";
  elements.loginStatus.textContent = loggedIn
    ? `Authenticated session active (${state.username})`
    : "Not logged in";
}

function showMessage(type, text) {
  elements.globalMessage.className = `global-message ${type}`;
  elements.globalMessage.textContent = text;
  setTimeout(() => {
    elements.globalMessage.className = "global-message hidden";
  }, 3200);
}

function appendDebug(method, path, statusCode, payload) {
  const body = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
  const entry = `[${now()}] ${method} ${path} -> ${statusCode}\n${body}\n${"-".repeat(58)}\n`;
  elements.debugPanel.textContent = entry + elements.debugPanel.textContent;
}

async function apiRequest(path, { method = "GET", body = null, auth = false } = {}) {
  if (auth && !state.token) {
    const payload = { detail: "Not authenticated" };
    appendDebug(method, path, 401, payload);
    throw Object.assign(new Error("Not authenticated"), { status: 401, payload });
  }

  const headers = { "Content-Type": "application/json" };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    let data = null;
    try {
      data = await response.json();
    } catch {
      data = { detail: "No JSON response" };
    }

    setApiStatus("success", "Online");
    appendDebug(method, path, response.status, data);

    if (!response.ok) {
      throw Object.assign(new Error(data.detail || "Request failed"), {
        status: response.status,
        payload: data,
      });
    }

    return data;
  } catch (error) {
    if (!error.status) {
      setApiStatus("error", "Offline");
      appendDebug(method, path, "NETWORK_ERROR", { detail: error.message });
      throw Object.assign(new Error("API is offline or unreachable"), { status: 0, payload: null });
    }
    throw error;
  }
}

function categoryNameById(id) {
  const match = state.categories.find((item) => item.id === id);
  return match ? match.name : `ID ${id}`;
}

function renderCategories() {
  const data = state.categories;
  elements.totalCategories.textContent = String(data.length);
  elements.categoryCount.textContent = String(data.length);

  if (!data.length) {
    elements.categoriesList.innerHTML = '<p class="meta-line">No categories available.</p>';
    return;
  }

  elements.categoriesList.innerHTML = data
    .map(
      (item) => `
      <div class="item-card">
        <div class="item-title">#${item.id} - ${item.name}</div>
        <div class="meta-line">${item.description || "No description"}</div>
      </div>
    `
    )
    .join("");
}

function renderRecords() {
  const records = state.records;
  const completedCount = records.filter((item) => item.completed).length;

  elements.totalRecords.textContent = String(records.length);
  elements.completedRecords.textContent = String(completedCount);
  elements.recordCount.textContent = String(records.length);
  elements.analyticsTotal.textContent = String(records.length);
  elements.analyticsCompleted.textContent = String(completedCount);

  const rate = records.length ? ((completedCount / records.length) * 100).toFixed(1) : "0.0";
  elements.analyticsRate.textContent = `${rate}%`;

  if (!records.length) {
    elements.recordsBody.innerHTML = '<tr><td colspan="7">No records available.</td></tr>';
    return;
  }

  elements.recordsBody.innerHTML = records
    .map((item) => {
      const badgeClass = item.completed ? "chip success" : "chip error";
      const badgeText = item.completed ? "Completed" : "Not Completed";
      return `
        <tr>
          <td>${item.id}</td>
          <td>${item.record_date}</td>
          <td>${item.habit_name}</td>
          <td>${categoryNameById(item.category_id)}</td>
          <td><span class="${badgeClass}">${badgeText}</span></td>
          <td>${item.duration_minutes ?? "-"}</td>
          <td>${item.notes || "-"}</td>
        </tr>
      `;
    })
    .join("");
}

async function refreshCategories() {
  state.categories = await apiRequest("/habits/categories");
  renderCategories();
}

async function refreshRecords() {
  state.records = await apiRequest("/habits/records?limit=200");
  renderRecords();
}

function refreshAnalytics() {
  renderRecords();
}

async function refreshAllData() {
  await Promise.all([refreshCategories(), refreshRecords()]);
  refreshAnalytics();
}

async function checkApiHealth() {
  try {
    await apiRequest("/");
    setApiStatus("success", "Online");
  } catch {
    setApiStatus("error", "Offline");
  }
}

elements.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  try {
    const result = await apiRequest("/auth/login", {
      method: "POST",
      body: { username, password },
    });

    state.username = username;
    state.token = result.access_token;
    localStorage.setItem(TOKEN_KEY, state.token);
    setAuthStatus();
    showMessage("success", "Login successful. Protected endpoints are now unlocked.");
  } catch (error) {
    showMessage("error", `Login failed: ${error.message}`);
  }
});

elements.logoutBtn.addEventListener("click", () => {
  state.token = "";
  localStorage.removeItem(TOKEN_KEY);
  setAuthStatus();
  showMessage("warning", "Logged out. Protected operations now require login.");
  appendDebug("AUTH", "logout", 200, { detail: "Token cleared from local storage" });
});

elements.categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = document.getElementById("categoryName").value.trim();
  const description = document.getElementById("categoryDescription").value.trim();

  try {
    await apiRequest("/habits/categories", {
      method: "POST",
      body: { name, description: description || null },
      auth: true,
    });
    elements.categoryForm.reset();
    await refreshCategories();
    showMessage("success", "Category created successfully.");
  } catch (error) {
    showMessage("error", `Create category failed: ${error.message}`);
  }
});

elements.findCategoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = Number(document.getElementById("findCategoryId").value);

  try {
    const category = await apiRequest(`/habits/categories/${id}`);
    showMessage("success", `Category found: ${category.name}`);
  } catch (error) {
    showMessage("error", `Find category failed: ${error.message}`);
  }
});

elements.recordForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    record_date: document.getElementById("recordDate").value,
    habit_name: document.getElementById("habitName").value.trim(),
    category_id: Number(document.getElementById("categoryId").value),
    completed: document.getElementById("completed").value === "true",
    duration_minutes: document.getElementById("durationMinutes").value
      ? Number(document.getElementById("durationMinutes").value)
      : null,
    notes: document.getElementById("recordNotes").value.trim() || null,
  };

  try {
    await apiRequest("/habits/records", {
      method: "POST",
      body: payload,
      auth: true,
    });
    elements.recordForm.reset();
    await refreshRecords();
    showMessage("success", "Record created successfully.");
  } catch (error) {
    showMessage("error", `Create record failed: ${error.message}`);
  }
});

elements.findRecordForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = Number(document.getElementById("findRecordId").value);

  try {
    const record = await apiRequest(`/habits/records/${id}`);
    showMessage("success", `Record found: #${record.id} ${record.habit_name}`);
  } catch (error) {
    showMessage("error", `Find record failed: ${error.message}`);
  }
});

elements.refreshCategories.addEventListener("click", async () => {
  try {
    await refreshCategories();
    showMessage("success", "Categories refreshed.");
  } catch (error) {
    showMessage("error", `Refresh categories failed: ${error.message}`);
  }
});

elements.refreshRecords.addEventListener("click", async () => {
  try {
    await refreshRecords();
    showMessage("success", "Records refreshed.");
  } catch (error) {
    showMessage("error", `Refresh records failed: ${error.message}`);
  }
});

elements.refreshSummary.addEventListener("click", () => {
  refreshAnalytics();
  showMessage("success", "Analytics summary recalculated.");
});

elements.refreshDataBtn.addEventListener("click", async () => {
  try {
    await refreshAllData();
    showMessage("success", "Data refreshed successfully.");
  } catch (error) {
    showMessage("error", `Refresh data failed: ${error.message}`);
  }
});

elements.testProtectedBtn.addEventListener("click", async () => {
  try {
    await apiRequest("/habits/categories", {
      method: "POST",
      body: {
        name: `Demo_${Date.now()}`,
        description: "Generated by protected request test",
      },
      auth: true,
    });
    await refreshCategories();
    showMessage("success", "Protected request test succeeded.");
  } catch (error) {
    showMessage("error", `Protected request failed: ${error.message}`);
  }
});

elements.triggerErrorBtn.addEventListener("click", async () => {
  try {
    if (state.token) {
      await apiRequest("/habits/records", {
        method: "POST",
        body: {
          record_date: "2024-06-10",
          habit_name: "Error Demo",
          category_id: 999999,
          completed: true,
          duration_minutes: 15,
          notes: "Invalid category demo",
        },
        auth: true,
      });
    } else {
      await apiRequest("/habits/categories", {
        method: "POST",
        body: { name: "UnauthorizedDemo", description: "Should fail" },
        auth: true,
      });
    }
  } catch (error) {
    showMessage("warning", `Error demo triggered: ${error.status || "ERR"} ${error.message}`);
  }
});

elements.clearDebugBtn.addEventListener("click", () => {
  elements.debugPanel.textContent = "No requests yet.";
});

async function init() {
  setAuthStatus();
  await checkApiHealth();

  try {
    await refreshAllData();
  } catch (error) {
    showMessage("error", `Initial load failed: ${error.message}`);
  }
}

init();
