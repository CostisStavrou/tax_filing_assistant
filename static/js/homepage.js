document.getElementById('taxForm').addEventListener('submit', async function(event) {
    event.preventDefault();



    var form = event.target;
    var numberFields = ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical', 'donations', 'insurance', 'renovation', 'propertyValue', 'taxPrepayments', 'insurancePayments'];

    for (var i = 0; i < numberFields.length; i++) {
        var field = form[numberFields[i]];
        if (field && isNaN(field.value)) {
            alert(field.name + " πρέπει να είναι αριθμός.");
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
                redirectToLogin("Your session has expired. Please log in again.");
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

function isTokenExpired(token) {
    if (!token) return true;

    const payload = JSON.parse(atob(token.split('.')[1]));
    const expiry = payload.exp * 1000;
    return Date.now() > expiry;
}

async function redirectToLogin(message) {
    localStorage.removeItem("token");
    alert(message);

    const redirectResponse = await fetch("/login-page", {
        method: "GET",
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (!redirectResponse.ok) {
        throw new Error("Failed to redirect to the tables page.");
    }
    window.location.href = "/login-page";
}
