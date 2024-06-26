document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    
    const afm = document.getElementById("signup-afm").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;

    const response = await fetch("/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            afm: afm,
            email: email,
            password: password
        })
    });

    if (response.ok) {
        document.getElementById("message").textContent = "Sign up successful!";
    } else {
        document.getElementById("message").textContent = "Sign up failed!";
    }
});
