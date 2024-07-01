document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("login-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        
        const afm = document.getElementById("login-afm").value;
        const password = document.getElementById("login-password").value;
    
        console.log(afm);

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
    
        console.log(response.status);

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            document.getElementById("message").textContent = "Login successful!";
            console.log("Login successful!");
            console.log(data.access_token);

            // Instead of redirecting directly, make a request to the endpoint and load the HTML
            const tablesResponse = await fetch("/tables", { 
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${data.access_token}`
                }
            });

            if (tablesResponse.ok) {
                const html = await tablesResponse.text();
                document.open();
                document.write(html);
                document.close();
            } else {
                document.getElementById("message").textContent = "Failed to load tables!";
            }

        } else {
            document.getElementById("message").textContent = "Login failed!";
        }
    });    
    
    const signupButton = document.getElementById('signup-button');
    if (signupButton) {
        signupButton.addEventListener('click', () => {
            const signupPageUrl = `${window.location.origin}/signup-page`;
            window.location.href = signupPageUrl;
        });
    }
});
