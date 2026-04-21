// ================================
// GLOBAL STATE
// ================================
let currentLang = "en";
let I18N = {};

// ================================
// TOAST POPUP
// ================================
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerText = message;

  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 100);
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ================================
// LOAD LANGUAGE JSON FROM BACKEND
// ================================
async function loadLanguage(lang) {
  try {
    const res = await fetch(`/api/ui-language/${lang}`);
    I18N = await res.json();
    applyLanguage();
    currentLang = lang;
  } catch (err) {
    console.error("Language load failed", err);
  }
}

// ================================
// APPLY LANGUAGE TO UI
// ================================
function applyLanguage() {
  const t = I18N;

  document.querySelector(".logo span").innerText = t.app_name;
  document.querySelector(".nav-btn").innerText = "📜 " + t.history;

  document.getElementById("level").options[0].text = t.level_basic;
  document.getElementById("level").options[1].text = t.level_intermediate;
  document.getElementById("level").options[2].text = t.level_professional;

  document.querySelector(".user-chip button").innerText = t.logout;

  document.querySelector(".hero").innerHTML = `
    ${t.hero_title}<br><span>${t.hero_subtitle}</span>
  `;

  document.querySelector(".tagline").innerText = t.tagline;

  document.getElementById("query").placeholder = t.search_placeholder;

  document.querySelector(".ai-btn").innerText = t.generate_btn;

  document.getElementById("output").innerText = t.output_placeholder;

  document.querySelector(".json-toggle button").innerText = t.view_json;

  document.querySelector("#historyModal h2").innerText = t.history_title;

  document.querySelector("#historyModal button").innerText = t.close;
}

// ================================
// CHECK LOGIN ON LOAD
// ================================
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/api/check-login", { credentials: "include" });
    const data = await res.json();

    if (!data.logged_in) {
      window.location.href = "/signin";
      return;
    }

    document.getElementById("username").innerText = data.username;

    // default language
    const lang = document.getElementById("languageSelect").value;
    await loadLanguage(lang);

    showToast("Login successful 🎉");

  } catch (err) {
    console.error("Login check failed:", err);
  }
});

// ================================
// LANGUAGE DROPDOWN CHANGE
// ================================
document.getElementById("languageSelect").addEventListener("change", (e) => {
  loadLanguage(e.target.value);
});

// ================================
// GENERATE AI RESPONSE
// ================================
async function generateExplanation() {
  const term = document.getElementById("query").value.trim();
  const level = document.getElementById("level").value;
  const output = document.getElementById("output");
  const jsonBox = document.getElementById("jsonOutput");
  const t = I18N;

  if (!term) {
    output.innerHTML = `<p>${t.no_term}</p>`;
    return;
  }

  output.innerHTML = t.loading;
  jsonBox.style.display = "none";

  try {
    const res = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        term,
        level,
        language: currentLang
      })
    });

    const data = await res.json();

    output.innerHTML = `
      <h3>${t.definition}</h3>
      <p>${data.definition}</p>

      <h3>${t.explanation}</h3>
      <ul>${data.explanation.map(e => `<li>${e}</li>`).join("")}</ul>

      <h3>${t.advantages}</h3>
      <ul>${data.advantages.map(a => `<li>${a}</li>`).join("")}</ul>

      <h3>${t.disadvantages}</h3>
      <ul>${data.disadvantages.map(d => `<li>${d}</li>`).join("")}</ul>
    `;

    jsonBox.textContent = JSON.stringify(data, null, 2);

  } catch (err) {
    output.innerHTML = "❌ Error generating response";
  }
}

// ================================
// JSON TOGGLE
// ================================
function toggleJSON() {
  const box = document.getElementById("jsonOutput");
  box.style.display = box.style.display === "block" ? "none" : "block";
}

// ================================
// HISTORY
// ================================
async function loadHistory() {
  const list = document.getElementById("historyList");
  list.innerHTML = "<li>Loading...</li>";

  const res = await fetch("/api/history", { credentials: "include" });
  const data = await res.json();

  list.innerHTML = "";

  if (!data.length) {
    list.innerHTML = `<li>No history found</li>`;
    return;
  }

  data.forEach(item => {
    const li = document.createElement("li");
    li.innerText = item.term;
    li.onclick = () => {
      document.getElementById("query").value = item.term;
      closeHistory();
      generateExplanation();
    };
    list.appendChild(li);
  });
}

function openHistory() {
  document.getElementById("historyModal").style.display = "flex";
  loadHistory();
}

function closeHistory() {
  document.getElementById("historyModal").style.display = "none";
}

// ================================
// LOGOUT
// ================================
async function logout() {
  await fetch("/api/logout", {
    method: "POST",
    credentials: "include"
  });

  showToast("Logged out successfully 👋");
  setTimeout(() => window.location.href = "/signin", 800);
}
