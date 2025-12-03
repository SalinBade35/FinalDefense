document.addEventListener('DOMContentLoaded', () => {
  // Dark mode toggle
  const darkToggle = document.getElementById("darkToggle");
  if (darkToggle) {
    darkToggle.addEventListener("click", () => {
      document.documentElement.classList.toggle("dark");
    });
  }

  // Notification logic
  window.showNotification = function(message, type = "info") {
    const notification = document.getElementById("notification");
    if (!notification) return;
    notification.innerText = message;
    notification.className = `fixed bottom-20 right-6 p-4 rounded-lg shadow-lg text-white z-50 ${type === "success" ? "bg-green-500" : type === "error" ? "bg-red-500" : "bg-blue-500"}`;
    notification.classList.remove("hidden");
    setTimeout(() => notification.classList.add("hidden"), 3000);
  };

  // Helper: Get CSRF token
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


  // AJAX instant search
  const searchInput = document.querySelector('input[name="search"]');
  const productGrid = document.getElementById('productGrid');
  let timer;

  if (searchInput && productGrid) {
    searchInput.addEventListener('input', function() {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const query = searchInput.value;
        const category = document.querySelector('input[name="category"]').value;
        const price = document.querySelector('input[name="price"]').value;

        fetch(`/souvenirs/ajax-search/?search=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&price=${encodeURIComponent(price)}`)
          .then(res => res.json())
          .then(data => {
            productGrid.innerHTML = data.html;
          });
      }, 400); // debounce
    });
  }


  // Helper: Check login status
  function requireLogin() {
    if (typeof window.isAuthenticated !== "undefined" && !window.isAuthenticated) {
      window.location.href = window.loginUrl + '?next=' + window.location.pathname;
      return false;
    }
    return true;
  }

  // Update badge counts from backend
  function updateCounts() {
    if (typeof window.isAuthenticated !== "undefined" && window.isAuthenticated) {
      fetch('/souvenirs/get-cart-items/')
        .then(res => res.json())
        .then(data => {
          document.getElementById('cart-count').innerText = data.items.length;
        })
        .catch(err => console.log('Cart count error:', err));
      
      fetch('/souvenirs/get-wishlist-items/')
        .then(res => res.json())
        .then(data => {
          document.getElementById('wishlist-count').innerText = data.items.length;
        })
        .catch(err => console.log('Wishlist count error:', err));
    }
  }

  updateCounts();

  // Add to Cart AJAX
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      if (!requireLogin()) return;
      
      const productId = btn.dataset.productId;
      fetch(`/souvenirs/add-to-cart/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          document.getElementById('cart-count').innerText = data.cart_count;
          showNotification('Added to cart!', 'success');
        } else {
          showNotification(data.error || 'Error adding to cart', 'error');
        }
      })
      .catch(err => {
        console.error('Add to cart error:', err);
        showNotification('Error adding to cart', 'error');
      });
    });
  });

  // Add to Wishlist AJAX
  document.querySelectorAll('.add-to-wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      if (!requireLogin()) return;
      
      const productId = btn.dataset.productId;
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
          document.getElementById('wishlist-count').innerText = data.wishlist_count;
          showNotification('Added to wishlist!', 'success');
        } else {
          showNotification(data.error || 'Error adding to wishlist', 'error');
        }
      })
      .catch(err => {
        console.error('Add to wishlist error:', err);
        showNotification('Error adding to wishlist', 'error');
      });
    });
  });

  // Cart Sidebar logic
  const cartBtn = document.getElementById("cartBtn");
  if (cartBtn) {
    cartBtn.addEventListener("click", () => {
      if (!requireLogin()) return;
      
      fetch('/souvenirs/get-cart-items/')
        .then(res => res.json())
        .then(data => {
          let html = '';
          if (data.items.length === 0) {
            html = '<div class="text-gray-500 text-center py-8">Your cart is empty</div>';
          } else {
            data.items.forEach(item => {
              const totalPrice = (item.price * item.quantity).toFixed(2);
              html += `
                <div class="sidebar-product-row flex items-center gap-3 p-3 border-b">
                  <img src="${item.image || '/static/images/placeholder.jpg'}" alt="${item.name}" class="sidebar-product-img w-16 h-16 object-cover rounded">
                  <div class="flex-1">
                    <div class="font-semibold text-sm">${item.name}</div>
                    <div class="text-xs text-gray-500">Qty: ${item.quantity}</div>
                    <div class="text-sm font-medium">$${totalPrice}</div>
                    <button class="sidebar-remove-btn remove-cart-item-btn text-red-500 text-xs mt-1" data-item-id="${item.id}">Remove</button>
                  </div>
                </div>`;
            });
          }
          document.getElementById('cartSidebarContent').innerHTML = html;

          // Show/hide Place Order button based on cart content
          const checkoutBtn = document.getElementById('checkoutSidebarBtn');
          if (checkoutBtn) {
            checkoutBtn.style.display = data.items.length > 0 ? 'block' : 'none';
          }

          document.getElementById('cartSidebar').classList.remove('hidden');

          // Remove cart item logic
          document.querySelectorAll('.remove-cart-item-btn').forEach(btn => {
            btn.addEventListener('click', function() {
              const itemId = btn.dataset.itemId;
              fetch('/souvenirs/remove-cart-item/', {
                method: 'POST',
                headers: {
                  'X-CSRFToken': getCookie('csrftoken'),
                  'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `item_id=${itemId}`
              })
              .then(res => res.json())
              .then(data => {
                if (data.success) {
                  updateCounts();
                  cartBtn.click(); // Refresh cart sidebar
                  showNotification('Item removed from cart', 'success');
                }
              });
            });
          });
        })
        .catch(err => {
          console.error('Cart loading error:', err);
          showNotification('Error loading cart', 'error');
        });
    });
  }

  window.closeCartSidebar = function() {
    document.getElementById('cartSidebar').classList.add('hidden');
  };

  // Wishlist Sidebar logic
  const wishlistBtn = document.getElementById("wishlistBtn");
  if (wishlistBtn) {
    wishlistBtn.addEventListener("click", () => {
      if (!requireLogin()) return;
      
      fetch('/souvenirs/get-wishlist-items/')
        .then(res => res.json())
        .then(data => {
          let html = '';
          if (data.items.length === 0) {
            html = '<div class="text-gray-500 text-center py-8">Your wishlist is empty</div>';
          } else {
            data.items.forEach(item => {
              html += `
                <div class="sidebar-product-row flex items-center gap-3 p-3 border-b">
                  <img src="${item.image || '/static/images/placeholder.jpg'}" alt="${item.name}" class="sidebar-product-img w-16 h-16 object-cover rounded">
                  <div class="flex-1">
                    <div class="font-semibold text-sm">${item.name}</div>
                    <div class="text-sm text-gray-500">$${item.price}</div>
                    <div class="flex gap-2 mt-2">
                      <button class="bg-primary text-white px-2 py-1 rounded text-xs wishlist-add-to-cart-btn" data-product-id="${item.id}">Add to Cart</button>
                      <button class="sidebar-remove-btn remove-wishlist-item-btn text-red-500 text-xs" data-product-id="${item.id}">Remove</button>
                    </div>
                  </div>
                </div>`;
            });
          }
          document.getElementById('wishlistSidebarContent').innerHTML = html;
          document.getElementById('wishlistSidebar').classList.remove('hidden');

          // Add to cart from wishlist
          document.querySelectorAll('.wishlist-add-to-cart-btn').forEach(btn => {
            btn.addEventListener('click', function() {
              const productId = btn.dataset.productId;
              fetch('/souvenirs/wishlist-add-to-cart/', {
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
                  updateCounts();
                  wishlistBtn.click(); // Refresh wishlist
                  showNotification('Added to cart!', 'success');
                }
              });
            });
          });

          // Remove from wishlist
          document.querySelectorAll('.remove-wishlist-item-btn').forEach(btn => {
            btn.addEventListener('click', function() {
              const productId = btn.dataset.productId;
              fetch('/souvenirs/remove-wishlist-item/', {
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
                  updateCounts();
                  wishlistBtn.click(); // Refresh wishlist
                  showNotification('Item removed from wishlist', 'success');
                }
              });
            });
          });
        })
        .catch(err => {
          console.error('Wishlist loading error:', err);
          showNotification('Error loading wishlist', 'error');
        });
    });
  }

  window.closeWishlistSidebar = function() {
    document.getElementById('wishlistSidebar').classList.add('hidden');
  };

  // Modal and Checkout Logic
  const checkoutSidebarBtn = document.getElementById('checkoutSidebarBtn');
  const addressModal = document.getElementById('addressModal');
  const addressForm = document.getElementById('addressForm');
  const orderAddress = document.getElementById('orderAddress');
  const cancelAddressBtn = document.getElementById('cancelAddressBtn');

  // Place Order Button Click - Show Modal
  if (checkoutSidebarBtn) {
    checkoutSidebarBtn.addEventListener('click', function(e) {
      e.preventDefault();
      console.log('Checkout button clicked'); // Debug log
      
      if (addressModal) {
        addressModal.classList.remove('hidden');
        if (orderAddress) {
          orderAddress.value = '';
          orderAddress.focus();
        }
        // Default to COD
        const codRadio = document.querySelector('input[name="payment_method"][value="COD"]');
        if (codRadio) {
          codRadio.checked = true;
        }
      } else {
        console.error('Address modal not found!');
      }
    });
  }

  // Cancel Button
  if (cancelAddressBtn) {
    cancelAddressBtn.addEventListener('click', function(e) {
      e.preventDefault();
      if (addressModal) {
        addressModal.classList.add('hidden');
      }
    });
  }

  // Close modal when clicking outside
  if (addressModal) {
    addressModal.addEventListener('click', function(e) {
      if (e.target === addressModal) {
        addressModal.classList.add('hidden');
      }
    });
  }

  // Form Submission - Create Order
  if (addressForm) {
    addressForm.addEventListener('submit', function(e) {
      e.preventDefault();
      console.log('Address form submitted'); // Debug log
      
      const address = orderAddress ? orderAddress.value.trim() : '';
      const paymentMethodEl = document.querySelector('input[name="payment_method"]:checked');
      const payment_method = paymentMethodEl ? paymentMethodEl.value : 'COD';
      
      if (!address) {
        showNotification('Please enter a delivery address', 'error');
        return;
      }
      
      // Disable submit button to prevent double submission
      const submitBtn = addressForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
      }
      
      console.log('Sending order data:', { address, payment_method }); // Debug log
      
      fetch('/souvenirs/create_order/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `address=${encodeURIComponent(address)}&payment_method=${encodeURIComponent(payment_method)}`
      })
      .then(res => {
        console.log('Response status:', res.status); // Debug log
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        console.log('Order response:', data); // Debug log
        if (data.success) {
          updateCounts();
          showNotification(data.message || 'Order placed successfully!', 'success');
          
          // Clear cart sidebar and hide modal
          document.getElementById('cartSidebarContent').innerHTML = '<div class="text-green-500 text-center py-8"><i class="fas fa-check-circle text-4xl mb-2"></i><br>Order placed successfully!</div>';
          if (checkoutSidebarBtn) {
            checkoutSidebarBtn.style.display = 'none';
          }
          if (addressModal) {
            addressModal.classList.add('hidden');
          }
          
          // Auto-close cart sidebar after 3 seconds
          setTimeout(() => {
            closeCartSidebar();
          }, 3000);
          
        } else {
          showNotification(data.error || 'Order failed', 'error');
        }
      })
      .catch(error => {
        console.error('Order error:', error);
        showNotification('An error occurred while placing the order', 'error');
      })
      .finally(() => {
        // Re-enable submit button
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Place Order';
        }
      });
    });
  }



});