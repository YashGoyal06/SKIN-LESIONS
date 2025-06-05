document.addEventListener('DOMContentLoaded', function() {
    
    const preloader = document.querySelector('.preloader');
    
    
    function hidePreloader() {
        preloader.classList.add('hidden');
        
        
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }
    
    
    window.addEventListener('load', function() {
        
        setTimeout(hidePreloader, 1500);
    });
    
    
    setTimeout(hidePreloader, 5000);
});