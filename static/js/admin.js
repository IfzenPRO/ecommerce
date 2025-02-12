// Initialize Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize all modals
    var modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'))
    var modalList = modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl)
    });

    // Initialize all tabs
    var tabTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tab"]'))
    var tabList = tabTriggerList.map(function (tabTriggerEl) {
        return new bootstrap.Tab(tabTriggerEl)
    });
});

// Confirm delete product
function confirmDelete(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        document.getElementById('deleteProduct' + productId).submit();
    }
}

// Preview image before upload
function previewImage(input) {
    var previewId = input.id + 'Preview';
    var preview = document.getElementById(previewId);
    
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// Toggle user status
function toggleUserStatus(userId) {
    if (confirm('Are you sure you want to change this user\'s status?')) {
        document.getElementById('toggleUser' + userId).submit();
    }
}
