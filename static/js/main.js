document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const urlInput = document.getElementById('urlInput');
    const enterHint = document.getElementById('enterHint');
    const errorMessage = document.getElementById('errorMessage');

    // Show/hide enter hint based on input
    if (urlInput && enterHint) {
        urlInput.addEventListener('input', function() {
            if (this.value.trim().length > 0) {
                enterHint.classList.add('show');
            } else {
                enterHint.classList.remove('show');
            }
        });

        // Hide hint when form is submitted
        if (form) {
            form.addEventListener('submit', function(e) {
                const url = urlInput.value.trim();
                
                if (!url) {
                    e.preventDefault();
                    showError('Please enter a website URL');
                    return;
                }

                // Show loading state
                enterHint.innerHTML = '<span class="loading-spinner">⏳</span> analyzing...';
                if (errorMessage) errorMessage.style.display = 'none';
            });
        }
    }

    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = '❌ ' + message;
            errorMessage.style.display = 'block';
        }
    }
});

