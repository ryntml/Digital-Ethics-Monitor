/**
 * Digital Ethics Monitor - Authentication Handler
 * 
 * JWT token yönetimi ve kullanıcı kimlik doğrulama işlemleri
 * Backend API ile entegre edilecektir
 */

/**
 * Login form submit handler
 */
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        // UI güncellemeleri
        const errorMessage = document.getElementById('errorMessage');
        const buttonText = document.getElementById('loginButtonText');
        const buttonSpinner = document.getElementById('loginButtonSpinner');
        const submitButton = e.target.querySelector('button[type="submit"]');

        // Error mesajını gizle
        errorMessage.classList.add('hidden');

        // Loading state
        buttonText.classList.add('hidden');
        buttonSpinner.classList.remove('hidden');
        submitButton.disabled = true;

        try {
            // API call - Şu anda placeholder
            const response = await loginUser(email, password);

            // Token'ı kaydet
            api.setToken(response.token);

            // Kullanıcı bilgilerini kaydet
            if (rememberMe) {
                localStorage.setItem('user', JSON.stringify(response.user));
            } else {
                sessionStorage.setItem('user', JSON.stringify(response.user));
            }

            // Success - Dashboard'a yönlendir
            window.location.href = 'dashboard.html';

        } catch (error) {
            // Error handling
            console.error('Login error:', error);

            // Error mesajını göster
            document.getElementById('errorText').textContent =
                error.message || 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.';
            errorMessage.classList.remove('hidden');

            // Reset button state
            buttonText.classList.remove('hidden');
            buttonSpinner.classList.add('hidden');
            submitButton.disabled = false;
        }
    });
}

/**
 * Kullanıcının login olup olmadığını kontrol et
 * @returns {boolean}
 */
function isAuthenticated() {
    const token = api.getToken();
    return token !== null && token !== undefined && token !== '';
}

/**
 * Mevcut kullanıcı bilgilerini getir
 * @returns {object|null}
 */
function getCurrentUser() {
    const userFromLocal = localStorage.getItem('user');
    const userFromSession = sessionStorage.getItem('user');

    const userJson = userFromLocal || userFromSession;

    if (userJson) {
        try {
            return JSON.parse(userJson);
        } catch (error) {
            console.error('User parse error:', error);
            return null;
        }
    }

    return null;
}

/**
 * Logout fonksiyonu
 */
async function logout() {
    try {
        // Backend API call (placeholder)
        await logoutUser();

        // Token ve kullanıcı bilgilerini temizle
        api.clearToken();
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');

        // Login sayfasına yönlendir
        window.location.href = 'index.html';

    } catch (error) {
        console.error('Logout error:', error);

        // Error olsa bile local verileri temizle ve yönlendir
        api.clearToken();
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}

/**
 * Protected route kontrolü
 * Eğer kullanıcı login olmamışsa, login sayfasına yönlendir
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

/**
 * Admin role kontrolü
 * @param {object} user 
 * @returns {boolean}
 */
function isAdmin(user) {
    return user && user.role === 'admin';
}

/**
 * Kullanıcı bilgilerini UI'da göster
 */
function displayUserInfo() {
    const user = getCurrentUser();

    if (!user) return;

    // User name
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = user.name || user.email;
    }

    // User initials
    const userInitialsElement = document.getElementById('userInitials');
    if (userInitialsElement) {
        const initials = user.name
            ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
            : user.email[0].toUpperCase();
        userInitialsElement.textContent = initials;
    }
}

/**
 * Token validation ve refresh
 * TODO: Backend hazır olduğunda JWT expiration kontrolü eklenecek
 */
async function validateToken() {
    const token = api.getToken();

    if (!token) {
        return false;
    }

    // TODO: Backend'e token validation request gönder
    // Şimdilik token varsa geçerli kabul et

    try {
        // JWT decode et ve expiration kontrolü yap
        // const payload = JSON.parse(atob(token.split('.')[1]));
        // const exp = payload.exp * 1000;
        // const now = Date.now();

        // if (now >= exp) {
        //     // Token expired - refresh token kullan veya logout
        //     await refreshToken();
        // }

        return true;
    } catch (error) {
        console.error('Token validation error:', error);
        return false;
    }
}

/**
 * Token refresh
 * TODO: Backend hazır olduğunda implement edilecek
 */
async function refreshToken() {
    try {
        // const response = await api.post('/auth/refresh');
        // api.setToken(response.token);
        console.log('Token refresh (Placeholder)');
    } catch (error) {
        console.error('Token refresh error:', error);
        // Refresh başarısız - logout
        logout();
    }
}

// Page load'da authentication kontrolü
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname;

    // Login sayfası değilse authentication kontrolü yap
    if (!currentPage.includes('index.html') && currentPage.includes('frontend')) {
        if (!requireAuth()) {
            return;
        }

        // Kullanıcı bilgilerini göster
        displayUserInfo();

        // Admin sayfası için role kontrolü
        if (currentPage.includes('admin.html')) {
            const user = getCurrentUser();
            if (!isAdmin(user)) {
                alert('Bu sayfaya erişim yetkiniz yok.');
                window.location.href = 'dashboard.html';
                return;
            }
        }
    }

    // Login sayfasında ve zaten authenticated ise dashboard'a yönlendir
    if (currentPage.includes('index.html') && isAuthenticated()) {
        window.location.href = 'dashboard.html';
    }
});

// Auto token refresh (her 5 dakikada bir)
// TODO: Backend hazır olduğunda aktif edilecek
// setInterval(async () => {
//     if (isAuthenticated()) {
//         await validateToken();
//     }
// }, 5 * 60 * 1000);
