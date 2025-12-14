/**
 * Digital Ethics Monitor - Chart.js Visualizations
 * 
 * AI bias ve fairness metriklerini görselleştirmek için Chart.js kullanımı
 * Backend'den gelen gerçek verilerle güncellenecektir
 */

// Chart.js global configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    Chart.defaults.font.family = 'Inter, sans-serif';
}

/**
 * Bias Distribution Chart
 * Demographic Parity görselleştirmesi
 */
let biasChart = null;

async function createBiasChart() {
    const canvas = document.getElementById('biasChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Destroy existing chart
    if (biasChart) {
        biasChart.destroy();
    }

    // TODO: Backend'den gerçek veri alınacak
    // const data = await getBiasAnalytics();

    // Placeholder data
    const data = {
        labels: ['Grup A', 'Grup B', 'Grup C', 'Grup D'],
        values: [0.45, 0.55, 0.42, 0.58]
    };

    biasChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Bias Oranı',
                data: data.values,
                backgroundColor: [
                    'rgba(139, 92, 246, 0.6)',
                    'rgba(59, 130, 246, 0.6)',
                    'rgba(239, 68, 68, 0.6)',
                    'rgba(245, 158, 11, 0.6)',
                ],
                borderColor: [
                    'rgba(139, 92, 246, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)',
                ],
                borderWidth: 2,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function (context) {
                            return `Bias: ${(context.parsed.y * 100).toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        callback: function (value) {
                            return (value * 100) + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Fairness Metrics Chart
 * Equalized Odds, Demographic Parity vb. metrikler
 */
let fairnessChart = null;

async function createFairnessChart() {
    const canvas = document.getElementById('fairnessChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Destroy existing chart
    if (fairnessChart) {
        fairnessChart.destroy();
    }

    // TODO: Backend'den gerçek veri alınacak
    // const data = await getFairnessMetrics();

    // Placeholder data
    const data = {
        labels: ['Equalized Odds', 'Demographic Parity', 'Equal Opportunity'],
        values: [0.87, 0.92, 0.85]
    };

    fairnessChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Adalet Metrikleri',
                data: data.values,
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(16, 185, 129, 1)',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function (context) {
                            return `Skor: ${(context.parsed.r * 100).toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2,
                        callback: function (value) {
                            return (value * 100) + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Decision Timeline Chart
 * Zaman içinde AI kararlarının trend analizi
 */
let timelineChart = null;

async function createTimelineChart() {
    const canvas = document.getElementById('timelineChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Destroy existing chart
    if (timelineChart) {
        timelineChart.destroy();
    }

    // TODO: Backend'den gerçek veri alınacak
    // const data = await getDecisionTimeline();

    // Placeholder data - Son 24 saat
    const hours = [];
    const decisions = [];
    const biasDetected = [];

    for (let i = 23; i >= 0; i--) {
        hours.push(`${i}:00`);
        decisions.push(Math.floor(Math.random() * 50) + 20);
        biasDetected.push(Math.floor(Math.random() * 5));
    }

    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Toplam Karar',
                    data: decisions,
                    borderColor: 'rgba(139, 92, 246, 1)',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: 'rgba(139, 92, 246, 1)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2
                },
                {
                    label: 'Bias Tespit Edildi',
                    data: biasDetected,
                    borderColor: 'rgba(239, 68, 68, 1)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: 'rgba(239, 68, 68, 1)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: {
                        color: '#94a3b8',
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

/**
 * Tüm chartları oluştur
 */
async function initializeCharts() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded');
        return;
    }

    try {
        await createBiasChart();
        await createFairnessChart();
        await createTimelineChart();
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

/**
 * Chartları yeniden yükle (veri güncellemesi için)
 */
async function refreshCharts() {
    console.log('Refreshing charts with new data...');
    await initializeCharts();
}

/**
 * Chart resize handler
 */
window.addEventListener('resize', () => {
    if (biasChart) biasChart.resize();
    if (fairnessChart) fairnessChart.resize();
    if (timelineChart) timelineChart.resize();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createBiasChart,
        createFairnessChart,
        createTimelineChart,
        initializeCharts,
        refreshCharts
    };
}
