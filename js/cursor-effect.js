
document.addEventListener('DOMContentLoaded', function() {
    
    document.body.classList.remove('custom-cursor');
    
    
    const cursorGlow = document.createElement('div');
    cursorGlow.classList.add('cursor-glow');
    document.body.appendChild(cursorGlow);
    
    
    const cursorFollow = document.createElement('div');
    cursorFollow.classList.add('cursor-follow');
    document.body.appendChild(cursorFollow);
    
    
    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    
    
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        
        cursorGlow.style.opacity = '1';
        cursorGlow.style.left = mouseX + 'px';
        cursorGlow.style.top = mouseY + 'px';
    });
    
    
    function animateFollowCursor() {
        
        const dx = mouseX - cursorX;
        const dy = mouseY - cursorY;
        
        
        cursorX += dx * 0.15;
        cursorY += dy * 0.15;
        
        
        cursorFollow.style.left = cursorX + 'px';
        cursorFollow.style.top = cursorY + 'px';
        
        
        requestAnimationFrame(animateFollowCursor);
    }
    
    
    animateFollowCursor();
    
    
    document.addEventListener('mousemove', function() {
        cursorFollow.style.opacity = '1';
        cursorGlow.style.opacity = '0.9';
    });
    
    
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
    
    
    document.addEventListener('mouseout', function(e) {
        if (e.relatedTarget === null) {
            cursorGlow.style.opacity = '0';
            cursorFollow.style.opacity = '0';
        }
    });
    
    
    document.addEventListener('mouseover', function() {
        cursorGlow.style.opacity = '1';
        cursorFollow.style.opacity = '1';
    });
    
    
    document.addEventListener('mousedown', function() {
        cursorGlow.style.transform = 'translate(-50%, -50%) scale(0.9)';
        cursorFollow.style.transform = 'translate(-50%, -50%) scale(0.5)';
    });
    
    document.addEventListener('mouseup', function() {
        cursorGlow.style.transform = 'translate(-50%, -50%) scale(1)';
        cursorFollow.style.transform = 'translate(-50%, -50%) scale(1)';
    });
});