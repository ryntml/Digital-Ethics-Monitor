/**
 * Digital Ethics Monitor - API Client
 * 
 * Bu dosya backend API ile iletişim kurmak için kullanılır.
 * Backend hazır - gerçek API endpoint'leri ile bağlantılı.
 */

// API Base URL - Backend adresi
const API_BASE_URL = 'http://localhost:8000';

/**
 * API Client Class
 * JWT token yönetimi ve HTTP istekleri için helper sınıf
 */
class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * JWT token'ı localStorage'dan al
     */
    getToken() {
        return localStorage.getItem('jwt_token');
    }

    /**
     * JWT token'ı localStorage'a kaydet
     */
    setToken(token) {
        localStorage.setItem('jwt_token', token);
    }

    /**
     * JWT token'ı temizle
     */
    clearToken() {
        localStorage.removeItem('jwt_token');
    }

    /**
     * HTTP headers oluştur (JWT token ile)
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    /**
     * Generic HTTP request
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} - API response
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.getHeaders(options.auth !== false),
                    ...options.headers,
                },
            });

            // Token geçersiz veya süresi dolmuş
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/frontend/index.html';
                throw new Error('Unauthorized');
            }

            // Response'u parse et
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'GET',
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'DELETE',
        });
    }
}

// Global API client instance
const api = new APIClient();

/**
 * API Endpoint Functions
 * Backend hazır olduğunda bu fonksiyonlar gerçek API çağrıları yapacaktır
 */

// ============================================
// AUTHENTICATION ENDPOINTS
// ============================================

/**
 * Login - Kullanıcı girişi
 * @param {string} username - email veya username
 * @param {string} password 
 * @returns {Promise<object>} - { access_token, token_type }
 */
async function loginUser(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Giriş başarısız');
        }

        // Token'ı kaydet
        api.setToken(data.access_token);

        // user bilgisini almak için /users/me çağır
        const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${data.access_token}` }
        });
        const user = await userResponse.json();

        return {
            token: data.access_token,
            user: user
        };
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

/**
 * Logout - Kullanıcı çıkışı
 */
async function logoutUser() {
    api.clearToken();
    return { success: true };
}

// ============================================
// DASHBOARD ENDPOINTS (PLACEHOLDER)
// ============================================

/**
 * Dashboard istatistiklerini getir
 * @returns {Promise<object>}
 */
async function getDashboardStats() {
    try {
        const response = await api.get('/stats/dashboard');
        return {
            totalDecisions: response.total_decisions,
            biasCount: response.bias_count,
            biasLevel: response.bias_count > 10 ? 'Yüksek' : response.bias_count > 5 ? 'Orta' : 'Düşük',
            fairnessScore: response.fairness_score,
            systemHealth: response.system_health
        };
    } catch (error) {
        console.error('Dashboard stats error:', error);
        // Fallback değerler
        return {
            totalDecisions: 0,
            biasCount: 0,
            biasLevel: '--',
            fairnessScore: 0,
            systemHealth: 100
        };
    }
}

/**
 * AI kararlarını getir
 * @param {number} limit 
 * @param {number} offset 
 * @returns {Promise<Array>}
 */
async function getDecisions(limit = 10, offset = 0) {
    // TODO: Backend API bağlantısı yapılacak
    // return api.get(`/decisions?limit=${limit}&offset=${offset}`);

    console.log('GET DECISIONS (Placeholder):', { limit, offset });

    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                decisions: [],
                total: 0
            });
        }, 300);
    });
}

/**
 * Bias analiz verilerini getir
 * @returns {Promise<object>}
 */
async function getBiasAnalytics() {
    // TODO: Backend API bağlantısı yapılacak
    // return api.get('/analytics/bias');

    console.log('GET BIAS ANALYTICS (Placeholder)');

    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                demographic_parity: [0.45, 0.55],
                labels: ['Group A', 'Group B']
            });
        }, 300);
    });
}

/**
 * Fairness metriklerini getir
 * @returns {Promise<object>}
 */
async function getFairnessMetrics() {
    // TODO: Backend API bağlantısı yapılacak
    // return api.get('/analytics/fairness');

    console.log('GET FAIRNESS METRICS (Placeholder)');

    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                equalized_odds: 0.87,
                demographic_parity: 0.92,
                equal_opportunity: 0.85
            });
        }, 300);
    });
}

// ============================================
// ADMIN ENDPOINTS
// ============================================

/**
 * Sistem loglarını getir
 * @param {object} filters - { startDate, endDate, logLevel, search, page, pageSize }
 * @returns {Promise<object>}
 */
async function getLogs(filters = {}) {
    try {
        let query = `limit=${filters.pageSize || 100}`;
        if (filters.logLevel) query += `&event_type=${filters.logLevel}`;

        const logs = await api.get(`/admin/logs?${query}`);
        return {
            logs: logs.map(log => ({
                id: log.id,
                timestamp: log.created_at,
                level: log.event_type,
                source: 'System',
                message: log.message,
                hash: log.hash
            })),
            total: logs.length,
            page: 1,
            totalPages: 1
        };
    } catch (error) {
        console.error('Get logs error:', error);
        return { logs: [], total: 0, page: 1, totalPages: 1 };
    }
}

/**
 * AI karar raporlarını getir
 * @param {number} page 
 * @param {number} pageSize 
 * @returns {Promise<object>}
 */
async function getReports(page = 1, pageSize = 10) {
    // TODO: Backend API bağlantısı yapılacak
    // return api.get(`/admin/reports?page=${page}&pageSize=${pageSize}`);

    console.log('GET REPORTS (Placeholder):', { page, pageSize });

    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                reports: [],
                total: 0,
                page: 1,
                totalPages: 1
            });
        }, 300);
    });
}

/**
 * Rapor indir
 * @param {string} reportId 
 * @returns {Promise<Blob>}
 */
async function downloadReport(reportId) {
    // TODO: Backend API bağlantısı yapılacak

    console.log('DOWNLOAD REPORT (Placeholder):', reportId);

    return Promise.resolve(new Blob(['Placeholder report data'], { type: 'application/pdf' }));
}

// Export API client and functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        api,
        APIClient,
        loginUser,
        logoutUser,
        getDashboardStats,
        getDecisions,
        getBiasAnalytics,
        getFairnessMetrics,
        getLogs,
        getReports,
        downloadReport
    };
}
