document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem("token");

    if (token) {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const afmField = document.getElementById('afm');

        if (payload.afm && afmField) {
            afmField.value = payload.afm;
            afmField.readOnly = true; // Make the AFM field read-only
        }
    }

    document.getElementById('taxForm').addEventListener('submit', async function(event) {
        event.preventDefault();

        const token = localStorage.getItem("token");

        // Check if the token is expired before proceeding
        if (isTokenExpired(token)) {
            await redirectToLogin("Your session has expired. Please log in again.");
            return;
        }

        var form = event.target;
        var numberFields = ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical', 'donations', 'insurance', 'renovation', 'propertyValue', 'taxPrepayments', 'insurancePayments'];

        for (var i = 0; i < numberFields.length; i++) {
            var field = form[numberFields[i]];
            if (field && isNaN(field.value)) {
                alert(field.name + " must be a number.");
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
                    await redirectToLogin("Your session has expired. Please log in again.");
                } else {
                    const errorData = await response.json();
                    throw new Error(JSON.stringify(errorData));
                }
            }

            const responseData = await response.json();
            console.log("Success:", responseData);
            alert("Data submitted successfully!");

            const redirectResponse = await fetch("/tables", {
                method: "GET",
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!redirectResponse.ok) {
                throw new Error("Failed to redirect to the tables page.");
            }
            window.location.href = "/tables";

        } catch (error) {
            console.error("Error:", error);
            alert(`An error occurred: ${error.message}`);
        }
    });
});

async function redirectToLogin(message) {
    localStorage.removeItem("token");
    alert(message);

    try {
        const redirectResponse = await fetch("/login-page", {
            method: "GET",
            headers: {}
        });

        if (!redirectResponse.ok) {
            throw new Error("Failed to redirect to the login page.");
        }
        window.location.href = "/login-page";
    } catch (error) {
        console.error("Error redirecting to login page:", error);
        alert(`An error occurred: ${error.message}`);
    }
}

function isTokenExpired(token) {
    if (!token) return true;

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expiry = payload.exp * 1000;
        return Date.now() > expiry;
    } catch (error) {
        console.error("Error parsing token payload:", error);
        return true;
    }
}
