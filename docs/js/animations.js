// Advanced animations using GSAP
document.addEventListener('DOMContentLoaded', function() {
    initGSAPAnimations();
    initScrollTriggerAnimations();
    initMouseFollowEffects();
    initTypingAnimation();
});

function initGSAPAnimations() {
    // Set initial states for animations
    gsap.set('.hero-text > *', { opacity: 0, y: 50 });
    gsap.set('.hero-visual', { opacity: 0, x: 100 });
    gsap.set('.feature-card', { opacity: 0, y: 30 });
    gsap.set('.doc-card', { opacity: 0, scale: 0.9 });

    // Hero section animation timeline
    const heroTL = gsap.timeline({ delay: 0.5 });
    
    heroTL
        .to('.hero-title', { 
            opacity: 1, 
            y: 0, 
            duration: 1.2, 
            ease: 'power3.out' 
        })
        .to('.hero-description', { 
            opacity: 1, 
            y: 0, 
            duration: 1, 
            ease: 'power3.out' 
        }, '-=0.8')
        .to('.hero-buttons', { 
            opacity: 1, 
            y: 0, 
            duration: 1, 
            ease: 'power3.out' 
        }, '-=0.6')
        .to('.hero-stats', { 
            opacity: 1, 
            y: 0, 
            duration: 1, 
            ease: 'power3.out' 
        }, '-=0.4')
        .to('.hero-visual', { 
            opacity: 1, 
            x: 0, 
            duration: 1.5, 
            ease: 'power3.out' 
        }, '-=1.2');

    // Floating elements animation
    gsap.to('.floating-element', {
        y: -20,
        duration: 4,
        ease: 'power2.inOut',
        yoyo: true,
        repeat: -1,
        stagger: 0.5
    });

    // Trading card floating animation
    gsap.to('.trading-card', {
        y: -10,
        duration: 3,
        ease: 'power2.inOut',
        yoyo: true,
        repeat: -1
    });

    // Gradient text animation
    gsap.to('.gradient-text', {
        backgroundPosition: '200% center',
        duration: 3,
        ease: 'none',
        repeat: -1,
        yoyo: true
    });
}

function initScrollTriggerAnimations() {
    // Register ScrollTrigger plugin (assuming it's loaded)
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }

    // Features section animation
    gsap.timeline({
        scrollTrigger: {
            trigger: '.features',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    })
    .to('.features .section-title', { 
        opacity: 1, 
        y: 0, 
        duration: 1, 
        ease: 'power3.out' 
    })
    .to('.features .section-subtitle', { 
        opacity: 1, 
        y: 0, 
        duration: 1, 
        ease: 'power3.out' 
    }, '-=0.7')
    .to('.feature-card', { 
        opacity: 1, 
        y: 0, 
        duration: 0.8, 
        ease: 'power3.out',
        stagger: 0.15
    }, '-=0.5');

    // Trading section animation
    gsap.timeline({
        scrollTrigger: {
            trigger: '.trading-section',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    })
    .to('.trading-section .section-title', { 
        opacity: 1, 
        y: 0, 
        duration: 1, 
        ease: 'power3.out' 
    })
    .to('.dashboard-left', { 
        opacity: 1, 
        x: 0, 
        duration: 1.2, 
        ease: 'power3.out' 
    }, '-=0.5')
    .to('.dashboard-right', { 
        opacity: 1, 
        x: 0, 
        duration: 1.2, 
        ease: 'power3.out' 
    }, '-=1');

    // Documentation section animation
    gsap.timeline({
        scrollTrigger: {
            trigger: '.documentation',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    })
    .to('.documentation .section-title', { 
        opacity: 1, 
        y: 0, 
        duration: 1, 
        ease: 'power3.out' 
    })
    .to('.doc-card', { 
        opacity: 1, 
        scale: 1, 
        duration: 0.8, 
        ease: 'back.out(1.7)',
        stagger: 0.2
    }, '-=0.5');

    // Shop CTA section animation
    gsap.timeline({
        scrollTrigger: {
            trigger: '.shop-cta',
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
        }
    })
    .to('.cta-text', { 
        opacity: 1, 
        x: 0, 
        duration: 1.2, 
        ease: 'power3.out' 
    })
    .to('.shop-card', { 
        opacity: 1, 
        x: 0, 
        duration: 1.2, 
        ease: 'power3.out' 
    }, '-=0.8');
}

function initMouseFollowEffects() {
    // Create cursor follower
    const cursor = document.createElement('div');
    cursor.className = 'cursor-follower';
    cursor.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.8) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        transition: transform 0.1s ease;
        display: none;
    `;
    document.body.appendChild(cursor);

    // Mouse movement effect
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        cursor.style.display = 'block';
    });

    // Smooth cursor following
    function updateCursor() {
        cursorX += (mouseX - cursorX) * 0.1;
        cursorY += (mouseY - cursorY) * 0.1;
        
        cursor.style.left = cursorX - 10 + 'px';
        cursor.style.top = cursorY - 10 + 'px';
        
        requestAnimationFrame(updateCursor);
    }
    updateCursor();

    // Interactive elements glow effect
    const interactiveElements = document.querySelectorAll('.btn, .nav-link, .trade-btn, .chart-select');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            gsap.to(cursor, { scale: 2, duration: 0.3, ease: 'power2.out' });
            gsap.to(element, { 
                boxShadow: '0 0 30px rgba(139, 92, 246, 0.4)', 
                duration: 0.3 
            });
        });
        
        element.addEventListener('mouseleave', () => {
            gsap.to(cursor, { scale: 1, duration: 0.3, ease: 'power2.out' });
            gsap.to(element, { 
                boxShadow: 'none', 
                duration: 0.3 
            });
        });
    });
}

function initTypingAnimation() {
    const texts = [
        'Professional Trading Made Simple',
        'Build Powerful Trading Bots',
        'Automate Your Strategies',
        'Real-time Market Analysis'
    ];
    
    let currentTextIndex = 0;
    let currentCharIndex = 0;
    let isDeleting = false;
    const typeSpeed = 100;
    const deleteSpeed = 50;
    const pauseTime = 2000;

    const heroTitle = document.querySelector('.hero-title');
    if (!heroTitle) return;

    const staticPart = '<span class="gradient-text">';
    const staticEnd = '</span><br>Made Simple';

    function typeText() {
        const currentText = texts[currentTextIndex];
        
        if (isDeleting) {
            currentCharIndex--;
        } else {
            currentCharIndex++;
        }

        const displayText = currentText.substring(0, currentCharIndex);
        heroTitle.innerHTML = staticPart + displayText + staticEnd;

        let nextDelay = isDeleting ? deleteSpeed : typeSpeed;

        if (!isDeleting && currentCharIndex === currentText.length) {
            nextDelay = pauseTime;
            isDeleting = true;
        } else if (isDeleting && currentCharIndex === 0) {
            isDeleting = false;
            currentTextIndex = (currentTextIndex + 1) % texts.length;
            nextDelay = typeSpeed;
        }

        setTimeout(typeText, nextDelay);
    }

    // Start typing animation after initial load
    setTimeout(typeText, 3000);
}

// Particle system for background
function initParticleSystem() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        opacity: 0.5;
    `;
    
    document.body.appendChild(canvas);
    
    let particles = [];
    const particleCount = 50;
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2
        };
    }
    
    function initParticles() {
        particles = [];
        for (let i = 0; i < particleCount; i++) {
            particles.push(createParticle());
        }
    }
    
    function updateParticles() {
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        });
    }
    
    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            const gradient = ctx.createRadialGradient(
                particle.x, particle.y, 0,
                particle.x, particle.y, particle.size
            );
            gradient.addColorStop(0, `rgba(139, 92, 246, ${particle.opacity})`);
            gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fill();
        });
    }
    
    function animate() {
        updateParticles();
        drawParticles();
        requestAnimationFrame(animate);
    }
    
    resizeCanvas();
    initParticles();
    animate();
    
    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });
}

// Initialize particle system
initParticleSystem();

// Performance optimization - pause animations when tab is not visible
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        gsap.globalTimeline.pause();
    } else {
        gsap.globalTimeline.resume();
    }
});

// Smooth reveal animation for elements entering viewport
function initRevealOnScroll() {
    const revealElements = document.querySelectorAll('.feature-card, .doc-card, .market-item, .balance-item');
    
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                gsap.to(entry.target, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: 'power3.out',
                    delay: Math.random() * 0.3
                });
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    });
    
    revealElements.forEach(el => {
        gsap.set(el, { opacity: 0, y: 30 });
        revealObserver.observe(el);
    });
}

// Initialize reveal animations
initRevealOnScroll();

// Export animation functions for external use
window.Animations = {
    initGSAPAnimations,
    initScrollTriggerAnimations,
    initMouseFollowEffects,
    initTypingAnimation,
    initParticleSystem,
    initRevealOnScroll
};
