// Quantity control functions
function increaseQuantity() {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        const currentValue = parseInt(quantityInput.value);
        const maxStock = parseInt(quantityInput.getAttribute('max'));
        if (currentValue < maxStock) {
            quantityInput.value = currentValue + 1;
        }
        syncBuyNowQty();
    }
}

function decreaseQuantity() {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        const currentValue = parseInt(quantityInput.value);
        if (currentValue > 1) {
            quantityInput.value = currentValue - 1;
        }
        syncBuyNowQty();
    }
}

function syncBuyNowQty() {
    const quantityInput = document.getElementById('quantity');
    const buyNowQty = document.getElementById('buyNowQty');
    if (quantityInput && buyNowQty) {
        buyNowQty.value = quantityInput.value;
    }
}

// --- Review Section ---

// Helper to render stars
function renderStars(container, avg) {
    if (!container) return;
    let html = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= Math.round(avg)) {
            html += '<i class="fas fa-star"></i>';
        } else {
            html += '<i class="far fa-star"></i>';
        }
    }
    container.innerHTML = html;
}

function loadReviews(productId) {
    fetch(`/souvenirs/product/${productId}/get-reviews/`)
    .then(res => res.json())
    .then(data => {
        // Update average rating and count
        const avgRating = data.avg_rating || 0;
        const reviewCount = data.review_count || 0;
        const avgStars = document.getElementById('avg-stars');
        const avgRatingText = document.getElementById('avg-rating-text');
        renderStars(avgStars, avgRating);
        if (avgRatingText) {
            avgRatingText.textContent = `(${avgRating.toFixed(1)}/5) • ${reviewCount} review${reviewCount === 1 ? '' : 's'}`;
        }

        // Render reviews
        const reviewsList = document.getElementById('reviews-list');
        if (reviewsList) {
            if (data.reviews.length === 0) {
                reviewsList.innerHTML = "<p>No reviews yet.</p>";
            } else {
                reviewsList.innerHTML = data.reviews.map(r => `
                    <div class="review mb-2">
                        <strong>${r.user}</strong>
                        <span class="text-warning">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</span>
                        <span class="text-muted">${r.created_at}</span>
                        <div>${r.comment ? r.comment : ''}</div>
                    </div>
                `).join('');
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', syncBuyNowQty);
        quantityInput.addEventListener('change', syncBuyNowQty);
    }

    // Add to cart functionality
    const cartBtn = document.querySelector('.add-to-cart-btn');
    if (cartBtn) {
        cartBtn.addEventListener('click', function() {
            if (!window.isAuthenticated) {
                alert('Please login to add items to cart.');
                window.location.href = window.loginUrl;
                return;
            }
            
            const productId = this.dataset.productId;
            
            fetch(`/souvenirs/add-to-cart/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showAlert('Product added to cart successfully!');
                } else {
                    showAlert(data.error || 'Failed to add to cart');
                }
            })
            .catch(err => {
                console.error('Add to cart error:', err);
                showAlert('Error adding to cart');
            });
        });
    }

    // Add to wishlist functionality
    const wishlistBtn = document.querySelector('.add-to-wishlist-btn');
    if (wishlistBtn) {
        wishlistBtn.addEventListener('click', function() {
            if (!window.isAuthenticated) {
                alert('Please login to add items to wishlist.');
                window.location.href = window.loginUrl;
                return;
            }
            
            const productId = this.dataset.productId;
            
            fetch(`/souvenirs/add-to-wishlist/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `product_id=${productId}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showAlert('Added to wishlist successfully!');
                    this.innerHTML = '<i class="fas fa-heart"></i>';
                    this.style.backgroundColor = '#dc3545';
                    this.style.color = 'white';
                } else {
                    showAlert(data.error || 'Failed to add to wishlist');
                }
            })
            .catch(err => {
                console.error('Add to wishlist error:', err);
                showAlert('Error adding to wishlist');
            });
        });
    }

    // --- Review Section ---
    // Set PRODUCT_ID from template context or hidden input
    let productId = window.PRODUCT_ID;
    if (!productId) {
        const buyNowForm = document.getElementById('buyNowForm');
        if (buyNowForm) {
            productId = buyNowForm.elements['product']?.value;
        }
    }
    if (productId) {
        loadReviews(productId);
    }

    // Handle review form submission
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm && productId) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(reviewForm);
            fetch(`/souvenirs/product/${productId}/submit-review/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                const msg = document.getElementById('review-message');
                if (data.success) {
                    msg.textContent = "Review submitted!";
                    msg.className = "text-success";
                    reviewForm.reset();
                    loadReviews(productId);
                } else {
                    msg.textContent = data.error || "Error submitting review.";
                    msg.className = "text-danger";
                }
            });
        });
    }
});

// Show alert function
function showAlert(message, type = 'success') {
    const alert = document.getElementById('successAlert');
    const alertMessage = document.getElementById('alertMessage');
    
    if (alert && alertMessage) {
        alertMessage.textContent = message;
        alert.style.display = 'flex';
        
        setTimeout(() => {
            alert.style.display = 'none';
        }, 3000);
    }
}

// CSRF token helper function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}