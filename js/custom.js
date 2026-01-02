document.addEventListener('DOMContentLoaded', () => {
    // Interactive Session Cards Logic
    const sessionCards = document.querySelectorAll('.sessions-single');

    sessionCards.forEach(card => {
        card.addEventListener('click', function (e) {
            // Check if click is on a link (e.g. title link), if so, do we follow?
            // The title is an <a> tag with href="#" in the current HTML.
            // We'll prevent default to avoid jumping to top if href="#"
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                e.preventDefault();
            }

            // Close other cards (Accordion behavior)
            sessionCards.forEach(c => {
                if (c !== this) {
                    c.classList.remove('active');
                }
            });

            // Toggle current card
            this.classList.toggle('active');
        });
    });
});
