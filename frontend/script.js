const API_BASE_URL = window.location.search.includes("local=1")
  ? "http://127.0.0.1:8000"
  : "https://web-service-1-iox1.onrender.com";

const TOKEN_KEY = "habit_api_token";

const state = {
  token: localStorage.getItem(TOKEN_KEY) || "",
  analytics: null,
  username: "demo",
  lastDemoCategoryId: null,
  lastDemoRecordId: null,
};

const elements = {
  backendUrl: document.getElementById("backendUrl"),
  apiStatus: document.getElementById("apiStatus"),
  authStatus: document.getElementById("authStatus"),
  globalMessage: document.getElementById("globalMessage"),
  loginStatus: document.getElementById("loginStatus"),

  totalRecords: document.getElementById("totalRecords"),
  completedRecords: document.getElementById("completedRecords"),
  summaryRate: document.getElementById("summaryRate"),
  summaryAverage: document.getElementById("summaryAverage"),

  analyticsCategoryList: document.getElementById("analyticsCategoryList"),
  analyticsTrendList: document.getElementById("analyticsTrendList"),

  demoLoginBtn: document.getElementById("demoLoginBtn"),
  createDemoCategoryBtn: document.getElementById("createDemoCategoryBtn"),
  createDemoRecordBtn: document.getElementById("createDemoRecordBtn"),
  refreshInsightsBtn: document.getElementById("refreshInsightsBtn"),
  deleteDemoRecordBtn: document.getElementById("deleteDemoRecordBtn"),
  deleteDemoCategoryBtn: document.getElementById("deleteDemoCategoryBtn"),
};

elements.backendUrl.textContent = API_BASE_URL;

function setApiStatus(type, text) {
  elements.apiStatus.className = `pill ${type}`;
  elements.apiStatus.textContent = text;
}

function setAuthStatus() {
  const loggedIn = Boolean(state.token);
  elements.authStatus.className = `pill ${loggedIn ? "success" : "neutral"}`;
  elements.authStatus.textContent = loggedIn ? "Authenticated" : "Not authenticated";
  elements.loginStatus.textContent = loggedIn
    ? `Session active: ${state.username}`
    : "No active session";
}

function showMessage(type, text) {
  elements.globalMessage.className = `global-message ${type}`;
  elements.globalMessage.textContent = text;
  setTimeout(() => {
    elements.globalMessage.className = "global-message hidden";
  }, 2800);
}

async function apiRequest(path, { method = "GET", body = null, auth = false } = {}) {
  if (auth && !state.token) {
    throw Object.assign(new Error("Please authenticate first."), { status: 401 });
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
      data = null;
    }

    setApiStatus("success", "Online");

    if (!response.ok) {
      throw Object.assign(new Error(data?.detail || "Request failed"), {
        status: response.status,
        payload: data,
      });
    }

    return data;
  } catch (error) {
    if (!error.status) {
      setApiStatus("error", "Offline");
      throw new Error("Service is offline or unreachable.");
    }
    throw error;
  }
}

function renderSummary(analytics) {
  const total = Number(analytics?.total_records || 0);
  const completed = Number(analytics?.completed_records || 0);
  const rate = Number(analytics?.completion_rate || 0);
  const average = Number(analytics?.average_duration || 0);

  elements.totalRecords.textContent = String(total);
  elements.completedRecords.textContent = String(completed);
  elements.summaryRate.textContent = `${rate.toFixed(2)}%`;
  elements.summaryAverage.textContent = `${average.toFixed(2)} min`;
}

function renderInsights(analytics) {
  const categoryRows = Array.isArray(analytics?.records_per_category)
    ? analytics.records_per_category.slice(0, 5)
    : [];
  const trendRows = Array.isArray(analytics?.daily_trend)
    ? analytics.daily_trend.slice(-5)
    : [];

  if (!categoryRows.length) {
    elements.analyticsCategoryList.innerHTML = '<p class="meta-line">No category insight available.</p>';
  } else {
    elements.analyticsCategoryList.innerHTML = categoryRows
      .map(
        (item) => `
          <div class="insight-row">
            <span class="name">${item.category_name}</span>
            <span class="value">${item.count}</span>
          </div>
        `
      )
      .join("");
  }

  if (!trendRows.length) {
    elements.analyticsTrendList.innerHTML = '<p class="meta-line">No trend insight available.</p>';
  } else {
    elements.analyticsTrendList.innerHTML = trendRows
      .map(
        (item) => `
          <div class="insight-row">
            <span class="name">${item.record_date}</span>
            <span class="value">${item.completed}/${item.total}</span>
          </div>
        `
      )
      .join("");
  }
}

async function refreshInsights() {
  const analytics = await apiRequest("/analytics/summary");
  state.analytics = analytics;
  renderSummary(analytics);
  renderInsights(analytics);
}

async function checkApiHealth() {
  try {
    await apiRequest("/");
    setApiStatus("success", "Online");
  } catch {
    setApiStatus("error", "Offline");
  }
}

async function loginWithDemoAccount() {
  const result = await apiRequest("/auth/login", {
    method: "POST",
    body: { username: "demo", password: "demo123" },
  });

  state.username = "demo";
  state.token = result.access_token;
  localStorage.setItem(TOKEN_KEY, state.token);
  setAuthStatus();
}

async function createDemoCategory() {
  const created = await apiRequest("/habits/categories", {
    method: "POST",
    body: {
      name: "Demo Category",
      description: "Auto-created for demo",
    },
    auth: true,
  });
  state.lastDemoCategoryId = created?.id ?? null;
  return created;
}

async function createDemoRecord() {
  const created = await apiRequest("/habits/records", {
    method: "POST",
    body: {
      record_date: new Date().toISOString().slice(0, 10),
      habit_name: "Demo Habit",
      category_id: 1,
      completed: true,
      duration_minutes: 30,
    },
    auth: true,
  });
  state.lastDemoRecordId = created?.id ?? null;
  return created;
}

async function resolveLatestDemoRecordId() {
  const records = await apiRequest("/habits/records?limit=200");
  const demoRecords = (Array.isArray(records) ? records : []).filter((item) => item.habit_name === "Demo Habit");
  if (!demoRecords.length) {
    return null;
  }
  return demoRecords.reduce((maxId, item) => (item.id > maxId ? item.id : maxId), demoRecords[0].id);
}

async function resolveLatestDemoCategoryId() {
  const categories = await apiRequest("/habits/categories?limit=200");
  const demoCategories = (Array.isArray(categories) ? categories : []).filter(
    (item) => item.name === "Demo Category"
  );
  if (!demoCategories.length) {
    return null;
  }
  return demoCategories.reduce((maxId, item) => (item.id > maxId ? item.id : maxId), demoCategories[0].id);
}

async function deleteDemoRecord() {
  const recordId = state.lastDemoRecordId ?? (await resolveLatestDemoRecordId());
  if (!recordId) {
    throw new Error("No Demo Habit record found.");
  }

  await apiRequest(`/habits/records/${recordId}`, {
    method: "DELETE",
    auth: true,
  });
  state.lastDemoRecordId = null;
}

async function deleteDemoCategory() {
  const categoryId = state.lastDemoCategoryId ?? (await resolveLatestDemoCategoryId());
  if (!categoryId) {
    throw new Error("No Demo Category found.");
  }

  await apiRequest(`/habits/categories/${categoryId}`, {
    method: "DELETE",
    auth: true,
  });
  state.lastDemoCategoryId = null;
}

elements.demoLoginBtn.addEventListener("click", async () => {
  try {
    await loginWithDemoAccount();
    showMessage("success", "Authentication successful.");
  } catch (error) {
    showMessage("error", `Authentication failed: ${error.message}`);
  }
});

elements.createDemoCategoryBtn.addEventListener("click", async () => {
  try {
    await createDemoCategory();
    await refreshInsights();
    showMessage("success", "Category created and analytics refreshed.");
  } catch (error) {
    showMessage("error", `Category creation failed: ${error.message}`);
  }
});

elements.createDemoRecordBtn.addEventListener("click", async () => {
  try {
    await createDemoRecord();
    await refreshInsights();
    showMessage("success", "Record created and analytics refreshed.");
  } catch (error) {
    showMessage("error", `Record creation failed: ${error.message}`);
  }
});

elements.refreshInsightsBtn.addEventListener("click", async () => {
  try {
    await refreshInsights();
    showMessage("success", "Analytics refreshed.");
  } catch (error) {
    showMessage("error", `Analytics refresh failed: ${error.message}`);
  }
});

elements.deleteDemoRecordBtn.addEventListener("click", async () => {
  try {
    await deleteDemoRecord();
    await refreshInsights();
    showMessage("success", "Demo record deleted and analytics refreshed.");
  } catch (error) {
    showMessage("error", `Record deletion failed: ${error.message}`);
  }
});

elements.deleteDemoCategoryBtn.addEventListener("click", async () => {
  try {
    await deleteDemoCategory();
    await refreshInsights();
    showMessage("success", "Demo category deleted and analytics refreshed.");
  } catch (error) {
    showMessage("error", `Category deletion failed: ${error.message}`);
  }
});

async function init() {
  setAuthStatus();
  await checkApiHealth();

  try {
    await refreshInsights();
  } catch {
    renderSummary(null);
    renderInsights(null);
  }
}

init();
