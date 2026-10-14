document.addEventListener('DOMContentLoaded', () => {
    // Already logged in? Go straight to the submissions page.
    if (!isTokenExpired(getToken())) {
        window.location.href = "/tables";
        return;
    }

    document.getElementById("login-form").addEventListener("submit", async (event) => {
        event.preventDefault();

        const afm = document.getElementById("login-afm").value.trim();
        const password = document.getElementById("login-password").value;
        const message = document.getElementById("message");

        try {
            const response = await fetch("/token", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ username: afm, password: password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("token", data.access_token);
                window.location.href = "/tables";
            } else {
                message.textContent = `Login failed: ${await errorMessage(response)}`;
            }
        } catch (error) {
            message.textContent = "Login failed: could not reach the server.";
        }
    });

    document.getElementById('signup-button').addEventListener('click', () => {
        window.location.href = "/signup-page";
    });
});
