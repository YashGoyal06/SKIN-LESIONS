// Custom cursor effect
document.addEventListener('DOMContentLoaded', function() {
    // Use default browser cursor as fallback
    document.body.classList.remove('custom-cursor');
    
    // Create cursor elements
    const cursorGlow = document.createElement('div');
    cursorGlow.classList.add('cursor-glow');
    document.body.appendChild(cursorGlow);
    
    // Create delayed follow circle
    const cursorFollow = document.createElement('div');
    cursorFollow.classList.add('cursor-follow');
    document.body.appendChild(cursorFollow);
    
    // Variables for storing mouse position
    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    
    // Update mouse position on mouse move
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Show the cursor glow and position it at the mouse coordinates
        cursorGlow.style.opacity = '1';
        cursorGlow.style.left = mouseX + 'px';
        cursorGlow.style.top = mouseY + 'px';
    });
    
    // Animate the follow cursor with delay
    function animateFollowCursor() {
        // Calculate the distance between current position and target position
        const dx = mouseX - cursorX;
        const dy = mouseY - cursorY;
        
        // Move the cursor a fraction of the distance (creates delay/easing effect)
        cursorX += dx * 0.15;
        cursorY += dy * 0.15;
        
        // Apply the position
        cursorFollow.style.left = cursorX + 'px';
        cursorFollow.style.top = cursorY + 'px';
        
        // Continue animation
        requestAnimationFrame(animateFollowCursor);
    }
    
    // Start the animation
    animateFollowCursor();
    
    // Make cursor visible when mouse moves
    document.addEventListener('mousemove', function() {
        cursorFollow.style.opacity = '1';
        cursorGlow.style.opacity = '0.9';
    });
    
    // Increase cursor glow size when hovering clickable elements
    const clickableElements = document.querySelectorAll('a, button, input[type="submit"], .cta-button, .submit-button, .feature-card, .testimonial-card, .step-number, nav ul li a, .footer-links ul li a, input[type="checkbox"], input[type="radio"], select, .color-label, .checkbox-option');
    
    clickableElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            cursorGlow.style.width = '70px';
            cursorGlow.style.height = '70px';
            cursorGlow.style.background = 'radial-gradient(circle, rgba(255, 143, 48, 0.6) 0%, rgba(255, 143, 48, 0) 70%)';
            cursorFollow.style.borderColor = 'rgba(255, 143, 48, 1)';
            cursorFollow.style.backgroundColor = 'rgba(255, 143, 48, 0.3)';
            cursorFollow.style.width = '35px';
            cursorFollow.style.height = '35px';
        });
        
        element.addEventListener('mouseleave', function() {
            cursorGlow.style.width = '50px';
            cursorGlow.style.height = '50px';
            cursorGlow.style.background = 'radial-gradient(circle, rgba(55, 199, 255, 0.5) 0%, rgba(55, 199, 255, 0) 70%)';
            cursorFollow.style.borderColor = 'rgba(55, 199, 255, 0.9)';
            cursorFollow.style.backgroundColor = 'rgba(55, 199, 255, 0.2)';
            cursorFollow.style.width = '25px';
            cursorFollow.style.height = '25px';
        });
    });
    
    // Hide cursor elements when mouse leaves the window
    document.addEventListener('mouseout', function(e) {
        if (e.relatedTarget === null) {
            cursorGlow.style.opacity = '0';
            cursorFollow.style.opacity = '0';
        }
    });
    
    // Show cursor elements when mouse enters the window
    document.addEventListener('mouseover', function() {
        cursorGlow.style.opacity = '1';
        cursorFollow.style.opacity = '1';
    });
    
    // Add cursor click effect
    document.addEventListener('mousedown', function() {
        cursorGlow.style.transform = 'translate(-50%, -50%) scale(0.9)';
        cursorFollow.style.transform = 'translate(-50%, -50%) scale(0.5)';
    });
    
    document.addEventListener('mouseup', function() {
        cursorGlow.style.transform = 'translate(-50%, -50%) scale(1)';
        cursorFollow.style.transform = 'translate(-50%, -50%) scale(1)';
    });
});