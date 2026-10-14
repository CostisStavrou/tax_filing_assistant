document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const afm = document.getElementById("signup-afm").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value;
    const message = document.getElementById("message");

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ afm: afm, email: email, password: password })
        });

        if (response.ok) {
            // Signup returns a token, so the user is logged in straight away.
            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            window.location.href = "/";
        } else {
            message.textContent = `Sign up failed: ${await errorMessage(response)}`;
        }
    } catch (error) {
        message.textContent = "Sign up failed: could not reach the server.";
    }
});
