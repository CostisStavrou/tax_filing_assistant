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
            const tablesHTML = generateTable([
                { data: data.person_info, dataType: "person" },
                { data: data.tax_details_info, dataType: "tax_details" }
            ]);

            document.getElementById('tablesContainer').innerHTML = tablesHTML;
            attachRowClickEvents(data.tax_details_info); 
            document.getElementById('message').innerText = '';
            document.querySelector('.container').classList.add('expanded');
        }
    } catch (error) {
        console.error('Error fetching tax data:', error);
        document.getElementById('message').innerText = 'This AFM does not exist';
        document.querySelector('.container').classList.remove('expanded');
    }
}

function generateTable(tablesData) {
    let combinedHTML = '';

    tablesData.forEach(tableData => {
        let table = `<table border="1"><tr>`;
        let excludeKeys = [];

        if (tableData.dataType === 'tax_details') {
            excludeKeys = ['uid', 'afm'];
        }
        const getFilteredKeys = (item) => Object.keys(item).filter(key => !excludeKeys.includes(key));

        if (Array.isArray(tableData.data)) {
            const keys = getFilteredKeys(tableData.data[0]);
            keys.forEach(key => {
                table += `<th>${key}</th>`;
            });
            table += `</tr>`;
            tableData.data.forEach(item => {
                table += `<tr>`;
                keys.forEach(key => {
                    table += `<td>${item[key]}</td>`;
                });
                table += `</tr>`;
            });
        } else {
            const keys = getFilteredKeys(tableData.data);
            keys.forEach(key => {
                table += `<th>${key}</th>`;
            });
            table += `</tr><tr>`;
            keys.forEach(key => {
                table += `<td>${tableData.data[key]}</td>`;
            });
            table += `</tr>`;
        }
        table += `</table>`;

        combinedHTML += table + '<br>'; 
    });

    return combinedHTML;
}

function attachRowClickEvents(taxDetailsData) {
    const rows = document.querySelectorAll('#tablesContainer table:nth-of-type(2) tr');
    const getFilteredKeys = (item) => Object.keys(item).filter(key => key !== 'uid' && key !== 'afm');

    rows.forEach((row, index) => {
        if (index > 0) {
            row.addEventListener('click', () => {
                const rowData = {};
                const cells = row.getElementsByTagName('td');
                const keys = getFilteredKeys(taxDetailsData[0]);
                keys.forEach((key, keyIndex) => {
                    rowData[key] = cells[keyIndex].innerText;
                });
                console.log(rowData);
                generateTaxAdvice(rowData);
            });
        }
    });
}

async function generateTaxAdvice(rowData) {
    try {
        console.log(rowData);
        const response = await fetch('http://127.0.0.1:8000/generate_advice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(rowData),
        });

        if (!response.ok) {
            throw new Error(`An error occurred: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(data);
        document.getElementById('advice').innerText = data.message;
    } catch (error) {
        console.error('Error generating advice:', error);
        document.getElementById('advice').innerText = 'Error generating advice. Please try again later.';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('fetchDataButton').addEventListener('click', () => {
        const afm = document.getElementById('afmInput').value;
        fetchTaxData(afm);
    });
});
