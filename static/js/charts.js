/**
 * Cyber Incident Reporting Portal — Chart.js Configuration
 * Renders analytics charts on the admin dashboard.
 */

// Shared chart colours matching the portal theme
const CHART_COLORS = {
    cyan:      'rgba(0, 212, 255, 1)',
    cyanAlpha: 'rgba(0, 212, 255, 0.25)',
    blue:      'rgba(0, 153, 204, 1)',
    green:     'rgba(0, 230, 118, 1)',
    orange:    'rgba(255, 171, 64, 1)',
    red:       'rgba(255, 82, 82, 1)',
    purple:    'rgba(156, 39, 176, 1)',
    teal:      'rgba(0, 188, 212, 1)',
    palette: [
        'rgba(0, 212, 255, 0.8)',
        'rgba(0, 230, 118, 0.8)',
        'rgba(255, 171, 64, 0.8)',
        'rgba(255, 82, 82, 0.8)',
        'rgba(156, 39, 176, 0.8)',
        'rgba(0, 188, 212, 0.8)',
        'rgba(255, 215, 0, 0.8)',
        'rgba(76, 175, 80, 0.8)',
    ]
};

// Global Chart.js defaults for dark theme
Chart.defaults.color = '#8a9bb5';
Chart.defaults.borderColor = 'rgba(0, 212, 255, 0.08)';
Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";

document.addEventListener('DOMContentLoaded', function () {
    loadCharts();
});

function loadCharts() {
    fetch('/admin/analytics/data')
        .then(resp => resp.json())
        .then(data => {
            renderMonthlyChart(data.monthly);
            renderCategoryChart(data.categories);
            renderResolutionChart(data.resolution);
            renderPriorityChart(data.priority);
            renderDailyChart(data.daily);
        })
        .catch(err => console.error('Failed to load chart data:', err));
}


/* ── Monthly Reports (Line Chart) ────────────────────────── */
function renderMonthlyChart(data) {
    const canvas = document.getElementById('monthlyChart');
    if (!canvas) return;

    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const counts = new Array(12).fill(0);
    if (data) {
        data.forEach(d => { counts[d.month - 1] = d.count; });
    }

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Incidents',
                data: counts,
                borderColor: CHART_COLORS.cyan,
                backgroundColor: CHART_COLORS.cyanAlpha,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: CHART_COLORS.cyan,
                pointBorderColor: '#0a1628',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0d1f3c',
                    borderColor: 'rgba(0,212,255,0.3)',
                    borderWidth: 1,
                    titleColor: '#00d4ff',
                    bodyColor: '#e8edf5',
                }
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}


/* ── Category Distribution (Doughnut Chart) ──────────────── */
function renderCategoryChart(data) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas || !data || data.length === 0) return;

    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.category),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: CHART_COLORS.palette.slice(0, data.length),
                borderColor: '#0a1628',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle',
                    }
                },
                tooltip: {
                    backgroundColor: '#0d1f3c',
                    borderColor: 'rgba(0,212,255,0.3)',
                    borderWidth: 1,
                    titleColor: '#00d4ff',
                    bodyColor: '#e8edf5',
                }
            },
            cutout: '65%',
        }
    });
}


/* ── Resolution Rate (Bar Chart) ─────────────────────────── */
function renderResolutionChart(data) {
    const canvas = document.getElementById('resolutionChart');
    if (!canvas || !data) return;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: ['Total', 'Resolved', 'Pending'],
            datasets: [{
                label: 'Cases',
                data: [data.total, data.resolved, data.total - data.resolved],
                backgroundColor: [
                    CHART_COLORS.cyanAlpha,
                    'rgba(0, 230, 118, 0.6)',
                    'rgba(255, 171, 64, 0.6)',
                ],
                borderColor: [
                    CHART_COLORS.cyan,
                    CHART_COLORS.green,
                    CHART_COLORS.orange,
                ],
                borderWidth: 1,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0d1f3c',
                    borderColor: 'rgba(0,212,255,0.3)',
                    borderWidth: 1,
                }
            },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}


/* ── Priority Distribution (Pie Chart) ───────────────────── */
function renderPriorityChart(data) {
    const canvas = document.getElementById('priorityChart');
    if (!canvas || !data || data.length === 0) return;

    const prioColors = {
        low: CHART_COLORS.green,
        medium: CHART_COLORS.cyan,
        high: CHART_COLORS.orange,
        critical: CHART_COLORS.red,
    };

    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: data.map(d => d.priority.charAt(0).toUpperCase() + d.priority.slice(1)),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: data.map(d => prioColors[d.priority] || CHART_COLORS.cyan),
                borderColor: '#0a1628',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                    }
                },
            }
        }
    });
}


/* ── Daily Reports (Bar Chart) ───────────────────────────── */
function renderDailyChart(data) {
    const canvas = document.getElementById('dailyChart');
    if (!canvas || !data || data.length === 0) return;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'Incidents',
                data: data.map(d => d.count),
                backgroundColor: CHART_COLORS.cyanAlpha,
                borderColor: CHART_COLORS.cyan,
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: { ticks: { maxRotation: 45, font: { size: 10 } } },
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}
