// TEPIS Web App - Optimized JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality in hero section
    const heroSearchBar = document.querySelector('.hero .search-bar');
    if (heroSearchBar) {
        const searchInput = heroSearchBar.querySelector('input');
        const searchButton = heroSearchBar.querySelector('button');
        
        function handleSearch() {
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                window.location.href = `/events?search=${encodeURIComponent(searchTerm)}`;
            }
        }
        
        searchButton.addEventListener('click', handleSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }

    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';
            }
        });
    });
});
