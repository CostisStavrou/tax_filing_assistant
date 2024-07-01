document.addEventListener('DOMContentLoaded', () => {
    fetchTaxData();

    document.getElementById('newSubmissionButton').addEventListener('click', async () => {
        await makeAuthorizedRequest();
    });
});

async function fetchTaxData() {
    const token = localStorage.getItem("token");

    // Check if the token is expired before proceeding
    if (isTokenExpired(token)) {
        await redirectToLogin("Your session has expired. Please log in again.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/get_tax_submissions", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                document.getElementById('message').innerText = 'No person found';
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
        document.getElementById('message').innerText = 'Error fetching tax data';
    }
}

async function makeAuthorizedRequest() {
    const token = localStorage.getItem("token");

    // Check if the token is expired before proceeding
    if (isTokenExpired(token)) {
        await redirectToLogin("Your session has expired. Please log in again.");
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/', {
            method: 'GET',
            headers: {
                "Content-Type": "application/json",
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`An error occurred: ${response.statusText}`);
        }

        const data = await response.text();
        document.open();
        document.write(data);
        document.close();

    } catch (error) {
        console.error('Error making authorized request:', error);
        document.getElementById('message').innerText = 'Error making authorized request. Please try again later.';
    }
}

async function generateTaxAdvice(rowData) {
    const token = localStorage.getItem("token");

    // Check if the token is expired before proceeding
    if (isTokenExpired(token)) {
        await redirectToLogin("Your session has expired. Please log in again.");
        return;
    }

    try {
        console.log("Retrieved token2:", token);
        const response = await fetch('http://127.0.0.1:8000/generate_advice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
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

            document.body.classList.add('loading');

            try {
                await generateTaxAdvice(rowObject);
            } finally {
                document.body.classList.remove('loading');
            }
        });
    });
}
