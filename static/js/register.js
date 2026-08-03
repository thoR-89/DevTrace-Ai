document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('registerPassword');
    const strengthBar = document.getElementById('strengthBar');
    const togglePass = document.getElementById('togglePassword');

    if (togglePass && passwordInput) {
        togglePass.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', function() {
            const val = this.value;
            let score = 0;

            if (val.length >= 8) score += 33;
            if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score += 33;
            if (/[0-9]/.test(val) || /[^A-Za-z0-9]/.test(val)) score += 34;

            strengthBar.className = 'strength-bar';
            if (score <= 33 && val.length > 0) {
                strengthBar.classList.add('weak');
            } else if (score <= 66) {
                strengthBar.classList.add('medium');
            } else if (score > 66) {
                strengthBar.classList.add('strong');
            }
        });
    }
});