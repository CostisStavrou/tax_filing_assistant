document.addEventListener('DOMContentLoaded', () => {
    // Event listener for the login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const afm = document.getElementById('login-afm').value;
            const password = document.getElementById('login-password').value;
            await loginUser(afm, password);
        });
    }

    // Event listener for the sign up button click
    const signupButton = document.getElementById('signup-button');
    if (signupButton) {
        signupButton.addEventListener('click', () => {
            const signupPageUrl = `${window.location.origin}/signup-page`;
            window.location.href = signupPageUrl;
        })
    }
});

// async function loginUser(afm, password) {
//     try {
//         const response = await fetch('http://127.0.0.1:8000/login', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ afm, password }),
//         });

//         if (!response.ok) {
//             throw new Error(`An error occurred: ${response.statusText}`);
//         }

//         const data = await response.json();
//         document.getElementById('message').innerText = data.message;

//     } catch (error) {
//         console.error('Error logging in:', error);
//         document.getElementById('message').innerText = 'Invalid AFM or password';
//     }
// }
