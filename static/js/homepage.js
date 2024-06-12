document.getElementById('taxForm').addEventListener('submit', function(event) {
    var form = event.target;
    var numberFields = ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical', 'donations', 'insurance', 'renovation', 'propertyValue', 'taxPrepayments', 'insurancePayments'];

    for (var i = 0; i < numberFields.length; i++) {
        var field = form[numberFields[i]];
        if (field && isNaN(field.value)) {
            alert(field.name + " πρέπει να είναι αριθμός.");
            event.preventDefault();
            return;
        }
    }

    event.preventDefault();

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

    fetch("http://127.0.0.1:8000/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(JSON.stringify(err)); });
        }
        return response.json();
    })
    .then(data => {
        console.log("Success:", data);
        alert("Data submitted successfully!");
    })
    .catch((error) => {
        console.error("Error:", error);
        alert(`An error occurred: ${error.message}`);
    });
});

async function fetchTaxData(afm) {
    // Validate the AFM
    if (afm.length !== 9 || isNaN(afm)) {
        console.error('AFM must be exactly 9 digits.');
        return;
    }

    try {
        // Fetch data from the API
        const response = await fetch(`http://127.0.0.1:8000/get_tax_submissions?afm=${afm}`);
        if (!response.ok) {
            throw new Error(`An error occurred: ${response.statusText}`);
        }

        // Parse JSON response
        const data = await response.json();

        // Format the JSON response
        const formattedData = formatResponse(data);

        // Log the formatted JSON data
        console.log(JSON.stringify(formattedData, null, 2));

    } catch (error) {
        console.error('Error fetching tax data:', error);
    }
}
