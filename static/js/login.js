document.addEventListener('DOMContentLoaded', function () {
    // ── Toggle password visibility ─────────────────────────────────────────
    const togglePass    = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');

    if (togglePass && passwordInput) {
        togglePass.addEventListener('click', function () {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

    // ── Prevent double-submit on login form ────────────────────────────────
    const loginBtn  = document.getElementById('loginBtn');
    const loginForm = document.getElementById('loginForm');
    if (loginForm && loginBtn) {
        loginForm.addEventListener('submit', function () {
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Signing In...';
        });
    }
});