document.addEventListener('DOMContentLoaded', function() {
    // FAQ Accordion Logic for Mobile
    function initMobileFAQ() {
        // STRICTLY restrict to mobile devices
        if (window.innerWidth > 479) return;

        // Only run if we haven't already initialized (check if mobile answers exist)
        if (document.querySelector('.mobile-faq-answer')) return;

        const faqLinks = document.querySelectorAll('.faq-link');
        
        faqLinks.forEach(link => {
            const tabId = link.getAttribute('data-w-tab');
            const contentPane = document.querySelector(`.faq-tab-pane[data-w-tab="${tabId}"]`);
            
            if (contentPane) {
                // Create a new container for the mobile answer
                const answerDiv = document.createElement('div');
                answerDiv.className = 'mobile-faq-answer';
                answerDiv.innerHTML = contentPane.innerHTML;
                
                // Insert AFTER the link (accordion style)
                if (link.nextSibling) {
                    link.parentNode.insertBefore(answerDiv, link.nextSibling);
                } else {
                    link.parentNode.appendChild(answerDiv);
                }
                
                // Use capture phase (true) to catch event before Webflow
                link.addEventListener('click', function(e) {
                    // Double check we are on mobile
                    if (window.innerWidth > 479) return; 

                    // Stop Webflow from interfering
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const isOpen = answerDiv.classList.contains('open');
                    
                    // Close all other answers
                    document.querySelectorAll('.mobile-faq-answer').forEach(el => {
                        el.style.display = 'none';
                        el.classList.remove('open');
                    });
                    document.querySelectorAll('.faq-link').forEach(el => {
                        el.classList.remove('mobile-active');
                        const circle = el.querySelector('.circle');
                        if(circle) circle.style.transform = 'rotate(0deg)';
                    });
                    
                    if (!isOpen) {
                        answerDiv.style.display = 'block';
                        answerDiv.classList.add('open');
                        link.classList.add('mobile-active');
                        
                        const circle = link.querySelector('.circle');
                        if(circle) circle.style.transform = 'rotate(45deg)';
                    }
                }, true); // Capture phase is key here
            }
        });
    }

    // Run on load
    initMobileFAQ();
    
    // Also run on resize - BUT only init if we cross into mobile width
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 479) {
            initMobileFAQ();
        } else {
            // Optional: If we go back to desktop, we might want to cleanup? 
            // For now, CSS hiding .mobile-faq-answer should be enough if the layout holds.
            // But strict prevention on load is the main fix for desktop layout.
        }
    });

    function initReviewsCarousel() {
        const section = document.querySelector('.section.real-voices');
        if (!section) return;

        const mask = section.querySelector('.real-voices-slider-wrapper-mask');
        if (!mask) return;

        // Allow native scrolling by stopping Webflow's touch interference
        // We capture the event and stop it from bubbling up to Webflow's global listeners
        const stopWebflowInterference = (e) => {
            e.stopPropagation();
        };

        mask.addEventListener('touchstart', stopWebflowInterference, { capture: true, passive: true });
        mask.addEventListener('touchmove', stopWebflowInterference, { capture: true, passive: true });
        mask.addEventListener('touchend', stopWebflowInterference, { capture: true, passive: true });

        const prevBtn = section.querySelector('.w-slider-arrow-left');
        const nextBtn = section.querySelector('.w-slider-arrow-right');

        const getStep = () => {
            const firstSlide = mask.querySelector('.w-slide');
            if (!firstSlide) return 0;
            const rect = firstSlide.getBoundingClientRect();
            const styles = window.getComputedStyle(mask);
            const gapValue = styles.columnGap || styles.gap || '0';
            const gap = Number.parseFloat(gapValue) || 0;
            return rect.width + gap;
        };

        const scrollByStep = (direction) => {
            const step = getStep();
            if (!step) return;
            const max = Math.max(0, mask.scrollWidth - mask.clientWidth);
            const current = mask.scrollLeft;
            const edgeThreshold = 2;

            if (direction > 0 && current >= max - edgeThreshold) {
                mask.scrollTo({ left: 0, behavior: 'smooth' });
                return;
            }

            if (direction < 0 && current <= edgeThreshold) {
                mask.scrollTo({ left: max, behavior: 'smooth' });
                return;
            }

            mask.scrollTo({ left: current + direction * step, behavior: 'smooth' });
        };

        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                scrollByStep(-1);
            }, true);
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                scrollByStep(1);
            }, true);
        }
    }

    initReviewsCarousel();
});
