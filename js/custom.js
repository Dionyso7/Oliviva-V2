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
});