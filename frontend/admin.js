// ================================
// AUTH CHECK
// ================================
window.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch("/api/check-login", { credentials: "include" });
  const data = await res.json();

  if (!data.logged_in || data.role !== "admin") {
    window.location.href = "/signin";
    return;
  }

  document.getElementById("adminName").innerText = data.username;

  loadUsers();
  loadPrompts();
});

// ================================
// LOAD USERS
// ================================
async function loadUsers() {
  const res = await fetch("/api/admin/users", { credentials: "include" });
  const users = await res.json();

  const tbody = document.querySelector("#usersTable tbody");
  tbody.innerHTML = "";

  users.forEach(u => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${u.id}</td>
      <td>${u.username}</td>
      <td>${u.email}</td>
      <td>${u.role}</td>
      <td>
        ${u.role !== "admin"
          ? `<button class="delete" onclick="deleteUser(${u.id})">Delete</button>`
          : "-"}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ================================
// LOAD PROMPTS
// ================================
async function loadPrompts() {
  const res = await fetch("/api/admin/prompts", { credentials: "include" });
  const prompts = await res.json();

  const tbody = document.querySelector("#promptsTable tbody");
  tbody.innerHTML = "";

  prompts.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.username}</td>
      <td>${p.term}</td>
      <td>${p.level}</td>
      <td>${p.language}</td>
      <td>${p.created_at}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ================================
// DELETE USER
// ================================
async function deleteUser(id) {
  if (!confirm("Delete this user?")) return;

  await fetch(`/api/admin/user/${id}`, {
    method: "DELETE",
    credentials: "include"
  });

  loadUsers();
}

// ================================
// LOGOUT
// ================================
async function logout() {
  await fetch("/api/logout", { method: "POST", credentials: "include" });
  window.location.href = "/signin";
}
