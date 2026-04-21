const form = document.getElementById("signinForm");
const errorMsg = document.getElementById("errorMsg");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorMsg.textContent = "";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    const res = await fetch("/api/signin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      errorMsg.textContent = data.message || "Login failed";
      return;
    }

    // ✅ ROLE-BASED REDIRECT
    if (data.role === "admin") {
      window.location.href = "/admin";
    } else {
      window.location.href = "/";
    }

  } catch (err) {
    errorMsg.textContent = "Server error. Try again.";
  }
});
