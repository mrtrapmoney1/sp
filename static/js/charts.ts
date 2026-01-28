/**
 * Charts Module - TypeScript
 * Handles Chart.js visualizations for analytics
 */

// =============================================================================
// Type Definitions
// =============================================================================

interface CallInfo {
    CallStatus?: string;
    call_status?: string;
    WarrantyType?: string;
    warranty_type?: string;
    ProductInfo_SPBrandDesc?: string;
    brand?: string;
    ProductInfo_SPProductDesc?: string;
    product?: string;
    ScheduleDate?: string;
    schedule_date?: string;
}

interface ChartData {
    labels: string[];
    values: number[];
}

// =============================================================================
// Chart Instances
// =============================================================================

let warrantyChart: any = null;
let volumeChart: any = null;

// =============================================================================
// Initialize Charts
// =============================================================================

function initializeCharts(calls: CallInfo[]): void {
    if (!calls || calls.length === 0) return;

    initializeWarrantyChart(calls);
    initializeVolumeChart(calls);
}

// =============================================================================
// Warranty Breakdown Chart (Doughnut)
// =============================================================================

function initializeWarrantyChart(calls: CallInfo[]): void {
    const canvas = document.getElementById('warranty-chart') as HTMLCanvasElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Destroy existing chart
    if (warrantyChart) {
        warrantyChart.destroy();
    }

    const data = processWarrantyData(calls);

    warrantyChart = new (window as any).Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    '#0d6efd', // Blue
                    '#6610f2', // Indigo
                    '#6f42c1', // Purple
                    '#d63384', // Pink
                    '#dc3545', // Red
                    '#fd7e14', // Orange
                    '#ffc107', // Yellow
                    '#198754', // Green
                    '#20c997', // Teal
                    '#0dcaf0', // Cyan
                ],
                borderWidth: 2,
                borderColor: '#ffffff',
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 10,
                        font: {
                            size: 12,
                        },
                    },
                },
                title: {
                    display: false,
                },
                tooltip: {
                    callbacks: {
                        label: function(context: any) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        },
                    },
                },
            },
        },
    });
}

function processWarrantyData(calls: CallInfo[]): ChartData {
    const counts: { [key: string]: number } = {};

    calls.forEach(call => {
        const warranty = call.WarrantyType || call.warranty_type || 'Unknown';
        counts[warranty] = (counts[warranty] || 0) + 1;
    });

    // Sort by count descending
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);

    return {
        labels: sorted.map(([label]) => label),
        values: sorted.map(([, value]) => value),
    };
}

// =============================================================================
// Call Volume Trend Chart (Line)
// =============================================================================

function initializeVolumeChart(calls: CallInfo[]): void {
    const canvas = document.getElementById('volume-chart') as HTMLCanvasElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Destroy existing chart
    if (volumeChart) {
        volumeChart.destroy();
    }

    const data = processVolumeData(calls);

    volumeChart = new (window as any).Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Service Calls',
                data: data.values,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#0d6efd',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false,
                },
                title: {
                    display: false,
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        font: {
                            size: 11,
                        },
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 11,
                        },
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                    },
                },
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false,
            },
        },
    });
}

function processVolumeData(calls: CallInfo[]): ChartData {
    const dateCounts: { [key: string]: number } = {};

    calls.forEach(call => {
        const dateStr = call.ScheduleDate || call.schedule_date || '';
        if (!dateStr) return;

        try {
            const date = new Date(dateStr);
            const dateKey = date.toISOString().split('T')[0]; // YYYY-MM-DD
            dateCounts[dateKey] = (dateCounts[dateKey] || 0) + 1;
        } catch {
            // Skip invalid dates
        }
    });

    // Sort by date ascending
    const sorted = Object.entries(dateCounts).sort((a, b) => a[0].localeCompare(b[0]));

    return {
        labels: sorted.map(([date]) => {
            const d = new Date(date);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }),
        values: sorted.map(([, count]) => count),
    };
}

// =============================================================================
// Product Type Distribution Chart (Bar)
// =============================================================================

function initializeProductTypeChart(calls: CallInfo[]): void {
    const canvas = document.getElementById('product-type-chart') as HTMLCanvasElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const data = processProductTypeData(calls);

    new (window as any).Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Calls by Product Type',
                data: data.values,
                backgroundColor: [
                    'rgba(13, 110, 253, 0.7)',
                    'rgba(102, 16, 242, 0.7)',
                    'rgba(111, 66, 193, 0.7)',
                    'rgba(214, 51, 132, 0.7)',
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(253, 126, 20, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(25, 135, 84, 0.7)',
                ],
                borderColor: [
                    '#0d6efd',
                    '#6610f2',
                    '#6f42c1',
                    '#d63384',
                    '#dc3545',
                    '#fd7e14',
                    '#ffc107',
                    '#198754',
                ],
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false,
                },
                title: {
                    display: false,
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                    },
                },
            },
        },
    });
}

function processProductTypeData(calls: CallInfo[]): ChartData {
    const counts: { [key: string]: number } = {};

    calls.forEach(call => {
        const product = call.ProductInfo_SPProductDesc || call.product || 'Unknown';
        counts[product] = (counts[product] || 0) + 1;
    });

    // Sort by count descending
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);

    // Take top 8
    const top8 = sorted.slice(0, 8);

    return {
        labels: top8.map(([label]) => label),
        values: top8.map(([, value]) => value),
    };
}

// =============================================================================
// Brand Performance Chart (Horizontal Bar)
// =============================================================================

function initializeBrandChart(calls: CallInfo[]): void {
    const canvas = document.getElementById('brand-chart') as HTMLCanvasElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const data = processBrandData(calls);

    new (window as any).Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Calls by Brand',
                data: data.values,
                backgroundColor: 'rgba(13, 110, 253, 0.7)',
                borderColor: '#0d6efd',
                borderWidth: 1,
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false,
                },
                title: {
                    display: false,
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                    },
                },
                y: {
                    grid: {
                        display: false,
                    },
                },
            },
        },
    });
}

function processBrandData(calls: CallInfo[]): ChartData {
    const counts: { [key: string]: number } = {};

    calls.forEach(call => {
        const brand = call.ProductInfo_SPBrandDesc || call.brand || 'Unknown';
        counts[brand] = (counts[brand] || 0) + 1;
    });

    // Sort by count descending
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);

    // Take top 10
    const top10 = sorted.slice(0, 10);

    return {
        labels: top10.map(([label]) => label),
        values: top10.map(([, value]) => value),
    };
}

// =============================================================================
// Destroy All Charts
// =============================================================================

function destroyAllCharts(): void {
    if (warrantyChart) {
        warrantyChart.destroy();
        warrantyChart = null;
    }
    if (volumeChart) {
        volumeChart.destroy();
        volumeChart = null;
    }
}

// =============================================================================
// Export Functions
// =============================================================================

if (typeof window !== 'undefined') {
    (window as any).initializeCharts = initializeCharts;
    (window as any).initializeWarrantyChart = initializeWarrantyChart;
    (window as any).initializeVolumeChart = initializeVolumeChart;
    (window as any).initializeProductTypeChart = initializeProductTypeChart;
    (window as any).initializeBrandChart = initializeBrandChart;
    (window as any).destroyAllCharts = destroyAllCharts;
}
