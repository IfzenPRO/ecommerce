// Cart functionality
function updateQuantity(productId, change) {
    const quantityInput = document.querySelector(`#quantity-${productId}`);
    let newQuantity = parseInt(quantityInput.value) + change;
    
    if (newQuantity < 1) newQuantity = 1;
    
    quantityInput.value = newQuantity;
    updateCartItem(productId, newQuantity);
}

function updateCartItem(productId, quantity) {
    fetch(`/cart/update/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('#cart-total').textContent = `$${data.total.toFixed(2)}`;
        document.querySelector(`#item-subtotal-${productId}`).textContent = 
            `$${data.item_total.toFixed(2)}`;
    });
}

// Product search and filter
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('#search-form');
    const filterForm = document.querySelector('#filter-form');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchQuery = document.querySelector('#search-input').value;
            window.location.href = `/products?search=${encodeURIComponent(searchQuery)}`;
        });
    }
    
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const category = document.querySelector('#category-filter').value;
            const minPrice = document.querySelector('#min-price').value;
            const maxPrice = document.querySelector('#max-price').value;
            
            let url = '/products?';
            if (category) url += `category=${encodeURIComponent(category)}&`;
            if (minPrice) url += `min_price=${encodeURIComponent(minPrice)}&`;
            if (maxPrice) url += `max_price=${encodeURIComponent(maxPrice)}`;
            
            window.location.href = url;
        });
    }
});

// PayPal integration
function initPayPalButton() {
    paypal.Buttons({
        createOrder: function(data, actions) {
            return fetch('/create-paypal-order', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(order => order.id);
        },
        onApprove: function(data, actions) {
            return fetch('/complete-paypal-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    orderID: data.orderID
                })
            })
            .then(response => response.json())
            .then(orderData => {
                window.location.href = '/order-confirmation';
            });
        }
    }).render('#paypal-button-container');
}

// Admin panel functionality
function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        fetch(`/admin/product/${productId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error deleting product');
            }
        });
    }
}

function updateOrderStatus(orderId, status) {
    fetch(`/admin/order/${orderId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Error updating order status');
        }
    });
}

// Image preview for product upload
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('#image-preview').src = e.target.result;
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// Form validation
function validateForm(formId) {
    const form = document.querySelector(`#${formId}`);
    if (!form) return true;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Password strength checker
function checkPasswordStrength(password) {
    const strengthMeter = document.querySelector('#password-strength');
    if (!strengthMeter) return;

    const strength = {
        0: "Very Weak",
        1: "Weak",
        2: "Medium",
        3: "Strong",
        4: "Very Strong"
    };

    let score = 0;
    if (password.length >= 8) score++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) score++;
    if (password.match(/\d/)) score++;
    if (password.match(/[^a-zA-Z\d]/)) score++;

    strengthMeter.textContent = strength[score];
    strengthMeter.className = `text-${score >= 3 ? 'success' : score >= 2 ? 'warning' : 'danger'}`;
}
