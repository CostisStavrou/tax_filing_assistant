document.addEventListener('DOMContentLoaded', () => {
    console.info("Document loaded. Initializing...");

    const token = localStorage.getItem("token");

    if (token) {
        console.debug("Token found in localStorage.");
        const payload = JSON.parse(atob(token.split('.')[1]));
        const afmField = document.getElementById('afm');

        if (payload.afm && afmField) {
            afmField.value = payload.afm;
            afmField.readOnly = true; // Make the AFM field read-only
            console.info("AFM field populated and set to read-only.");
        } else {
            console.warn("AFM field or payload.afm not found.");
        }
    } else {
        console.warn("No token found in localStorage.");
    }

    document.getElementById('taxForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        console.info("Form submission initiated.");

        const token = localStorage.getItem("token");

        // Check if the token is expired before proceeding
        if (isTokenExpired(token)) {
            console.warn("Token expired. Redirecting to login...");
            await redirectToLogin("Your session has expired. Please log in again.");
            return;
        }

        var form = event.target;
        var numberFields = ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical', 'donations', 'insurance', 'renovation', 'propertyValue', 'taxPrepayments', 'insurancePayments'];

        for (var i = 0; i < numberFields.length; i++) {
            var field = form[numberFields[i]];
            if (field && isNaN(field.value)) {
                alert(field.name + " must be a number.");
                console.error(`${field.name} must be a number.`);
                return;
            }
        }

        let formData = new FormData(event.target);
        let data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical', 'donations', 'insurance', 'renovation', 'property_value', 'tax_prepayments', 'insurance_payments'].forEach(field => {
            if (data[field]) {
                data[field] = parseFloat(data[field]);
            }
        });

        try {
            console.debug("Sending data to the server...");
            const response = await fetch("http://127.0.0.1:8000/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                if (response.status === 401) {
                    console.warn("Unauthorized response from the server. Redirecting to login...");
                    await redirectToLogin("Your session has expired. Please log in again.");
                } else {
                    const errorData = await response.json();
                    console.error("Error response from server:", errorData);
                    throw new Error(JSON.stringify(errorData));
                }
            }

            const responseData = await response.json();
            console.info("Data submitted successfully:", responseData);
            alert("Data submitted successfully!");

            const redirectResponse = await fetch("/tables", {
                method: "GET",
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!redirectResponse.ok) {
                console.error("Failed to redirect to the tables page.");
                throw new Error("Failed to redirect to the tables page.");
            }
            window.location.href = "/tables";

        } catch (error) {
            console.error("Error during form submission:", error);
            alert(`An error occurred: ${error.message}`);
        }
    });
});

async function redirectToLogin(message) {
    localStorage.removeItem("token");
    alert(message);
    console.info("Redirecting to login page...");

    try {
        const redirectResponse = await fetch("/login-page", {
            method: "GET",
            headers: {}
        });

        if (!redirectResponse.ok) {
            console.error("Failed to redirect to the login page.");
            throw new Error("Failed to redirect to the login page.");
        }
        window.location.href = "/login-page";
    } catch (error) {
        console.error("Error redirecting to login page:", error);
        alert(`An error occurred: ${error.message}`);
    }
}

function isTokenExpired(token) {
    if (!token) {
        console.warn("Token not found or expired.");
        return true;
    }

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expiry = payload.exp * 1000;
        const isExpired = Date.now() > expiry;
        if (isExpired) {
            console.warn("Token has expired.");
        } else {
            console.debug("Token is valid.");
        }
        return isExpired;
    } catch (error) {
        console.error("Error parsing token payload:", error);
        return true;
    }
}
