 document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("login-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        
        const afm = document.getElementById("login-afm").value;
        const password = document.getElementById("login-password").value;
    
        console.log(afm)

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
    
        console.log(response.status)

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            document.getElementById("message").textContent = "Login successful!";
            window.location.href = "/tables";
        } else {
            document.getElementById("message").textContent = "Login failed!";
        }
    });    
    
    const signupButton = document.getElementById('signup-button');
    if (signupButton) {
        signupButton.addEventListener('click', () => {
            const signupPageUrl = `${window.location.origin}/signup-page`;
            window.location.href = signupPageUrl;
        })
    }
});

