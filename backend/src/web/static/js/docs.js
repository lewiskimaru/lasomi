/**
 * Documentation pages JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDocumentation();
});

// Reinitialize when loaded via SPA navigation
window.addEventListener('page:loaded', function(e) {
    try {
        const page = (e && e.detail && e.detail.page) ? e.detail.page : null;
        if (page === 'docs' || page === 'developer') {
            initializeDocumentation();
            setupResponsiveTables();
            setupSearch();
            setupPrintOptimization();
            handleInitialHash();
        }
    } catch (err) {
        console.error('Error re-initializing documentation scripts:', err);
    }
});

function initializeDocumentation() {
    setupSidebarNavigation();
    setupSmoothScrolling();
    setupCodeBlockCopyButtons();
    setupSidebarToggle();
    setupActiveNavigation();
}

/**
 * Setup sidebar navigation functionality
 */
function setupSidebarNavigation() {
    const navLinks = document.querySelectorAll('.nav-link:not(.external)');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Only handle internal anchor links
            if (href && href.startsWith('#')) {
                e.preventDefault();
                
                // Remove active class from all links
                navLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                this.classList.add('active');
                
                // Smooth scroll to target
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update URL without triggering page reload
                    history.pushState(null, null, href);
                }
            }
        });
    });
}

/**
 * Setup smooth scrolling for all anchor links
 */
function setupSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL
                history.pushState(null, null, href);
            }
        });
    });
}

/**
 * Add copy buttons to code blocks
 */
function setupCodeBlockCopyButtons() {
    const codeBlocks = document.querySelectorAll('.code-block');
    
    codeBlocks.forEach(block => {
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy to clipboard';
        
        // Position button
        block.style.position = 'relative';
        copyButton.style.position = 'absolute';
        copyButton.style.top = '10px';
        copyButton.style.right = '10px';
        copyButton.style.background = 'rgba(255, 255, 255, 0.1)';
        copyButton.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        copyButton.style.color = '#fff';
        copyButton.style.padding = '6px 8px';
        copyButton.style.borderRadius = '4px';
        copyButton.style.cursor = 'pointer';
        copyButton.style.fontSize = '12px';
        copyButton.style.transition = 'all 0.2s ease';
        
        // Add hover effect
        copyButton.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255, 255, 255, 0.2)';
        });
        
        copyButton.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(255, 255, 255, 0.1)';
        });
        
        // Add copy functionality
        copyButton.addEventListener('click', function() {
            const codeElement = block.querySelector('code');
            const text = codeElement.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                // Show success feedback
                const originalHTML = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i>';
                this.style.background = '#28a745';
                
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.style.background = 'rgba(255, 255, 255, 0.1)';
                }, 1500);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                // Show success feedback
                const originalHTML = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i>';
                this.style.background = '#28a745';
                
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                    this.style.background = 'rgba(255, 255, 255, 0.1)';
                }, 1500);
            });
        });
        
        block.appendChild(copyButton);
    });
}

/**
 * Setup sidebar toggle for mobile
 */
function setupSidebarToggle() {
    const toggleButton = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.docs-sidebar');
    
    if (toggleButton && sidebar) {
        toggleButton.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-open');
            
            // Update button icon
            const icon = this.querySelector('i');
            if (sidebar.classList.contains('sidebar-open')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !toggleButton.contains(e.target)) {
                    sidebar.classList.remove('sidebar-open');
                    const icon = toggleButton.querySelector('i');
                    icon.className = 'fas fa-bars';
                }
            }
        });
    }
}

/**
 * Setup active navigation based on scroll position
 */
function setupActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link:not(.external)');
    
    if (sections.length === 0 || navLinks.length === 0) return;
    
    // Throttle scroll events
    let ticking = false;
    
    function updateActiveNavigation() {
        const scrollPosition = window.scrollY + 100; // Offset for better UX
        
        let activeSection = null;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                activeSection = section.id;
            }
        });
        
        // Update active nav link
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                const targetId = href.substring(1);
                if (targetId === activeSection) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            }
        });
        
        ticking = false;
    }
    
    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(updateActiveNavigation);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', onScroll);
    
    // Initial call
    updateActiveNavigation();
}

/**
 * Handle URL hash on page load
 */
function handleInitialHash() {
    const hash = window.location.hash;
    if (hash) {
        const targetElement = document.querySelector(hash);
        if (targetElement) {
            // Small delay to ensure page is fully loaded
            setTimeout(() => {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update active navigation
                const navLinks = document.querySelectorAll('.nav-link:not(.external)');
                navLinks.forEach(link => {
                    if (link.getAttribute('href') === hash) {
                        link.classList.add('active');
                    } else {
                        link.classList.remove('active');
                    }
                });
            }, 100);
        }
    }
}

// Handle initial hash when page loads
window.addEventListener('load', handleInitialHash);

/**
 * Add responsive table wrapper for better mobile experience
 */
function setupResponsiveTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-wrapper';
            wrapper.style.overflowX = 'auto';
            wrapper.style.marginBottom = 'var(--spacing-md)';
            
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Initialize responsive tables
document.addEventListener('DOMContentLoaded', setupResponsiveTables);

/**
 * Add search functionality (basic implementation)
 */
function setupSearch() {
    const searchInput = document.getElementById('docs-search');
    if (!searchInput) return;
    
    const searchableElements = document.querySelectorAll('h1, h2, h3, p, li');
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length < 2) {
            // Reset all elements
            searchableElements.forEach(el => {
                el.style.display = '';
                el.classList.remove('search-highlight');
            });
            return;
        }
        
        searchableElements.forEach(el => {
            const text = el.textContent.toLowerCase();
            if (text.includes(query)) {
                el.style.display = '';
                el.classList.add('search-highlight');
            } else {
                el.style.display = 'none';
                el.classList.remove('search-highlight');
            }
        });
    });
}

// Initialize search if search input exists
document.addEventListener('DOMContentLoaded', setupSearch);

/**
 * Add print styles optimization
 */
function setupPrintOptimization() {
    const printButton = document.getElementById('print-docs');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }
}

// Initialize print optimization
document.addEventListener('DOMContentLoaded', setupPrintOptimization);
