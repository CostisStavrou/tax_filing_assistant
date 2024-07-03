document.getElementById("signup-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    
    const afm = document.getElementById("signup-afm").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;

    try {
        console
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
            console.log("sign up successful")
            document.getElementById("message").textContent = "Sign up successful!";
            console.log("sign up successful")
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
                console.log(tokenData.access_token)
                const response = await fetch("/", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${tokenData.access_token}`
                    }
                });

                if (response.ok) {
                    console.log("tables response")
                    const homeHTML = await response.text();
                    
                    document.open();
                    document.write(homeHTML);
                    document.close();
                    
                } else {
                    throw new Error("Failed to load homepage.");
                }
            } else {
                throw new Error("Failed to retrieve token.");
            }
        } else {
            document.getElementById("message").textContent = "Sign up failed!";
        }
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("message").textContent = `An error occurred: ${error.message}`;
    }
});
