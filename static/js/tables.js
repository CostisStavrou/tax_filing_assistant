const HIDDEN_COLUMNS = ['uid', 'afm', 'submission_date'];

document.addEventListener('DOMContentLoaded', () => {
    if (!requireToken()) return;
    fetchTaxData();

    document.getElementById('newSubmissionButton').addEventListener('click', () => {
        window.location.href = "/";
    });

    document.getElementById('logoutButton').addEventListener('click', logoutUser);
});

async function fetchTaxData() {
    const message = document.getElementById('message');
    try {
        const response = await authFetch("/get_tax_submissions");
        if (!response) return;  // redirected to login
        if (!response.ok) {
            message.innerText = `Error fetching tax data: ${await errorMessage(response)}`;
            return;
        }

        const data = await response.json();
        if (!data.person_info || data.tax_details_info.length === 0) {
            message.innerText = 'No submissions yet. Click "New Submission" to file your first tax return.';
            return;
        }

        document.getElementById('tablesContainer').innerHTML =
            generatePersonTable(data.person_info) + '<br>' + generateSubmissionsTable(data.tax_details_info);
        attachAdviceButtons(data.tax_details_info);
        message.innerText = '';
    } catch (error) {
        message.innerText = 'Error fetching tax data: the server could not be reached.';
    }
}

function logoutUser() {
    fetch("/logout", { method: "POST" }).finally(() => {
        localStorage.removeItem("token");
        window.location.href = "/login-page";
    });
}

// All values are escaped: names, addresses and other free text are typed in by the user.
function generatePersonTable(person) {
    const keys = Object.keys(person).filter(key => key !== 'afm');
    let table = '<table border="1"><tr>';
    keys.forEach(key => { table += `<th>${escapeHtml(key)}</th>`; });
    table += '</tr><tr>';
    keys.forEach(key => { table += `<td>${escapeHtml(person[key])}</td>`; });
    return table + '</tr></table>';
}

function generateSubmissionsTable(submissions) {
    const keys = Object.keys(submissions[0]).filter(key => !HIDDEN_COLUMNS.includes(key));
    let table = '<table border="1"><tr><th>Action</th><th>submission_date</th>';
    keys.forEach(key => { table += `<th>${escapeHtml(key)}</th>`; });
    table += '</tr>';

    submissions.forEach((item, index) => {
        table += `<tr><td><button class="advice-button" data-index="${index}">Generate Advice</button></td>`;
        table += `<td>${escapeHtml(item.submission_date)}</td>`;
        keys.forEach(key => { table += `<td>${escapeHtml(item[key])}</td>`; });
        table += '</tr>';
    });
    return table + '</table>';
}

function attachAdviceButtons(submissions) {
    document.querySelectorAll('.advice-button').forEach(button => {
        button.addEventListener('click', async (event) => {
            const submission = submissions[event.target.dataset.index];
            document.body.classList.add('loading');
            try {
                await generateTaxAdvice(submission.uid);
            } finally {
                document.body.classList.remove('loading');
            }
        });
    });
}

async function generateTaxAdvice(uid) {
    const advice = document.getElementById('advice');
    try {
        // Only the submission's id is sent: the server loads the figures itself, and only for the logged-in user.
        const response = await authFetch('/generate_advice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid: uid })
        });
        if (!response) return;
        if (!response.ok) {
            advice.innerText = await errorMessage(response);
            return;
        }

        const data = await response.json();
        // The model replies in Markdown. Convert it to HTML, then sanitise it before inserting it into the page.
        const html = new showdown.Converter().makeHtml(data.message);
        advice.innerHTML = DOMPurify.sanitize(html);
    } catch (error) {
        advice.innerText = 'Error generating advice. Please try again later.';
    }
}
