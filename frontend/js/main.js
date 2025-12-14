/**
 * Digital Ethics Monitor - Main Application Logic
 * 
 * Dashboard ve admin panel için ana uygulama mantığı
 * Backend API ile entegre edilecektir
 */

/**
 * Dashboard initialization
 */
async function initializeDashboard() {
    console.log('Initializing Dashboard...');

    try {
        // Load dashboard stats
        await loadDashboardStats();

        // Initialize charts
        await initializeCharts();

        // Load recent decisions
        await loadRecentDecisions();

        // Set up auto-refresh
        setupAutoRefresh();

        // Update last update time
        updateLastUpdateTime();

    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

/**
 * Load dashboard statistics
 */
async function loadDashboardStats() {
    try {
        // TODO: Backend API call
        const stats = await getDashboardStats();

        // Update UI
        updateElement('totalDecisions', stats.totalDecisions);
        updateElement('biasCount', stats.biasCount);
        updateElement('biasLevel', stats.biasLevel);
        updateElement('fairnessScore', stats.fairnessScore.toFixed(2));
        updateElement('systemHealth', stats.systemHealth + '%');

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

/**
 * Load recent decisions table
 */
async function loadRecentDecisions() {
    try {
        // TODO: Backend API call
        const data = await getDecisions(10, 0);

        const tableBody = document.getElementById('decisionsTableBody');
        if (!tableBody) return;

        if (data.decisions.length === 0) {
            tableBody.innerHTML = `
                <tr class="border-b border-white/5">
                    <td colspan="6" class="text-center py-8 text-gray-500">
                        Henüz karar verisi bulunmuyor
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = data.decisions.map(decision => `
            <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="py-3 px-4">${formatDateTime(decision.timestamp)}</td>
                <td class="py-3 px-4 font-mono text-xs">${decision.id}</td>
                <td class="py-3 px-4">${decision.model}</td>
                <td class="py-3 px-4">${decision.result}</td>
                <td class="py-3 px-4">
                    ${getBiasRiskBadge(decision.biasRisk)}
                </td>
                <td class="py-3 px-4">
                    ${getStatusBadge(decision.status)}
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading recent decisions:', error);
    }
}

/**
 * Admin panel initialization
 */
async function initializeAdminPanel() {
    console.log('Initializing Admin Panel...');

    try {
        // Load logs
        await loadLogs();

        // Load reports
        await loadReports();

    } catch (error) {
        console.error('Admin panel initialization error:', error);
    }
}

/**
 * Load system logs
 */
let currentLogsPage = 1;
const logsPageSize = 20;

async function loadLogs(filters = {}) {
    try {
        // TODO: Backend API call
        const data = await getLogs({
            ...filters,
            page: currentLogsPage,
            pageSize: logsPageSize
        });

        updateElement('totalLogs', data.total);
        updateElement('currentPage', data.page);
        updateElement('totalPages', data.totalPages);

        const tableBody = document.getElementById('logsTableBody');
        if (!tableBody) return;

        if (data.logs.length === 0) {
            tableBody.innerHTML = `
                <tr class="border-b border-white/5">
                    <td colspan="6" class="text-center py-8 text-gray-500">
                        Log verisi bulunamadı
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = data.logs.map(log => `
            <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="py-3 px-4 text-xs">${formatDateTime(log.timestamp)}</td>
                <td class="py-3 px-4 font-mono text-xs">${log.id}</td>
                <td class="py-3 px-4">
                    ${getLogLevelBadge(log.level)}
                </td>
                <td class="py-3 px-4 text-xs">${log.source}</td>
                <td class="py-3 px-4 text-xs">${truncateText(log.message, 50)}</td>
                <td class="py-3 px-4 font-mono text-xs text-gray-500">${log.hash.substring(0, 8)}...</td>
            </tr>
        `).join('');

        // Update pagination buttons
        updatePaginationButtons(data.page, data.totalPages);

    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

/**
 * Load AI decision reports
 */
async function loadReports() {
    try {
        // TODO: Backend API call
        const data = await getReports(1, 10);

        const tableBody = document.getElementById('reportsTableBody');
        if (!tableBody) return;

        if (data.reports.length === 0) {
            tableBody.innerHTML = `
                <tr class="border-b border-white/5">
                    <td colspan="7" class="text-center py-8 text-gray-500">
                        Rapor bulunamadı
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = data.reports.map(report => `
            <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="py-3 px-4 font-mono text-xs">${report.id}</td>
                <td class="py-3 px-4 text-xs">${formatDate(report.date)}</td>
                <td class="py-3 px-4">${report.model}</td>
                <td class="py-3 px-4">${report.decisionCount}</td>
                <td class="py-3 px-4">
                    <span class="text-${report.biasRate > 0.1 ? 'red' : 'green'}-400">
                        ${(report.biasRate * 100).toFixed(1)}%
                    </span>
                </td>
                <td class="py-3 px-4">
                    <span class="text-${report.fairnessScore < 0.7 ? 'red' : 'green'}-400">
                        ${report.fairnessScore.toFixed(2)}
                    </span>
                </td>
                <td class="py-3 px-4">
                    <button 
                        onclick="downloadReportById('${report.id}')"
                        class="text-purple-400 hover:text-purple-300 transition-colors"
                    >
                        İndir
                    </button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

/**
 * Apply filters for admin logs
 */
function applyFilters() {
    const startDate = document.getElementById('startDate')?.value;
    const endDate = document.getElementById('endDate')?.value;
    const logLevel = document.getElementById('logLevel')?.value;
    const searchQuery = document.getElementById('searchQuery')?.value;

    const filters = {};

    if (startDate) filters.startDate = startDate;
    if (endDate) filters.endDate = endDate;
    if (logLevel) filters.logLevel = logLevel;
    if (searchQuery) filters.search = searchQuery;

    currentLogsPage = 1;
    loadLogs(filters);
}

/**
 * Pagination functions
 */
function previousPage() {
    if (currentLogsPage > 1) {
        currentLogsPage--;
        loadLogs();
    }
}

function nextPage() {
    currentLogsPage++;
    loadLogs();
}

function updatePaginationButtons(currentPage, totalPages) {
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');

    if (prevButton) {
        prevButton.disabled = currentPage <= 1;
    }

    if (nextButton) {
        nextButton.disabled = currentPage >= totalPages;
    }
}

/**
 * Download report by ID
 */
async function downloadReportById(reportId) {
    try {
        console.log('Downloading report:', reportId);
        // TODO: Backend API call
        // const blob = await downloadReport(reportId);
        // const url = window.URL.createObjectURL(blob);
        // const a = document.createElement('a');
        // a.href = url;
        // a.download = `report_${reportId}.pdf`;
        // a.click();
        alert('Rapor indirme özelliği backend entegrasyonundan sonra aktif olacaktır.');
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Rapor indirilemedi');
    }
}

/**
 * Auto-refresh setup
 */
function setupAutoRefresh() {
    // Her 30 saniyede bir verileri güncelle
    setInterval(async () => {
        const currentPage = window.location.pathname;

        if (currentPage.includes('dashboard.html')) {
            await loadDashboardStats();
            await refreshCharts();
            await loadRecentDecisions();
            updateLastUpdateTime();
        }
    }, 30000); // 30 seconds
}

/**
 * Update last update time
 */
function updateLastUpdateTime() {
    const element = document.getElementById('lastUpdate');
    if (element) {
        const now = new Date();
        element.textContent = `Son Güncelleme: ${now.toLocaleTimeString('tr-TR')}`;
    }
}

/**
 * Utility Functions
 */

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function formatDateTime(timestamp) {
    if (!timestamp) return '--';
    const date = new Date(timestamp);
    return date.toLocaleString('tr-TR');
}

function formatDate(date) {
    if (!date) return '--';
    return new Date(date).toLocaleDateString('tr-TR');
}

function truncateText(text, maxLength) {
    if (!text) return '--';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function getBiasRiskBadge(risk) {
    const colors = {
        low: 'green',
        medium: 'yellow',
        high: 'red'
    };
    const labels = {
        low: 'Düşük',
        medium: 'Orta',
        high: 'Yüksek'
    };
    const color = colors[risk] || 'gray';
    const label = labels[risk] || '--';
    return `<span class="badge badge-${color === 'yellow' ? 'warning' : color === 'red' ? 'danger' : 'success'}">${label}</span>`;
}

function getStatusBadge(status) {
    const colors = {
        approved: 'success',
        pending: 'warning',
        rejected: 'danger'
    };
    const color = colors[status] || 'info';
    return `<span class="badge badge-${color}">${status}</span>`;
}

function getLogLevelBadge(level) {
    const colors = {
        info: 'info',
        warning: 'warning',
        error: 'danger',
        critical: 'danger'
    };
    const color = colors[level.toLowerCase()] || 'info';
    return `<span class="badge badge-${color}">${level.toUpperCase()}</span>`;
}

/**
 * Page initialization
 */
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname;

    if (currentPage.includes('dashboard.html')) {
        initializeDashboard();
    } else if (currentPage.includes('admin.html')) {
        initializeAdminPanel();
    }
});
