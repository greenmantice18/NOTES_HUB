document.addEventListener("DOMContentLoaded", function () {
    // Ensure elements exist before attaching event listeners
    const signupLink = document.getElementById('signup-link');
    const loginLink = document.getElementById('login-link');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const loginTab = document.getElementById('login-tab');
    const signupTab = document.getElementById('signup-tab');
    const loginFormElement = document.getElementById('loginForm');
    const signupFormElement = document.getElementById('signupForm');

    if (signupLink && loginLink && loginForm && signupForm && loginTab && signupTab) {
        // Switch to Signup Form
        signupLink.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default link action
            loginForm.classList.add('hidden');
            signupForm.classList.remove('hidden');
            signupTab.classList.add('active');
            loginTab.classList.remove('active');
        });

        // Switch to Login Form
        loginLink.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default link action
            signupForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
            loginTab.classList.add('active');
            signupTab.classList.remove('active');
        });
    }

    // Optional: Form submission handling
    if (loginFormElement) {
        loginFormElement.addEventListener('submit', function (event) {
            event.preventDefault();
            alert('Login Form Submitted');
        });
    }

    if (signupFormElement) {
        signupFormElement.addEventListener('submit', function (event) {
            event.preventDefault();
            alert('Signup Form Submitted');
        });
    }
});
