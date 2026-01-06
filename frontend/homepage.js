async function checkLogin() {
    const response = await fetch("/api/check-login", {
        credentials: "include"
    });

    const data = await response.json();

    if (!data.logged_in) {
        // Not logged in → redirect to signin
        window.location.href = "/signin";
    } else {
        // Show username on top
        document.getElementById("username").innerText = data.username;
    }
}

async function logout() {
    await fetch("/api/logout", {
        credentials: "include"
    });
    window.location.href = "/signin";
}

// Run when page loads
checkLogin();
