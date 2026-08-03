document.addEventListener('DOMContentLoaded', function () {

    const passwordInput = document.getElementById('registerPassword');
    const strengthBar   = document.getElementById('strengthBar');
    const strengthLabel = document.getElementById('strengthLabel');
    const togglePass    = document.getElementById('togglePassword');

    // ── Toggle password visibility ────────────────────────────────────────
    if (togglePass && passwordInput) {
        togglePass.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

    // ── Password strength meter ───────────────────────────────────────────
    if (passwordInput && strengthBar) {
        passwordInput.addEventListener('input', function () {
            const val = this.value;

            // Reset to empty if field is blank
            if (val.length === 0) {
                strengthBar.className = 'strength-bar';
                strengthBar.style.width = '0%';
                if (strengthLabel) {
                    strengthLabel.className = 'strength-label';
                    strengthLabel.textContent = '';
                }
                return;
            }

            let score = 0;
            if (val.length >= 8)                              score += 33;
            if (/[A-Z]/.test(val) && /[a-z]/.test(val))      score += 33;
            if (/[0-9]/.test(val) || /[^A-Za-z0-9]/.test(val)) score += 34;

            strengthBar.className = 'strength-bar';
            if (strengthLabel) strengthLabel.className = 'strength-label';

            if (score <= 33) {
                strengthBar.classList.add('weak');
                if (strengthLabel) { strengthLabel.classList.add('weak'); strengthLabel.textContent = 'Weak'; }
            } else if (score <= 66) {
                strengthBar.classList.add('medium');
                if (strengthLabel) { strengthLabel.classList.add('medium'); strengthLabel.textContent = 'Medium'; }
            } else {
                strengthBar.classList.add('strong');
                if (strengthLabel) { strengthLabel.classList.add('strong'); strengthLabel.textContent = 'Strong'; }
            }
        });
    }

    // ── Prevent double-submit on register form ────────────────────────────
    const registerBtn = document.getElementById('registerBtn');
    const registerForm = document.getElementById('registerForm');
    if (registerForm && registerBtn) {
        registerForm.addEventListener('submit', function () {
            registerBtn.disabled = true;
            registerBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Creating Account...';
        });
    }
});