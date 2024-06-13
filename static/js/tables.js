async function fetchTaxData(afm) {
    if (afm.length !== 9 || isNaN(afm)) {
        console.error('AFM must be exactly 9 digits.');
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/get_tax_submissions?afm=${afm}`);
        if (!response.ok) {
            throw new Error(`An error occurred: ${response.statusText}`);
        }
                      
        const data = await response.json();
        document.getElementById('personTable').innerHTML = generateTable(data.person_info, "person" );
        document.getElementById('taxDetailsTable').innerHTML = generateTable(data.tax_details_info, "tax_details");

    } catch (error) {
        console.error('Error fetching tax data:', error);
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
    const urlParams = new URLSearchParams(window.location.search);
    const afm = urlParams.get('afm');
    if (afm) {
        fetchTaxData(afm);
    }
});


