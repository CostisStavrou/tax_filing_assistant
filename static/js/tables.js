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
            attachButtonClickEvents(data.tax_details_info); 
            document.getElementById('message').innerText = '';
        }
    } catch (error) {
        console.error('Error fetching tax data:', error);
        document.getElementById('message').innerText = 'This AFM does not exist';
    }
}

function generateTable(tablesData) {
    let combinedHTML = '';

    tablesData.forEach(tableData => {
        let table = `<table border="1"><tr>`;
        let excludeKeys = [];

        if (tableData.dataType === 'tax_details') {
            excludeKeys = ['uid', 'afm', 'submission_date'];
        }
        const getFilteredKeys = (item) => Object.keys(item).filter(key => !excludeKeys.includes(key));

        if (Array.isArray(tableData.data)) {
            const keys = getFilteredKeys(tableData.data[0]);

            if (tableData.dataType === 'tax_details') {
                table += `<th>Action</th><th>submission_date</th>`;
            }
            
            keys.forEach(key => {
                table += `<th>${key}</th>`;
            });
            table += `</tr>`;
            tableData.data.forEach((item, index) => {
                table += `<tr>`;

                if (tableData.dataType === 'tax_details') {
                    table += `<td><button class="advice-button" data-index="${index}">Generate Advice</button></td>`;
                    table += `<td>${item.submission_date}</td>`;
                }

                keys.forEach(key => {
                    table += `<td>${item[key]}</td>`;
                });
                table += `</tr>`;
            });
        } else {
            const keys = getFilteredKeys(tableData.data);

            if (tableData.dataType === 'tax_details') {
                table += `<th>Action</th><th>submission_date</th>`;
            }

            keys.forEach(key => {
                table += `<th>${key}</th>`;
            });
            table += `</tr><tr>`;

            if (tableData.dataType === 'tax_details') {
                table += `<td><button class="advice-button" data-index="0">Generate Advice</button></td>`;
                table += `<td>${tableData.data.submission_date}</td>`;
            }

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

function attachButtonClickEvents(taxDetailsData) {
    const buttons = document.querySelectorAll('.advice-button');
    const getFilteredKeys = (item) => Object.keys(item).filter(key => key !== 'uid' && key !== 'afm' && key !== 'submission_date');

    buttons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const index = event.target.dataset.index;
            const rowData = taxDetailsData[index];
            const filteredKeys = getFilteredKeys(rowData);
            const rowObject = {};
            
            filteredKeys.forEach(key => {
                rowObject[key] = rowData[key];
            });

            const spinner = document.getElementById('spinner');
            spinner.style.display = 'block';
            document.querySelectorAll('.advice-button').forEach(btn => btn.disabled = true);

            try {
                await generateTaxAdvice(rowObject);
            } finally {
                spinner.style.display = 'none';
                document.querySelectorAll('.advice-button').forEach(btn => btn.disabled = false);
            }
        });
    });
}

async function generateTaxAdvice(rowData) {
    try {
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

        const converter = new showdown.Converter();
        const adviceHTML = converter.makeHtml(data.message);
        document.getElementById('advice').innerHTML = adviceHTML;

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
