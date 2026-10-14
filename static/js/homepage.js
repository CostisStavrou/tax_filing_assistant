const NUMBER_FIELDS = ['children', 'salary', 'freelance', 'rental', 'investments', 'business', 'medical',
    'donations', 'insurance', 'renovation', 'property_value', 'tax_prepayments', 'insurance_payments'];

document.addEventListener('DOMContentLoaded', () => {
    const token = requireToken();
    if (!token) return;

    // Fill in the logged-in user's AFM and lock the field: returns can only be filed for your own AFM.
    const payload = decodeTokenPayload(token);
    const afmField = document.getElementById('afm');
    if (payload.afm && afmField) {
        afmField.value = payload.afm;
        afmField.readOnly = true;
    }

    document.getElementById('taxForm').addEventListener('submit', async (event) => {
        event.preventDefault();

        const data = {};
        new FormData(event.target).forEach((value, key) => {
            data[key] = NUMBER_FIELDS.includes(key) ? Number(value) : value.trim();
        });

        try {
            const response = await authFetch("/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!response) return;  // redirected to login

            if (response.ok) {
                window.location.href = "/tables";
            } else {
                alert(`Could not submit: ${await errorMessage(response)}`);
            }
        } catch (error) {
            alert("Could not submit: the server could not be reached.");
        }
    });
});
