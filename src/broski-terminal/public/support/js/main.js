// Hyperfocus Support Page - JavaScript Functionality
'use strict';

class HyperfocusSupport {
    constructor() { this.init(); }
    init() {
        this.setupAccessibilityControls();
        this.setupAnimations();
        this.setupProgressBars();
        this.setupMetricsUpdater();
        this.setupFormEnhancements();
        this.setupAnalytics();
        console.log('🚀 Hyperfocus Support initialized');
    }

    setupAccessibilityControls() {
        const motionToggle = document.getElementById('motionToggle');
        if (motionToggle) {
            motionToggle.addEventListener('click', () => {
                document.body.classList.toggle('reduced-motion');
                const isReduced = document.body.classList.contains('reduced-motion');
                motionToggle.setAttribute('aria-pressed', isReduced);
                localStorage.setItem('reduced-motion', isReduced);
                this.showNotification(isReduced ? 'Animations reduced' : 'Animations enabled');
            });
            const savedMotionPref = localStorage.getItem('reduced-motion') === 'true';
            if (savedMotionPref) { document.body.classList.add('reduced-motion'); motionToggle.setAttribute('aria-pressed', 'true'); }
        }

        const fontToggle = document.getElementById('fontToggle');
        if (fontToggle) {
            fontToggle.addEventListener('click', () => {
                document.body.classList.toggle('dyslexic-font');
                const on = document.body.classList.contains('dyslexic-font');
                fontToggle.setAttribute('aria-pressed', on);
                localStorage.setItem('dyslexic-font', on);
                this.showNotification(on ? 'Dyslexic-friendly font enabled' : 'Default font restored');
            });
            const saved = localStorage.getItem('dyslexic-font') === 'true';
            if (saved) { document.body.classList.add('dyslexic-font'); fontToggle.setAttribute('aria-pressed', 'true'); }
        }

        const focusToggle = document.getElementById('focusToggle');
        if (focusToggle) {
            focusToggle.addEventListener('click', () => {
                document.body.classList.toggle('focus-mode');
                const on = document.body.classList.contains('focus-mode');
                focusToggle.setAttribute('aria-pressed', on);
                localStorage.setItem('focus-mode', on);
                this.showNotification(on ? 'Focus mode enabled' : 'Focus mode disabled');
            });
            const saved = localStorage.getItem('focus-mode') === 'true';
            if (saved) { document.body.classList.add('focus-mode'); focusToggle.setAttribute('aria-pressed', 'true'); }
        }

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.body.classList.add('reduced-motion');
            if (motionToggle) motionToggle.setAttribute('aria-pressed', 'true');
        }
    }

    setupAnimations() {
        const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => { if (entry.isIntersecting) { entry.target.style.opacity = '1'; entry.target.style.transform = 'translateY(0)'; } });
        }, observerOptions);
        document.querySelectorAll('.section').forEach(section => {
            section.style.opacity = '0'; section.style.transform = 'translateY(50px)'; section.style.transition = 'opacity 0.6s ease, transform 0.6s ease'; observer.observe(section);
        });
        document.querySelectorAll('.tier-card, .support-card, .contact-item').forEach(card => {
            card.addEventListener('mouseenter', () => { if (!document.body.classList.contains('reduced-motion')) { card.style.transform = 'translateY(-10px)'; } });
            card.addEventListener('mouseleave', () => { card.style.transform = ''; });
        });
    }

    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => { if (entry.isIntersecting) { setTimeout(() => { bar.style.transition = 'width 2s ease'; }, 500); observer.unobserve(entry.target); } });
            });
            observer.observe(bar);
        });
    }

    setupMetricsUpdater() {
        const updateMetrics = () => {
            const supportersEl = document.getElementById('live-supporters');
            const discordCountEl = document.getElementById('discord-count');
            const fundingTextEl = document.getElementById('funding-text');
            if (supportersEl) supportersEl.textContent = '0';
            if (discordCountEl) discordCountEl.textContent = '0+';
            const fundingProgress = document.getElementById('funding-progress');
            if (fundingProgress && fundingTextEl) {
                fundingProgress.style.width = '0%';
                fundingProgress.setAttribute('aria-valuenow', '0');
                fundingTextEl.textContent = '£0 of £10,000 monthly goal reached (0%)';
            }
        };
        setTimeout(updateMetrics, 500);
    }

    animateNumber(element, start, end) {
        const duration = 2000; const startTime = performance.now();
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime; const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(start + (end - start) * this.easeOutCubic(progress));
            element.textContent = current.toLocaleString();
            if (progress < 1) { requestAnimationFrame(animate); }
        };
        requestAnimationFrame(animate);
    }

    easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

    setupFormEnhancements() {
        document.querySelectorAll('.donation-btn').forEach(btn => {
            btn.addEventListener('focus', function() { this.style.outline = '3px solid var(--focus-color)'; this.style.outlineOffset = '2px'; });
            btn.addEventListener('blur', function() { this.style.outline = ''; this.style.outlineOffset = ''; });
            btn.addEventListener('keydown', function(e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); } });
        });
        document.querySelectorAll('.skip-link').forEach(link => {
            link.addEventListener('click', (e) => { e.preventDefault(); const target = document.querySelector(link.getAttribute('href')); if (target) { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); (target instanceof HTMLElement) && target.focus(); } });
        });
    }

    setupAnalytics() {
        document.querySelectorAll('.donation-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.textContent.trim(); const href = btn.href || btn.getAttribute('data-action');
                console.log('Donation action clicked:', action, href);
                this.trackEvent('donation_click', { action, reduced_motion: document.body.classList.contains('reduced-motion'), dyslexic_font: document.body.classList.contains('dyslexic-font'), focus_mode: document.body.classList.contains('focus-mode') });
                this.showClickFeedback(btn);
            });
        });
        document.querySelectorAll('.accessibility-btn').forEach(btn => { btn.addEventListener('click', () => { this.trackEvent('accessibility_control_used', { control: btn.id, timestamp: new Date().toISOString() }); }); });
        this.setupScrollTracking();
    }

    setupScrollTracking() {
        const trackingPoints = [25, 50, 75, 90, 100]; const tracked = new Set();
        const trackScroll = () => {
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            trackingPoints.forEach(point => { if (scrollPercent >= point && !tracked.has(point)) { tracked.add(point); this.trackEvent('scroll_depth', { percent: point }); } });
        };
        window.addEventListener('scroll', this.throttle(trackScroll, 250));
    }

    trackEvent(eventName, properties = {}) { console.log(`📊 Event: ${eventName}`, properties); }
    showNotification(message) {
        const notification = document.createElement('div'); notification.className = 'notification'; notification.textContent = message; notification.style.cssText = `position: fixed; top: 80px; right: 20px; background: var(--neon-purple); color: white; padding: 12px 20px; border-radius: 8px; z-index: 1000; animation: slideIn 0.3s ease;`;
        document.body.appendChild(notification); setTimeout(() => { notification.style.animation = 'slideOut 0.3s ease forwards'; setTimeout(() => notification.remove(), 300); }, 3000);
    }
    showClickFeedback(element) { if (document.body.classList.contains('reduced-motion')) return; element.style.transform = 'scale(0.95)'; setTimeout(() => { element.style.transform = ''; }, 150); }
    throttle(func, limit) { let inThrottle; return function() { if (!inThrottle) { func.apply(this, arguments); inThrottle = true; setTimeout(() => inThrottle = false, limit); } }; }
}

const style = document.createElement('style');
style.textContent = `@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } } @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }`;
document.head.appendChild(style);
document.addEventListener('DOMContentLoaded', () => { new HyperfocusSupport(); });
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') { console.log('👀 Page visible - user returned'); } });
window.addEventListener('error', (e) => { console.error('💥 JavaScript error:', e.error); });
document.addEventListener('keydown', (e) => { if (e.altKey && e.key === 'm') { e.preventDefault(); document.getElementById('motionToggle')?.click(); } if (e.altKey && e.key === 'f') { e.preventDefault(); document.getElementById('fontToggle')?.click(); } if (e.altKey && e.key === 'z') { e.preventDefault(); document.getElementById('focusToggle')?.click(); } });
