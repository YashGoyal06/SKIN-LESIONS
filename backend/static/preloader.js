// Preloader Script
document.addEventListener('DOMContentLoaded', function() {
    // Get preloader element
    const preloader = document.querySelector('.preloader');
    
    // Function to hide preloader
    function hidePreloader() {
        preloader.classList.add('hidden');
        
        // Remove preloader from DOM after transition completes
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }
    
    // Hide preloader after all content is loaded
    window.addEventListener('load', function() {
        // Add a small delay for visual effect
        setTimeout(hidePreloader, 1500);
    });
    
    // Fallback - hide preloader after 5 seconds even if content isn't fully loaded
    setTimeout(hidePreloader, 5000);
});