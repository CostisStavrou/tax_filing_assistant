document.getElementById('taxForm').addEventListener('submit', function(event) {
    var form = event.target;

    var numberFields = ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical', 'donations', 'afm', 'insurance', 'renovation', 'propertyValue', 'taxPrepayments', 'insurancePayments'];
    for (var i = 0; i < numberFields.length; i++) {
        var field = form[numberFields[i]];
        if (field && isNaN(field.value)) {
            alert(field.name + " πρέπει να είναι αριθμός.");
            event.preventDefault();
            return;
        }
    }
});

document.getElementById("taxForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let formData = new FormData(event.target);
    console.log(formData)

    let data = {
        name: formData.get("name"),
        afm: parseInt(formData.get("afm")),
        address: formData.get("address"),
        family_status: formData.get("familyStatus"),
        children: parseInt(formData.get("children")),
        salary: parseFloat(formData.get("salary")),
        freelance: parseFloat(formData.get("freelance")),
        rental: parseFloat(formData.get("rental")),
        investments: parseFloat(formData.get("investments")),
        business: parseFloat(formData.get("business")),
        medical: parseFloat(formData.get("medical")),
        donations: parseFloat(formData.get("donations")),
        insurance: parseFloat(formData.get("insurance")),
        renovation: parseFloat(formData.get("renovation")),
        property_details: formData.get("propertyDetails"),
        property_value: parseFloat(formData.get("propertyValue")),
        vehicles: formData.get("vehicles"),
        tax_prepayments: parseFloat(formData.get("taxPrepayments")),
        insurance_payments: parseFloat(formData.get("insurancePayments"))
    };

    // Make fetch request
    fetch("http://127.0.0.1:8000/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail) });
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