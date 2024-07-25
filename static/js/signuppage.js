document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    console.info("Signup form submitted.");

    const afm = document.getElementById("signup-afm").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;

    try {
        console.debug("Attempting to sign up with AFM:", afm, "Email:", email);

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
            console.info("Sign up successful.");
            document.getElementById("message").textContent = "Sign up successful!";
            
            // Fetch the token
            const tokenResponse = await fetch("/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    username: afm,
                    password: password
                })
            });

            if (tokenResponse.ok) {
                const tokenData = await tokenResponse.json();
                localStorage.setItem("token", tokenData.access_token);
                console.info("Token retrieved and stored:", tokenData.access_token);

                const response = await fetch("/", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${tokenData.access_token}`
                    }
                });

                if (response.ok) {
                    console.info("Homepage loaded successfully.");
                    const homeHTML = await response.text();
                    
                    document.open();
                    document.write(homeHTML);
                    document.close();
                    
                } else {
                    console.error("Failed to load homepage.");
                    throw new Error("Failed to load homepage.");
                }
            } else {
                console.error("Failed to retrieve token.");
                throw new Error("Failed to retrieve token.");
            }
        } else {
            console.warn("Sign up failed with status:", response.status);
            document.getElementById("message").textContent = "Sign up failed!";
        }
    } catch (error) {
        console.error("Error during sign up:", error);
        document.getElementById("message").textContent = `An error occurred: ${error.message}`;
    }
});
