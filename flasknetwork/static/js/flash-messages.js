/**
 * RateKTH Focus Modal Alerts
 * Handles the lifecycle of the full-screen flash message overlay.
 * 
 * Logic:
 * 1. Checks for existence of #flash-overlay on load.
 * 2. If found, starts a 4-second timer.
 * 3. After 4s (or on user click), fades out and removes from DOM.
 */

document.addEventListener('DOMContentLoaded', () => {
    const flashOverlay = document.getElementById('flash-overlay');

    if (flashOverlay) {
        // Configuration
        const DISPLAY_DURATION = 4000; // 4 seconds (matches CSS animation)

        // Function to dismiss the modal gracefully
        const dismissModal = () => {
            if (flashOverlay.classList.contains('hiding')) return; // Already hiding

            // Add class to trigger CSS fade-out animation
            flashOverlay.classList.add('hiding');

            // Remove from DOM after animation completes (300ms matches CSS)
            setTimeout(() => {
                if (flashOverlay.parentNode) {
                    flashOverlay.parentNode.removeChild(flashOverlay);
                }
            }, 300);
        };

        // 1. Auto-dismiss timer
        let autoDismissTimer = setTimeout(dismissModal, DISPLAY_DURATION);

        // 2. Click to dismiss (User MUST click the blurred background to dismiss)
        // This prevents accidental dismissal when trying to interact with the text (e.g. select/copy)
        flashOverlay.addEventListener('click', (e) => {
            if (e.target === flashOverlay) {
                clearTimeout(autoDismissTimer); // Stop the auto-timer since user manually dismissed
                dismissModal();
            }
        });

        // Optional: Pause timer on hover? (Adds complexity, maybe skip for "Simple")
    }
});
