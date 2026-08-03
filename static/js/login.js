document.addEventListener('DOMContentLoaded', function() {
    const togglePass = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');

    if (togglePass && passwordInput) {
        togglePass.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
});