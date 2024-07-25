document.addEventListener('DOMContentLoaded', () => {
    console.info("Document loaded and DOM content initialized.");

    document.getElementById("login-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        console.info("Login form submitted.");

        const afm = document.getElementById("login-afm").value;
        const password = document.getElementById("login-password").value;

        try {
            const response = await fetch("/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    username: afm,
                    password: password
                })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("token", data.access_token);
                document.getElementById("message").textContent = "Login successful!";
                console.info("Login successful!");
                console.debug("Access token:", data.access_token);

                // Instead of redirecting directly, make a request to the endpoint and load the HTML
                const tablesResponse = await fetch("/tables", { 
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${data.access_token}`
                    }
                });

                if (tablesResponse.ok) {
                    const html = await tablesResponse.text();
                    console.info("Tables page loaded successfully.");
                    document.open();
                    document.write(html);
                    document.close();
                } else {
                    document.getElementById("message").textContent = "Failed to load tables!";
                    console.error("Failed to load tables page.");
                }

            } else {
                document.getElementById("message").textContent = "Login failed!";
                console.warn("Login failed with status:", response.status);
            }
        } catch (error) {
            console.error("Error during login:", error);
            document.getElementById("message").textContent = "An error occurred during login!";
        }
    });    
    
    const signupButton = document.getElementById('signup-button');
    if (signupButton) {
        signupButton.addEventListener('click', () => {
            console.info("Signup button clicked.");
            const signupPageUrl = `${window.location.origin}/signup-page`;
            window.location.href = signupPageUrl;
        });
    }
});
