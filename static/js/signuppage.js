document.addEventListener('DOMContentLoaded', () => {
    // Event listener for the signup form submission
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const afm = document.getElementById('signup-afm').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;
            await signupUser(afm, email, password);
        });
    }
});

// async function signupUser(afm, email, password) {
//     try {
//         const response = await fetch('http://127.0.0.1:8000/signup', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ afm, email, password }),
//         });

//         if (!response.ok) {
//             throw new Error(`An error occurred: ${response.statusText}`);
//         }

//         const data = await response.json();
//         console.log(data);
//         document.getElementById('message').innerText = data.message;

//     } catch (error) {
//         console.error('Error signing up:', error);
//         document.getElementById('message').innerText = 'Error signing up. Please try again.';
//     }
// }
