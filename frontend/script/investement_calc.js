const apiBase = '/api/v1/financial_goals';

let chart = null;
let currentData = null;
let currentMode = 'standard'; // 'standard' or 'realValue'

async function calculateInvestment() {
    // Get form values
    const principal = parseInt(document.getElementById('principal').value);
    const monthlyContribution = parseInt(document.getElementById('monthlyContribution').value);
    const years = parseInt(document.getElementById('years').value);
    const annualReturn = parseFloat(document.getElementById('annualReturn').value) / 100;
    const contributionGrowth = parseFloat(document.getElementById('contributionGrowth').value) / 100;
    const taxRate = parseFloat(document.getElementById('taxRate').value) / 100;
    const annualInflation = parseFloat(document.getElementById('annualInflation').value) / 100;

    hideError();
    showLoading(true);
    document.getElementById('statsGrid').style.display = 'none';

    try {
        const url = `${apiBase}/?principal=${principal}&monthly_contribution=${monthlyContribution}&years=${years}&annual_return=${annualReturn}&contribution_growth=${contributionGrowth}&tax_rate=${taxRate}&annual_inflation=${annualInflation}`;

        const response = await fetch(url);
        const data = await response.json();

        if (!data || data.length === 0) {
            showError('Помилка при отриманні даних');
            showLoading(false);
            return;
        }

        currentData = data;
        displayChart(currentMode);
        updateStats(data);

        showLoading(false);
        document.getElementById('statsGrid').style.display = 'grid';
    } catch (error) {
        showError('Помилка завантаження даних: ' + error.message);
        showLoading(false);
    }
}

function displayChart(mode) {
    if (!currentData) return;

    const categories = [];
    const investedData = [];
    const balanceData = [];
    const profitData = [];
    const realValueData = [];

    // Sample data every year for better visualization
    currentData.forEach((item) => {
        if (item.month % 12 === 0) {
            const year = item.month / 12;
            categories.push(`Рік ${year}`);
            investedData.push(item.invested);
            balanceData.push(item.total_balance);
            profitData.push(item.profit);
            realValueData.push(item.real_value);
        }
    });

    if (chart) {
        chart.destroy();
    }

    let series;
    if (mode === 'standard') {
        series = [
            {
                name: 'Інвестовано',
                data: investedData
            },
            {
                name: 'Баланс',
                data: balanceData
            },
            {
                name: 'Прибуток',
                data: profitData
            }
        ];
    } else {
        series = [
            {
                name: 'Реальна вартість',
                data: realValueData
            }
        ];
    }

    const options = {
        series: series,
        chart: {
            type: 'line',
            height: 450,
            toolbar: {
                show: true,
                tools: {
                    download: true,
                    selection: false,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: false,
                    reset: true
                }
            },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 500,
                dynamicAnimation: {
                    speed: 300
                }
            }
        },
        stroke: {
            curve: 'straight',
            width: 3
        },
        colors: mode === 'standard'
            ? ['#93c5fd', '#10b981', '#fbbf24']
            : ['#ef4444'],
        dataLabels: {
            enabled: false
        },
        markers: {
            size: 5,
            hover: {
                size: 7
            }
        },
        xaxis: {
            categories: categories,
            title: {
                text: 'Період',
                style: {
                    fontSize: '14px',
                    fontWeight: 600
                }
            }
        },
        yaxis: {
            title: {
                text: 'Сума ($)',
                style: {
                    fontSize: '14px',
                    fontWeight: 600
                }
            },
            labels: {
                formatter: function (val) {
                    return formatCurrency(val);
                }
            }
        },
        tooltip: {
            shared: true,
            intersect: false,
            y: {
                formatter: function (val) {
                    return formatCurrency(val);
                }
            }
        },
        legend: {
            position: 'top',
            horizontalAlign: 'center',
            fontSize: '14px',
            fontWeight: 600,
            markers: {
                width: 12,
                height: 12,
                radius: 6
            }
        },
        grid: {
            borderColor: '#f0f0f0',
            strokeDashArray: 4
        }
    };

    chart = new ApexCharts(document.querySelector("#investmentChart"), options);
    chart.render();
}

function updateStats(data) {
    if (!data || data.length === 0) return;

    const lastMonth = data[data.length - 1];

    document.getElementById('totalInvested').textContent = formatCurrency(lastMonth.invested);
    document.getElementById('finalBalance').textContent = formatCurrency(lastMonth.total_balance);
    document.getElementById('totalProfit').textContent = formatCurrency(lastMonth.profit);
    document.getElementById('realValue').textContent = formatCurrency(lastMonth.real_value);
}

function formatCurrency(value) {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(2) + ' млн $';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + ' тис $';
    }
    return value.toFixed(2) + ' $';
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    const chartDiv = document.getElementById('investmentChart');

    if (show) {
        loading.classList.add('show');
        chartDiv.style.display = 'none';
    } else {
        loading.classList.remove('show');
        chartDiv.style.display = 'block';
    }
}

function showError(message) {
    const errorElement = document.getElementById('errorMsg');
    errorElement.textContent = message;
    errorElement.classList.add('show');
}

function hideError() {
    document.getElementById('errorMsg').classList.remove('show');
}

// Event listeners
document.getElementById('calculateBtn').addEventListener('click', calculateInvestment);

document.getElementById('standardBtn').addEventListener('click', () => {
    currentMode = 'standard';
    document.getElementById('standardBtn').classList.add('active');
    document.getElementById('realValueBtn').classList.remove('active');
    if (currentData) {
        displayChart(currentMode);
    }
});

document.getElementById('realValueBtn').addEventListener('click', () => {
    currentMode = 'realValue';
    document.getElementById('realValueBtn').classList.add('active');
    document.getElementById('standardBtn').classList.remove('active');
    if (currentData) {
        displayChart(currentMode);
    }
});

// Load initial calculation on page load
window.addEventListener('load', () => {
    calculateInvestment();
});
