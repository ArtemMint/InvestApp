const apiBase = '/api/v1/stock';

let chart = null;
let candlestickSeries = null;
let volumeSeries = null;
let ma200Series = null;
let ma50Series = null;
let ma20Series = null;
let ma9Series = null;
let recommendationsChart = null;
let targetPriceChart = null;
let earningsChart = null;

// Initialize chart
function initChart() {
    const chartElement = document.getElementById('chartCanvas');

    if (chart) {
        chart.remove();
    }

    chart = LightweightCharts.createChart(chartElement, {
        width: chartElement.clientWidth,
        height: 600,
        layout: {
            background: {color: '#ffffff'},
            textColor: '#333',
        },
        grid: {
            vertLines: {color: '#f0f0f0'},
            horzLines: {color: '#f0f0f0'},
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#d1d4dc',
        },
        timeScale: {
            borderColor: '#d1d4dc',
            timeVisible: true,
            secondsVisible: false,
        },
    });

    candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        priceScaleId: 'right',
    });

    volumeSeries = chart.addHistogramSeries({
        color: '#93c5fd',
        priceFormat: {
            type: 'volume',
        },
        priceScaleId: 'volume',
    });

    ma200Series = chart.addLineSeries({
        color: '#6b7280',
        lineWidth: 2,
        priceScaleId: 'right',
        title: 'SMA200',
    });

    ma50Series = chart.addLineSeries({
        color: '#3b82f6',
        lineWidth: 2,
        priceScaleId: 'right',
        title: 'SMA50',
    });

    ma20Series = chart.addLineSeries({
        color: '#fbbf24',
        lineWidth: 2,
        priceScaleId: 'right',
        title: 'SMA20',
    });

    ma9Series = chart.addLineSeries({
        color: '#10b981',
        lineWidth: 2,
        priceScaleId: 'right',
        title: 'SMA9',
    });

    // Configure price scale for candlesticks (top 75% of chart)
    chart.priceScale('right').applyOptions({
        scaleMargins: {
            top: 0.1,
            bottom: 0.3,
        },
    });

    // Configure price scale for volume (bottom 20% of chart)
    chart.priceScale('volume').applyOptions({
        scaleMargins: {
            top: 0.8,
            bottom: 0,
        },
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        chart.applyOptions({width: chartElement.clientWidth});
    });
}

async function loadStockData() {
    const ticker = document.getElementById('ticker').value.trim().toUpperCase();
    const period = document.getElementById('period').value;
    let interval = null;

    if (!ticker) {
        showError('Будь ласка, введіть тікер акції');
        return;
    }

    if (period === '1d') {
        interval = '5m'; // Override interval for 1 day period
    } else if (period === '5d') {
        interval = '15m'; // Override interval for 5 days period
    } else if (period === '1mo') {
        interval = '1h'; // Override interval for 1 month period
    } else if (period === '3mo') {
        interval = '1d'; // Override interval for 3 months period
    } else if (period == '6mo') {
        interval = '1d'; // Override interval for 6 months period
    } else if (period === '1y') {
        interval = '1d'; // Override interval for 1 year period
    } else if (period === 'ytd') {
        interval = '1d'; // Override interval for year-to-date period
    } else if (period === '5y') {
        interval = '1wk'; // Override interval for 5 years period
    } else {
        showError('Невірний період. Будь ласка, виберіть правильний період.');
    }


    hideError();
    showLoading(true);
    document.getElementById('statsGrid').style.display = 'none';

    try {
        const response = await apiFetch(`${apiBase}/?stock_ticker=${ticker}&period=${period}&interval=${interval}`);
        const data = await response.json();

        if (data.error) {
            showError(data.error);
            showLoading(false);
            return;
        }

        if (!data.data || data.data.length === 0) {
            showError('Немає даних для відображення');
            showLoading(false);
            return;
        }

        // Update header info
        document.getElementById('tickerDisplay').textContent = data.ticker;
        document.getElementById('chartInfo').textContent = `Період: ${data.period}`;

        // Process and display data
        displayChart(data.data);
        updateStats(data.data);

        // Load all analytics
        loadAllAnalytics(ticker);

        showLoading(false);
        document.getElementById('statsGrid').style.display = 'grid';
    } catch (error) {
        showError('Помилка завантаження даних: ' + error.message);
        showLoading(false);
    }
}

function displayChart(stockData) {
    if (!chart) {
        initChart();
    }

    // Convert data to chart format
    const candleData = stockData.map(item => ({
        time: new Date(item.time).getTime() / 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
    }));

    const volumeData = stockData.map(item => ({
        time: new Date(item.time).getTime() / 1000,
        value: item.volume,
        color: item.close >= item.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)',
    }));

    const ma200Data = stockData.flatMap(item => {
        if (item.ma200 === undefined || item.ma200 === null) return [];

        return {
            time: new Date(item.time).getTime() / 1000,
            value: item.ma200
        };
    });

    const ma50Data = stockData.flatMap(item => {
        if (item.ma50 === undefined || item.ma50 === null) return [];

        return {
            time: new Date(item.time).getTime() / 1000,
            value: item.ma50
        };
    });

    const ma20Data = stockData.flatMap(item => {
        if (item.ma20 === undefined || item.ma20 === null) return [];

        return {
            time: new Date(item.time).getTime() / 1000,
            value: item.ma20
        };
    });

    const ma9Data = stockData.flatMap(item => {
        if (item.ma9 === undefined || item.ma9 === null) return [];

        return {
            time: new Date(item.time).getTime() / 1000,
            value: item.ma9
        };
    });

    candlestickSeries.setData(candleData);
    volumeSeries.setData(volumeData);
    ma200Series.setData(ma200Data);
    ma50Series.setData(ma50Data);
    ma20Series.setData(ma20Data);
    ma9Series.setData(ma9Data);

    // Fit content
    chart.timeScale().fitContent();
}

function updateStats(stockData) {
    if (stockData.length === 0) return;

    const latestData = stockData[stockData.length - 1];
    const firstData = stockData[0];

    const currentPrice = latestData.close;
    const priceChange = currentPrice - firstData.close;
    const priceChangePercent = ((priceChange / firstData.close) * 100).toFixed(2);

    const highPrice = Math.max(...stockData.map(d => d.high));
    const lowPrice = Math.min(...stockData.map(d => d.low));
    const totalVolume = stockData.reduce((sum, d) => sum + d.volume, 0);

    // Update stats
    document.getElementById('currentPrice').textContent = `${currentPrice.toFixed(2)}`;

    const changeElement = document.getElementById('currentPrice');
    const changeSign = priceChange >= 0 ? '+' : '';
    changeElement.textContent = `${currentPrice.toFixed(2)}  ${changeSign}${priceChange.toFixed(2)} (${changeSign}${priceChangePercent}%)`;
    changeElement.className = `stat-value ${priceChange >= 0 ? 'positive' : 'negative'}`;

    document.getElementById('highPrice').textContent = `${highPrice.toFixed(2)}`;
    document.getElementById('lowPrice').textContent = `${lowPrice.toFixed(2)}`;
    document.getElementById('totalVolume').textContent = formatVolume(totalVolume);
}

function formatVolume(volume) {
    if (volume >= 1e9) return (volume / 1e9).toFixed(2) + 'B';
    if (volume >= 1e6) return (volume / 1e6).toFixed(2) + 'M';
    if (volume >= 1e3) return (volume / 1e3).toFixed(2) + 'K';
    return volume.toString();
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    const chartCanvas = document.getElementById('chartCanvas');

    if (show) {
        loading.classList.add('show');
        chartCanvas.style.display = 'none';
    } else {
        loading.classList.remove('show');
        chartCanvas.style.display = 'block';
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

async function loadAllAnalytics(ticker) {
    const analyticsGrid = document.getElementById('analyticsGrid');
    analyticsGrid.style.display = 'none';

    try {
        // Load all three endpoints in parallel
        const [recommendations, targetPrice, earnings] = await Promise.all([
            apiFetch(`${apiBase}/recommendations?stock_ticker=${ticker}`).then(r => r.json()).catch(() => null),
            apiFetch(`${apiBase}/price_target?stock_ticker=${ticker}`).then(r => r.json()).catch(() => null),
            apiFetch(`${apiBase}/earnings_history?stock_ticker=${ticker}`).then(r => r.json()).catch(() => null)
        ]);

        let hasData = false;

        if (recommendations && !recommendations.error && recommendations.strongBuy !== undefined) {
            displayRecommendations(recommendations);
            hasData = true;
        }

        if (targetPrice && !targetPrice.error && targetPrice.mean) {
            displayTargetPrice(targetPrice);
            hasData = true;
        }

        if (earnings && !earnings.error && earnings.epsActual) {
            displayEarnings(earnings);
            hasData = true;
        }

        if (hasData) {
            analyticsGrid.style.display = 'grid';
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

async function loadRecommendations(ticker) {
    try {
        const response = await apiFetch(`${apiBase}/recommendations?stock_ticker=${ticker}`);
        const data = await response.json();

        if (data.error || !data.strongBuy) {
            document.getElementById('recommendationsContainer').style.display = 'none';
            return;
        }

        displayRecommendations(data);
        document.getElementById('recommendationsContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading recommendations:', error);
        document.getElementById('recommendationsContainer').style.display = 'none';
    }
}

function displayRecommendations(data) {
    const categories = ['Сильна купівля', 'Купівля', 'Утримувати', 'Продаж', 'Сильний продаж'];
    const values = [
        data.strongBuy || 0,
        data.buy || 0,
        data.hold || 0,
        data.sell || 0,
        data.strongSell || 0
    ];

    // Filter out zero values
    const filteredData = categories.map((cat, idx) => ({
        category: cat,
        value: values[idx]
    })).filter(item => item.value > 0);

    if (recommendationsChart) {
        recommendationsChart.destroy();
    }

    const options = {
        series: filteredData.map(item => item.value),
        chart: {
            type: 'donut',
            height: 350,
        },
        labels: filteredData.map(item => item.category),
        colors: ['#10b981', '#6ee7b7', '#93c5fd', '#fbbf24', '#ef4444'],
        legend: {
            position: 'bottom',
            fontSize: '14px',
        },
        plotOptions: {
            pie: {
                donut: {
                    size: '65%',
                    labels: {
                        show: true,
                        total: {
                            show: true,
                            label: 'Всього',
                            fontSize: '16px',
                            fontWeight: 600,
                        }
                    }
                }
            }
        },
        dataLabels: {
            enabled: true,
            formatter: function (val, opts) {
                return opts.w.config.series[opts.seriesIndex];
            },
        },
        tooltip: {
            y: {
                formatter: function (value) {
                    return value + ' аналітик' + (value > 1 ? 'ів' : '');
                }
            }
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    height: 300
                },
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };

    recommendationsChart = new ApexCharts(document.querySelector("#recommendationsChart"), options);
    recommendationsChart.render();
}

function displayTargetPrice(data) {
    if (targetPriceChart) {
        targetPriceChart.destroy();
    }

    const options = {
        series: [{
            name: 'Ціна',
            data: [
                {x: 'Поточна', y: data.current || 0},
                {x: 'Середня', y: data.mean || 0}
            ]
        }],
        chart: {
            type: 'bar',
            height: 350,
            toolbar: {show: false}
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                distributed: true,
                dataLabels: {
                    position: 'top'
                }
            }
        },
        colors: ['#93c5fd', '#10b981'],
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return '$' + val.toFixed(2);
            },
            offsetY: -20,
            style: {
                fontSize: '12px',
                colors: ["#304758"]
            }
        },
        xaxis: {
            categories: ['Поточна', 'Цільова'],
        },
        yaxis: {
            title: {
                text: 'Ціна ($)'
            },
            labels: {
                formatter: function (val) {
                    return '$' + val.toFixed(0);
                }
            }
        },
        legend: {show: false},
        tooltip: {
            y: {
                formatter: function (val) {
                    return '$' + val.toFixed(2);
                }
            }
        }
    };

    targetPriceChart = new ApexCharts(document.querySelector("#targetPriceChart"), options);
    targetPriceChart.render();
}

function displayEarnings(data) {
    if (earningsChart) {
        earningsChart.destroy();
    }

    // Convert timestamps to dates
    const dates = Object.keys(data.epsActual).map(ts => {
        const date = new Date(ts);
        return date.toLocaleDateString('uk-UA', {year: 'numeric', month: 'short'});
    });

    const actual = Object.values(data.epsActual);
    const estimate = Object.values(data.epsEstimate);

    const options = {
        series: [
            {
                name: 'Фактичний EPS',
                data: actual
            },
            {
                name: 'Прогноз EPS',
                data: estimate
            }
        ],
        chart: {
            type: 'bar',
            height: 350,
            toolbar: {show: false}
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                dataLabels: {
                    position: 'top'
                }
            }
        },
        colors: ['#10b981', '#93c5fd'],
        dataLabels: {
            enabled: true,
            formatter: function (val) {
                return val.toFixed(2);
            },
            offsetY: -20,
            style: {
                fontSize: '11px',
                colors: ["#304758"]
            }
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
        },
        xaxis: {
            categories: dates,
        },
        yaxis: {
            title: {
                text: 'EPS ($)'
            },
            labels: {
                formatter: function (val) {
                    return val.toFixed(2);
                }
            }
        },
        fill: {
            opacity: 1
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return '$' + val.toFixed(2);
                }
            }
        },
        legend: {
            position: 'top',
            horizontalAlign: 'center'
        }
    };

    earningsChart = new ApexCharts(document.querySelector("#earningsChart"), options);
    earningsChart.render();
}

// Event listeners
document.getElementById('loadBtn').addEventListener('click', loadStockData);

// Allow Enter key to load data
document.getElementById('ticker').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') loadStockData();
});

// Load initial data
window.addEventListener('load', () => {
    initChart();
    loadStockData();
});