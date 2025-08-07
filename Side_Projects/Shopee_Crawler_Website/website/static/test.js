// Simple test to verify JavaScript is working
console.log("Test script loaded successfully!");

// Test if jQuery is available with retry mechanism
function checkJQuery() {
    if (typeof $ !== 'undefined' && typeof jQuery !== 'undefined') {
        console.log("jQuery is available, version:", $.fn.jquery);
        return true;
    } else {
        console.error("jQuery is not available!");
        return false;
    }
}

// Check jQuery immediately and retry if needed
if (!checkJQuery()) {
    // Retry after a short delay
    setTimeout(function() {
        if (checkJQuery()) {
            console.log("jQuery loaded successfully on retry!");
        } else {
            console.error("jQuery failed to load even after retry!");
        }
    }, 500);
}

// Test basic DOM manipulation
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM is ready");
    
    // Test if main elements exist
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const sortableTable = document.getElementById('sortableTable');
    
    console.log("Upload button:", uploadBtn ? "Found" : "Not found");
    console.log("File input:", fileInput ? "Found" : "Not found");
    console.log("Sortable table:", sortableTable ? "Found" : "Not found");
    
    if (uploadBtn) {
        uploadBtn.style.backgroundColor = '#28a745';
        console.log("Upload button style changed - JavaScript is working!");
    }
});
