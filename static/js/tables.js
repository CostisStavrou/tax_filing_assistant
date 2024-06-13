async function fetchTaxData(afm) {
    if (afm.length !== 9 || isNaN(afm)) {
        console.error('AFM must be exactly 9 digits.');
        document.getElementById('message').innerText = 'AFM must be exactly 9 digits.';
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/get_tax_submissions?afm=${afm}`);
        if (!response.ok) {
            if (response.status === 404) {
                document.getElementById('message').innerText = `No person found with AFM: ${afm}`;
            } else {
                throw new Error(`An error occurred: ${response.statusText}`);
            }
        } else {
            const data = await response.json();
            document.getElementById('personTable').innerHTML = generateTable(data.person_info, "person");
            document.getElementById('taxDetailsTable').innerHTML = generateTable(data.tax_details_info, "tax_details");
            document.getElementById('message').innerText = '';
        }
    } catch (error) {
        console.error('Error fetching tax data:', error);
        document.getElementById('message').innerText = 'Error fetching tax data. Please try again later.';
    }
}

function generateTable(data, dataType) {
    let table = `<table border="1"><tr>`;
    let excludeKeys = [];

    if (dataType === 'tax_details') {
        excludeKeys = ['uid', 'afm'];
    } 

    if (Array.isArray(data)) {
        const keys = Object.keys(data[0]).filter(key => !excludeKeys.includes(key));
        keys.forEach(key => {
            table += `<th>${key}</th>`;
        });
        table += `</tr>`;
        data.forEach(item => {
            table += `<tr>`;
            keys.forEach(key => {
                table += `<td>${item[key]}</td>`;
            });
            table += `</tr>`;
        });
    } else {
        const keys = Object.keys(data).filter(key => !excludeKeys.includes(key));
        keys.forEach(key => {
            table += `<th>${key}</th>`;
        });
        table += `</tr><tr>`;
        keys.forEach(key => {
            table += `<td>${data[key]}</td>`;
        });
        table += `</tr>`;
    }
    table += `</table>`;
    return table;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('fetchDataButton').addEventListener('click', () => {
        const afm = document.getElementById('afmInput').value;
        fetchTaxData(afm);
    });
});


