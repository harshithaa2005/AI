document.getElementById("signupForm").addEventListener("submit", async e => {
  e.preventDefault();

  const username = document.getElementById("username").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;
  const msg = document.getElementById("errorMsg");

  try {
    const res = await fetch("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        username,
        email,
        password,
        role
      })
    });

    const data = await res.json();

    if (!res.ok) {
      msg.textContent = data.message || "Signup failed";
      return;
    }

    window.location.href = "/signin";

  } catch {
    msg.textContent = "Server error";
  }
});
