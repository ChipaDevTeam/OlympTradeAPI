// Trading Panel JavaScript - Advanced Interactive Trading Simulation
class TradingPanel {
    constructor() {
        this.chart = null;
        this.priceData = [];
        this.currentPair = 'EURUSD';
        this.timeframe = '5m';
        this.isRunning = false;
        this.trades = [];
        this.balance = 10000;
        this.todayPnl = 245.80;
        
        this.basePrices = {
            'EURUSD': 1.0842,
            'GBPUSD': 1.2134,
            'USDJPY': 149.82,
            'AUDUSD': 0.6758
        };

        this.init();
    }

    init() {
        this.initChart();
        this.bindEvents();
        this.startPriceSimulation();
        this.updateMarketOverview();
    }

    initChart() {
        const ctx = document.getElementById('tradingChart');
        if (!ctx) return;

        // Generate initial candlestick data
        this.generateInitialData();

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.priceData.map((_, i) => this.formatTime(i)),
                datasets: [{
                    label: this.currentPair,
                    data: this.priceData,
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 1,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#8B5CF6',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 2
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
                        backgroundColor: 'rgba(15, 11, 26, 0.9)',
                        titleColor: '#E5E7EB',
                        bodyColor: '#CBD5E1',
                        borderColor: '#8B5CF6',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                return `${this.currentPair}: ${context.parsed.y.toFixed(4)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(139, 92, 246, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94A3B8',
                            maxTicksLimit: 8
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(139, 92, 246, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94A3B8',
                            callback: function(value) {
                                return value.toFixed(4);
                            }
                        },
                        position: 'right'
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    generateInitialData() {
        const basePrice = this.basePrices[this.currentPair];
        this.priceData = [];
        
        let currentPrice = basePrice;
        for (let i = 0; i < 50; i++) {
            // Simulate realistic price movement
            const volatility = this.getVolatility();
            const change = (Math.random() - 0.5) * volatility;
            currentPrice += change;
            this.priceData.push(currentPrice);
        }
    }

    getVolatility() {
        const volatilities = {
            'EURUSD': 0.0005,
            'GBPUSD': 0.0008,
            'USDJPY': 0.05,
            'AUDUSD': 0.0006
        };
        return volatilities[this.currentPair] || 0.0005;
    }

    startPriceSimulation() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.simulationInterval = setInterval(() => {
            this.updatePrice();
            this.updateChart();
            this.checkTrades();
        }, 1000);
    }

    updatePrice() {
        const volatility = this.getVolatility();
        const change = (Math.random() - 0.5) * volatility;
        const lastPrice = this.priceData[this.priceData.length - 1];
        const newPrice = lastPrice + change;
        
        this.priceData.push(newPrice);
        
        // Keep only last 50 data points
        if (this.priceData.length > 50) {
            this.priceData.shift();
        }

        // Update current price display
        const currentPriceElement = document.getElementById('currentPrice');
        if (currentPriceElement) {
            currentPriceElement.textContent = this.formatPrice(newPrice);
            
            // Add price change animation
            currentPriceElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                currentPriceElement.style.transform = 'scale(1)';
            }, 200);
        }
    }

    updateChart() {
        if (!this.chart) return;

        this.chart.data.labels = this.priceData.map((_, i) => this.formatTime(i));
        this.chart.data.datasets[0].data = this.priceData;
        
        // Update chart color based on price trend
        const isUpTrend = this.priceData[this.priceData.length - 1] > this.priceData[this.priceData.length - 2];
        this.chart.data.datasets[0].borderColor = isUpTrend ? '#10B981' : '#EF4444';
        this.chart.data.datasets[0].backgroundColor = isUpTrend ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)';
        
        this.chart.update('none');
    }

    bindEvents() {
        // Pair selector
        const pairSelector = document.getElementById('pairSelector');
        if (pairSelector) {
            pairSelector.addEventListener('change', (e) => {
                this.changePair(e.target.value);
            });
        }

        // Trade pair selector
        const tradePair = document.getElementById('tradePair');
        if (tradePair) {
            tradePair.addEventListener('change', (e) => {
                this.currentPair = e.target.value;
            });
        }

        // Timeframe selector
        const timeframeSelector = document.getElementById('timeframeSelector');
        if (timeframeSelector) {
            timeframeSelector.addEventListener('change', (e) => {
                this.timeframe = e.target.value;
                this.regenerateChart();
            });
        }
    }

    changePair(newPair) {
        this.currentPair = newPair;
        this.generateInitialData();
        this.updateChart();
        
        // Update trade pair selector to match
        const tradePairSelect = document.getElementById('tradePair');
        if (tradePairSelect) {
            tradePairSelect.value = newPair;
        }
    }

    regenerateChart() {
        this.generateInitialData();
        if (this.chart) {
            this.chart.data.labels = this.priceData.map((_, i) => this.formatTime(i));
            this.chart.data.datasets[0].data = this.priceData;
            this.chart.update();
        }
    }

    formatTime(index) {
        const now = new Date();
        const timeMultipliers = {
            '1m': 60000,
            '5m': 300000,
            '15m': 900000,
            '1h': 3600000
        };
        
        const timeOffset = timeMultipliers[this.timeframe] || 300000;
        const time = new Date(now.getTime() - (49 - index) * timeOffset);
        
        return time.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    formatPrice(price) {
        if (this.currentPair === 'USDJPY') {
            return price.toFixed(2);
        }
        return price.toFixed(4);
    }

    updateMarketOverview() {
        setInterval(() => {
            const marketItems = document.querySelectorAll('.market-item');
            marketItems.forEach(item => {
                const symbol = item.querySelector('.symbol').textContent;
                const priceElement = item.querySelector('.price');
                const changeElement = item.querySelector('.change');
                
                if (priceElement && changeElement) {
                    const basePair = symbol.replace('/', '');
                    if (this.basePrices[basePair]) {
                        // Simulate price change
                        const volatility = this.getVolatilityForPair(basePair);
                        const change = (Math.random() - 0.5) * volatility;
                        this.basePrices[basePair] += change;
                        
                        // Update display
                        const price = this.basePrices[basePair];
                        priceElement.textContent = this.formatPriceForPair(price, basePair);
                        
                        // Update change percentage
                        const changePercent = ((change / price) * 100).toFixed(2);
                        changeElement.textContent = `${change > 0 ? '+' : ''}${changePercent}%`;
                        changeElement.className = `change ${change > 0 ? 'up' : 'down'}`;
                    }
                }
            });
        }, 3000);
    }

    getVolatilityForPair(pair) {
        const volatilities = {
            'EURUSD': 0.0003,
            'GBPUSD': 0.0004,
            'USDJPY': 0.03,
            'AUDUSD': 0.0003
        };
        return volatilities[pair] || 0.0003;
    }

    formatPriceForPair(price, pair) {
        return pair === 'USDJPY' ? price.toFixed(2) : price.toFixed(4);
    }

    checkTrades() {
        // Check for trade expirations and update P&L
        this.trades = this.trades.filter(trade => {
            if (Date.now() - trade.timestamp > trade.duration * 1000) {
                // Trade expired, calculate result
                const currentPrice = this.priceData[this.priceData.length - 1];
                const isWin = (trade.direction === 'up' && currentPrice > trade.entryPrice) ||
                             (trade.direction === 'down' && currentPrice < trade.entryPrice);
                
                const payout = isWin ? trade.amount * 0.85 : -trade.amount;
                this.balance += payout;
                this.todayPnl += payout;
                
                this.updateBalanceDisplay();
                this.addTradeToHistory(trade, isWin, payout);
                
                return false; // Remove trade from active trades
            }
            return true;
        });
    }

    updateBalanceDisplay() {
        const balanceElement = document.getElementById('accountBalance');
        const pnlElement = document.getElementById('todayPnl');
        const positionsElement = document.getElementById('openPositions');
        
        if (balanceElement) {
            balanceElement.textContent = this.formatCurrency(this.balance);
        }
        
        if (pnlElement) {
            pnlElement.textContent = `${this.todayPnl > 0 ? '+' : ''}${this.formatCurrency(this.todayPnl)}`;
            pnlElement.className = `value ${this.todayPnl > 0 ? 'profit' : 'loss'}`;
        }
        
        if (positionsElement) {
            positionsElement.textContent = this.trades.length.toString();
        }
    }

    addTradeToHistory(trade, isWin, payout) {
        const tradesList = document.getElementById('tradesList');
        if (!tradesList) return;

        const tradeElement = document.createElement('div');
        tradeElement.className = `trade-item ${isWin ? 'win' : 'loss'}`;
        
        tradeElement.innerHTML = `
            <div class="trade-info">
                <span class="trade-pair">${trade.pair}</span>
                <span class="trade-direction">${trade.direction === 'up' ? '↑' : '↓'} ${trade.direction === 'up' ? 'Higher' : 'Lower'}</span>
            </div>
            <div class="trade-result">
                <span class="trade-amount">${this.formatCurrency(trade.amount)}</span>
                <span class="trade-pnl ${isWin ? 'profit' : 'loss'}">${payout > 0 ? '+' : ''}${this.formatCurrency(payout)}</span>
            </div>
        `;

        // Add to top of list
        tradesList.insertBefore(tradeElement, tradesList.firstChild);

        // Keep only last 5 trades visible
        while (tradesList.children.length > 5) {
            tradesList.removeChild(tradesList.lastChild);
        }

        // Add animation
        tradeElement.style.opacity = '0';
        tradeElement.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            tradeElement.style.transition = 'all 0.5s ease';
            tradeElement.style.opacity = '1';
            tradeElement.style.transform = 'translateY(0)';
        }, 100);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }
}

// Trade placement function (global scope for button onclick)
function placeTrade(direction) {
    const pair = document.getElementById('tradePair')?.value || 'EURUSD';
    const amount = parseFloat(document.getElementById('tradeAmount')?.value || 10);
    const duration = parseInt(document.getElementById('tradeDuration')?.value || 300);
    
    if (!tradingPanel) return;
    
    // Validation
    if (amount < 1 || amount > tradingPanel.balance) {
        showNotification('Invalid trade amount', 'error');
        return;
    }
    
    // Create trade object
    const trade = {
        id: Date.now(),
        pair: pair,
        direction: direction,
        amount: amount,
        duration: duration,
        entryPrice: tradingPanel.priceData[tradingPanel.priceData.length - 1],
        timestamp: Date.now()
    };
    
    // Add to active trades
    tradingPanel.trades.push(trade);
    tradingPanel.balance -= amount; // Reserve trade amount
    
    // Update displays
    tradingPanel.updateBalanceDisplay();
    
    // Show success notification
    showNotification(`Trade placed: ${pair} ${direction.toUpperCase()} $${amount}`, 'success');
    
    // Add visual feedback to buttons
    const buttons = document.querySelectorAll('.trade-btn');
    buttons.forEach(btn => {
        btn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            btn.style.transform = 'scale(1)';
        }, 150);
    });
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        background: ${type === 'success' ? 'linear-gradient(135deg, #10B981, #059669)' : 
                    type === 'error' ? 'linear-gradient(135deg, #EF4444, #DC2626)' : 
                    'linear-gradient(135deg, #8B5CF6, #A855F7)'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        font-weight: 600;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Initialize trading panel when DOM is loaded
let tradingPanel;
document.addEventListener('DOMContentLoaded', function() {
    tradingPanel = new TradingPanel();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (tradingPanel && tradingPanel.simulationInterval) {
        clearInterval(tradingPanel.simulationInterval);
    }
});
