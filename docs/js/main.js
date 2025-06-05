// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initScrollAnimations();
    initHeroChart();
    initPriceUpdates();
    initSmoothScrolling();
});

// Navigation functionality
function initNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');

    // Mobile menu toggle
    hamburger?.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            hamburger?.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(15, 11, 26, 0.98)';
            navbar.style.boxShadow = '0 10px 30px rgba(139, 92, 246, 0.1)';
        } else {
            navbar.style.background = 'rgba(15, 11, 26, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });
}

// Scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .doc-card, .section-title, .section-subtitle');
    animateElements.forEach(el => observer.observe(el));
}

// Hero chart initialization
function initHeroChart() {
    const ctx = document.getElementById('heroChart');
    if (!ctx) return;

    // Generate sample price data
    const generatePriceData = (count = 20) => {
        const data = [];
        let price = 1.0842;
        
        for (let i = 0; i < count; i++) {
            price += (Math.random() - 0.5) * 0.001;
            data.push(price);
        }
        return data;
    };

    const labels = Array.from({length: 20}, (_, i) => `${i + 1}`);
    const priceData = generatePriceData();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'EUR/USD',
                data: priceData,
                borderColor: '#8B5CF6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
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
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            },
            elements: {
                point: {
                    radius: 0
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Real-time price updates simulation
function initPriceUpdates() {
    const priceElements = {
        eurUsd: document.getElementById('eurUsdPrice'),
        gbpUsd: document.getElementById('gbpUsdPrice'),
        currentPrice: document.getElementById('currentPrice')
    };

    const initialPrices = {
        eurUsd: 1.0842,
        gbpUsd: 1.2134,
        currentPrice: 1.0842
    };

    // Update prices every 2 seconds
    setInterval(() => {
        Object.keys(initialPrices).forEach(key => {
            const element = priceElements[key];
            if (!element) return;

            // Generate price change
            const change = (Math.random() - 0.5) * 0.002;
            initialPrices[key] += change;

            // Update display
            element.textContent = initialPrices[key].toFixed(4);

            // Add visual feedback for price change
            element.classList.remove('up', 'down');
            if (change > 0) {
                element.classList.add('up');
            } else if (change < 0) {
                element.classList.add('down');
            }

            // Flash effect
            element.style.transform = 'scale(1.05)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        });

        // Update price change indicator
        const priceChangeElement = document.getElementById('priceChange');
        if (priceChangeElement) {
            const change = (Math.random() - 0.5) * 0.002;
            const changePercent = (change / initialPrices.currentPrice * 100).toFixed(2);
            const changeValue = change > 0 ? `+${change.toFixed(4)}` : change.toFixed(4);
            
            priceChangeElement.textContent = `${changeValue} (${changePercent}%)`;
            priceChangeElement.className = change > 0 ? 'price-change up' : 'price-change down';
        }
    }, 2000);
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Utility functions
function formatPrice(price, decimals = 4) {
    return parseFloat(price).toFixed(decimals);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

function getRandomPrice(basePrice, volatility = 0.001) {
    const change = (Math.random() - 0.5) * volatility;
    return basePrice + change;
}

// Export functions for use in other modules
window.MainJS = {
    formatPrice,
    formatCurrency,
    getRandomPrice
};
