document.addEventListener('DOMContentLoaded', () => {
    const sectionStorageKey = 'portfolioSectionId';
    sessionStorage.removeItem('portfolioScrollY');
    let isRestoringSection = false;
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }

    const getCurrentSectionId = () => {
        const sectionList = Array.from(document.querySelectorAll('main section[id]'));
        const viewportTop = window.scrollY;
        const viewportBottom = viewportTop + window.innerHeight;
        let bestSection = sectionList[0];
        let bestVisibleHeight = 0;

        sectionList.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            const visibleHeight = Math.min(viewportBottom, sectionBottom) - Math.max(viewportTop, sectionTop);

            if (visibleHeight > bestVisibleHeight) {
                bestVisibleHeight = visibleHeight;
                bestSection = section;
            }
        });

        return bestSection?.id || '';
    };

    const saveCurrentSection = (force = false) => {
        if (isRestoringSection && !force) return;
        const currentSectionId = getCurrentSectionId();
        if (currentSectionId) {
            sessionStorage.setItem(sectionStorageKey, currentSectionId);
        }
    };

    // ==========================================
    // PAGE LOADER
    // ==========================================
    window.addEventListener('load', () => {
        const loader = document.querySelector('.page-loader');
        if (loader) {
            setTimeout(() => {
                loader.classList.add('hidden');
            }, 500);
        }

        // Restore the visible section after refresh, then fall back to direct section links.
        const navigationEntry = performance.getEntriesByType('navigation')[0];
        const isRefresh = navigationEntry?.type === 'reload';
        const savedSectionId = sessionStorage.getItem(sectionStorageKey);
        if (isRefresh && savedSectionId) {
            isRestoringSection = true;
            setTimeout(() => {
                const target = document.getElementById(savedSectionId);
                target?.scrollIntoView({ behavior: 'auto' });
                setTimeout(() => {
                    isRestoringSection = false;
                    saveCurrentSection(true);
                }, 250);
            }, 650);
        } else if (window.location.hash) {
            setTimeout(() => {
                const target = document.getElementById(window.location.hash.slice(1));
                target?.scrollIntoView({ behavior: 'smooth' });
            }, 650);
        }
    });

    window.addEventListener('pagehide', () => {
        saveCurrentSection(true);
    });

    window.addEventListener('beforeunload', () => {
        saveCurrentSection(true);
    });

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            saveCurrentSection(true);
        }
    });

    // Current Year Update
    const currentYear = document.getElementById('current-year');
    if (currentYear) currentYear.textContent = new Date().getFullYear();

    // ==========================================
    // HEADER SCROLL EFFECT
    // ==========================================
    const header = document.querySelector('.header');
    let sectionSaveFrame = null;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        header?.classList.toggle('scrolled', currentScroll > 50);

        if (sectionSaveFrame) return;
        sectionSaveFrame = requestAnimationFrame(() => {
            updateCurrentSection();
            saveCurrentSection();
            sectionSaveFrame = null;
        });
    });

    // Highlight the navigation link for the section currently in view.
    const sections = document.querySelectorAll('main section[id]');
    const sectionLinks = document.querySelectorAll('.nav-link[href^="#"]');

    let currentSectionId = window.location.hash.slice(1);

    const updateCurrentSection = () => {
        if (!sections.length || isRestoringSection) return;

        const nextSectionId = getCurrentSectionId();
        if (!nextSectionId || nextSectionId === currentSectionId) return;

        currentSectionId = nextSectionId;
        sessionStorage.setItem(sectionStorageKey, nextSectionId);
        history.replaceState(null, '', `#${nextSectionId}`);

        sectionLinks.forEach((link) => {
            link.classList.toggle('active', link.getAttribute('href') === `#${nextSectionId}`);
        });
    };

    // ==========================================
    // MOBILE MENU
    // ==========================================
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mainNav = document.getElementById('main-nav');
    const navLinks = document.querySelectorAll('.nav-link');

    if (mobileMenuBtn && mainNav) {
        const closeMobileMenu = () => {
            mobileMenuBtn.classList.remove('active');
            mainNav.classList.remove('active');
        };

        mobileMenuBtn.addEventListener('click', () => {
            mobileMenuBtn.classList.toggle('active');
            mainNav.classList.toggle('active');
        });

        // Close mobile menu on clicking navigation links
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                closeMobileMenu();
            });
        });

        document.addEventListener('click', (event) => {
            if (!mainNav.classList.contains('active')) return;
            if (mainNav.contains(event.target) || mobileMenuBtn.contains(event.target)) return;
            closeMobileMenu();
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeMobileMenu();
            }
        });
    }

    // ==========================================
    // THEME SWITCHER (DARK / LIGHT)
    // ==========================================
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    
    if (savedTheme === 'light' || (!savedTheme && systemPrefersLight)) {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        updateThemeIcon(true);
    } else {
        body.classList.add('dark-theme');
        body.classList.remove('light-theme');
        updateThemeIcon(false);
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isCurrentlyLight = body.classList.contains('light-theme');
            if (isCurrentlyLight) {
                body.classList.remove('light-theme');
                body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
                updateThemeIcon(false);
            } else {
                body.classList.remove('dark-theme');
                body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
                updateThemeIcon(true);
            }
        });
    }

    function updateThemeIcon(isLight) {
        const icon = themeToggle?.querySelector('i');
        if (icon) {
            icon.className = isLight ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    }

    // ==========================================
    // STAGGERED PROJECT CARD ANIMATIONS
    // ==========================================
    const projectCards = document.querySelectorAll('.project-modern-card');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (projectCards.length > 0 && !prefersReducedMotion) {
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        projectCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
            cardObserver.observe(card);
        });
    }

    // ==========================================
    // CUSTOM CURSOR (DESKTOP ONLY)
    // ==========================================
    if (window.innerWidth >= 1024) {
        const cursor = document.createElement('div');
        const cursorDot = document.createElement('div');
        cursor.className = 'custom-cursor';
        cursorDot.className = 'custom-cursor-dot';
        document.body.appendChild(cursor);
        document.body.appendChild(cursorDot);
        document.body.classList.add('custom-cursor-active');

        let mouseX = 0, mouseY = 0;
        let cursorX = 0, cursorY = 0;
        let dotX = 0, dotY = 0;

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            cursor.classList.add('visible');
            cursorDot.classList.add('visible');
        });

        function animateCursor() {
            // Smooth follow for outer cursor
            cursorX += (mouseX - cursorX) * 0.1;
            cursorY += (mouseY - cursorY) * 0.1;
            cursor.style.left = cursorX + 'px';
            cursor.style.top = cursorY + 'px';

            // Faster follow for dot
            dotX += (mouseX - dotX) * 0.2;
            dotY += (mouseY - dotY) * 0.2;
            cursorDot.style.left = dotX + 'px';
            cursorDot.style.top = dotY + 'px';

            requestAnimationFrame(animateCursor);
        }
        animateCursor();

        // Expand on hover
        const hoverElements = document.querySelectorAll('a, button, .btn, .social-icon, .project-modern-card');
        hoverElements.forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.style.transform = 'translate(-50%, -50%) scale(1.5)';
                cursor.style.background = 'rgba(230, 57, 70, 0.2)';
            });
            el.addEventListener('mouseleave', () => {
                cursor.style.transform = 'translate(-50%, -50%) scale(1)';
                cursor.style.background = 'transparent';
            });
        });
    }

    // ==========================================
    // INTERACTIVE PARTICLE CANVAS BACKGROUND
    // ==========================================
    const canvas = document.getElementById('particle-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particles = [];
        
        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2 + 1;
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;
            }

            update() {
                this.x += this.speedX;
                this.y += this.speedY;

                // Wrap around edges
                if (this.x < 0) this.x = canvas.width;
                if (this.x > canvas.width) this.x = 0;
                if (this.y < 0) this.y = canvas.height;
                if (this.y > canvas.height) this.y = 0;
            }

            draw() {
                const isLight = document.body.classList.contains('light-theme');
                ctx.fillStyle = isLight ? 'rgba(230, 57, 70, 0.08)' : 'rgba(230, 57, 70, 0.1)';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const initParticles = () => {
            particles = [];
            const count = Math.min(60, Math.floor(window.innerWidth / 20));
            for (let i = 0; i < count; i++) {
                particles.push(new Particle());
            }
        };
        initParticles();

        // Connect nearby particles with lines
        const drawConnections = () => {
            const maxDistance = 120;
            const isLight = document.body.classList.contains('light-theme');
            const strokeStyle = isLight ? 'rgba(230, 57, 70, 0.03)' : 'rgba(230, 57, 70, 0.04)';
            
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < maxDistance) {
                        ctx.strokeStyle = strokeStyle;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
        };

        const drawFrame = (moveParticles = true) => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                if (moveParticles) p.update();
                p.draw();
            });
            drawConnections();
        };

        const animate = () => {
            drawFrame();
            requestAnimationFrame(animate);
        };

        if (prefersReducedMotion) {
            drawFrame(false);
        } else {
            animate();
        }
    }

    // ==========================================
    // CONTACT FORM VALIDATION & MOCK SUBMIT
    // ==========================================
    const contactForm = document.getElementById('contact-form');
    const toast = document.getElementById('toast');
    const toastCloseBtn = document.getElementById('toast-close-btn');
    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    };

    const submitForm = async (url, form) => {
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: new FormData(form),
        });
        const data = await response.json();
        if (!response.ok || !data.ok) {
            throw new Error(data.message || 'Something went wrong. Please try again.');
        }
        return data;
    };
    
    // Toast Controls
    const showToast = () => {
        if (toast) {
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 5000);
        }
    };
    
    if (toastCloseBtn && toast) {
        toastCloseBtn.addEventListener('click', () => {
            toast.classList.remove('show');
        });
    }

    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = feedbackForm.querySelector('button[type="submit"]');
            const originalText = submitBtn?.innerHTML;

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Sending... <i class="fa-solid fa-spinner fa-spin"></i>';
            }

            const toastTitle = toast?.querySelector('.toast-title');
            const toastBody = toast?.querySelector('.toast-body');

            try {
                await submitForm(feedbackForm.action, feedbackForm);

                if (toastTitle) toastTitle.textContent = 'Feedback received!';
                if (toastBody) toastBody.textContent = 'Thank you for sharing your experience.';

                showToast();
                feedbackForm.reset();
            } catch (error) {
                if (toastTitle) toastTitle.textContent = 'Could not send feedback';
                if (toastBody) toastBody.textContent = error.message;
                showToast();
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    }

    // Email Validator regex helper
    const isValidEmail = (email) => {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    };

    if (contactForm) {
        const inputs = contactForm.querySelectorAll('.cta-form-input');
        
        // Remove validation error on input change
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                const group = input.closest('.cta-form-group');
                if (group) group.classList.remove('invalid');
            });
        });

        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            let hasErrors = false;

            inputs.forEach(input => {
                const group = input.closest('.cta-form-group');
                if (!group) return;

                const value = input.value.trim();
                
                // General empty check
                if (!value) {
                    group.classList.add('invalid');
                    hasErrors = true;
                } else if (input.type === 'email' && !isValidEmail(value)) {
                    // Email check
                    group.classList.add('invalid');
                    const errorSpan = group.querySelector('.error-msg');
                    if (errorSpan) errorSpan.textContent = 'Please enter a valid email';
                    hasErrors = true;
                } else {
                    group.classList.remove('invalid');
                }
            });

            if (!hasErrors) {
                const submitBtn = document.getElementById('btn-submit-contact');
                if (!submitBtn) return;
                const originalText = submitBtn.innerHTML;
                
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'SENDING... <i class="fa-solid fa-spinner fa-spin"></i>';

                submitForm(contactForm.action, contactForm)
                    .then(() => {
                        const toastTitle = toast?.querySelector('.toast-title');
                        const toastBody = toast?.querySelector('.toast-body');
                        if (toastTitle) toastTitle.textContent = 'Message sent!';
                        if (toastBody) toastBody.textContent = "Thank you for reaching out. I'll get back to you soon.";
                        showToast();
                        contactForm.reset();
                    })
                    .catch((error) => {
                        const toastTitle = toast?.querySelector('.toast-title');
                        const toastBody = toast?.querySelector('.toast-body');
                        if (toastTitle) toastTitle.textContent = 'Could not send message';
                        if (toastBody) toastBody.textContent = error.message;
                        showToast();
                    })
                    .finally(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    });
            }
        });
    }
});
