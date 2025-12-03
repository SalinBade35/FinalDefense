document.addEventListener('DOMContentLoaded', () => {
  // Dark mode toggle
  const darkToggle = document.getElementById("darkToggle");
  if (darkToggle) {
    darkToggle.addEventListener("click", () => {
      document.documentElement.classList.toggle("dark");
    });
  }

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



  // Product Details Redirect Function - Enhanced
  window.redirectToProductDetails = function(productId) {
  const button = event.target.closest('.details-menu-btn');
  if (button) {
    event.preventDefault();
    event.stopPropagation();
    button.style.pointerEvents = 'none';
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    setTimeout(() => {
      try {
        // Redirect to the dynamic product detail page
        window.location.href = `/souvenirs/product/${productId}/`;
      } catch (error) {
        button.style.pointerEvents = 'auto';
        button.innerHTML = originalContent;
        alert('Unable to load product details. Please try again.');
      }
    }, 300);
  }
};
  

  // Enhanced keyboard navigation for details menu
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      const target = e.target;
      if (target.classList.contains('details-menu-btn')) {
        e.preventDefault();
        const productId = target.getAttribute('onclick').match(/\d+/)[0];
        redirectToProductDetails(productId);
      }
    }
  });

  // Add click event listener for details buttons (backup method)
  document.addEventListener('click', function(e) {
    if (e.target.closest('.details-menu-btn')) {
      e.preventDefault();
      e.stopPropagation();
      
      const button = e.target.closest('.details-menu-btn');
      const onclickAttr = button.getAttribute('onclick');
      
      if (onclickAttr) {
        const productIdMatch = onclickAttr.match(/redirectToProductDetails\((\d+)\)/);
        if (productIdMatch) {
          const productId = productIdMatch[1];
          redirectToProductDetails(productId);
        }
      }
    }
  });


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
        }
      })
      .catch(err => {
        console.error('Add to cart error:', err);
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
        }
      })
      .catch(err => {
        console.error('Add to wishlist error:', err);
      });
    });
  });

  // Function to update cart item quantity
  function updateCartQuantity(itemId, newQuantity) {
    fetch('/souvenirs/update-cart-quantity/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: `item_id=${itemId}&quantity=${newQuantity}`
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        updateCounts();
        // Refresh cart sidebar to show updated totals
        document.getElementById("cartBtn").click();
      }
    })
    .catch(err => {
      console.error('Quantity update error:', err);
    });
  }



  // Enhanced Cart Sidebar logic with quantity controls
  const cartBtn = document.getElementById("cartBtn");
  if (cartBtn) {
    cartBtn.addEventListener("click", () => {
      if (!requireLogin()) return;
      
      fetch('/souvenirs/get-cart-items/')
        .then(res => res.json())
        .then(data => {
          let html = '';
          if (data.items.length === 0) {
            html = '<div class="sidebar-empty-state cart-empty">Your cart is empty<br><small>Add some amazing souvenirs!</small></div>';
          } else {
            data.items.forEach(item => {
              const totalPrice = (item.price * item.quantity).toFixed(2);
              const unitPrice = parseFloat(item.price).toFixed(2);
              html += `
                <div class="sidebar-product-row">
                  <div class="flex items-start gap-3">
                    <img src="${item.image || '/static/images/placeholder.jpg'}" alt="${item.name}" class="sidebar-product-img">
                    <div class="sidebar-product-info flex-1">
                      <div class="product-name">${item.name}</div>
                      <div class="product-unit-price">$${unitPrice} each</div>
                      <div class="product-price">Total: $${totalPrice}</div>
                      
                      <!-- Quantity Controls -->
                      <div class="quantity-controls">
                        <button class="quantity-btn decrease-btn" data-item-id="${item.id}" data-current-qty="${item.quantity}" ${item.quantity <= 1 ? 'disabled' : ''}>
                          <i class="fas fa-minus"></i>
                        </button>
                        <div class="quantity-display">${item.quantity}</div>
                        <button class="quantity-btn increase-btn" data-item-id="${item.id}" data-current-qty="${item.quantity}">
                          <i class="fas fa-plus"></i>
                        </button>
                      </div>
                      
                      <div class="sidebar-actions">
                        <button class="sidebar-remove-btn remove-cart-item-btn" data-item-id="${item.id}">Remove</button>
                      </div>
                    </div>
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

          const sidebar = document.getElementById('cartSidebar');
          sidebar.classList.remove('hidden');
          sidebar.classList.add('sidebar-enter');

          // Quantity increase button logic
          document.querySelectorAll('.increase-btn').forEach(btn => {
            btn.addEventListener('click', function() {
              const itemId = btn.dataset.itemId;
              const currentQty = parseInt(btn.dataset.currentQty);
              updateCartQuantity(itemId, currentQty + 1);
            });
          });

          // Quantity decrease button logic
          document.querySelectorAll('.decrease-btn').forEach(btn => {
            btn.addEventListener('click', function() {
              const itemId = btn.dataset.itemId;
              const currentQty = parseInt(btn.dataset.currentQty);
              if (currentQty > 1) {
                updateCartQuantity(itemId, currentQty - 1);
              }
            });
          });

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
                }
              });
            });
          });
        })
        .catch(err => {
          console.error('Cart loading error:', err);
        });
    });
  }

  window.closeCartSidebar = function() {
    const sidebar = document.getElementById('cartSidebar');
    sidebar.classList.add('hidden');
    sidebar.classList.remove('sidebar-enter');
  };

  // Enhanced Wishlist Sidebar logic
  const wishlistBtn = document.getElementById("wishlistBtn");
  if (wishlistBtn) {
    wishlistBtn.addEventListener("click", () => {
      if (!requireLogin()) return;
      
      fetch('/souvenirs/get-wishlist-items/')
        .then(res => res.json())
        .then(data => {
          let html = '';
          if (data.items.length === 0) {
            html = '<div class="sidebar-empty-state wishlist-empty">Your wishlist is empty<br><small>Save your favorite items here!</small></div>';
          } else {
            data.items.forEach(item => {
              html += `
                <div class="sidebar-product-row">
                  <div class="flex items-center gap-3">
                    <img src="${item.image || '/static/images/placeholder.jpg'}" alt="${item.name}" class="sidebar-product-img">
                    <div class="sidebar-product-info flex-1">
                      <div class="product-name">${item.name}</div>
                      <div class="product-price">$${item.price}</div>
                      <div class="sidebar-actions">
                        <button class="sidebar-add-to-cart-btn wishlist-add-to-cart-btn" data-product-id="${item.id}">
                          <i class="fas fa-shopping-cart"></i>Add to Cart
                        </button>
                        <button class="sidebar-remove-btn remove-wishlist-item-btn" data-product-id="${item.id}">Remove</button>
                      </div>
                    </div>
                  </div>
                </div>`;
            });
          }
          document.getElementById('wishlistSidebarContent').innerHTML = html;
          
          const sidebar = document.getElementById('wishlistSidebar');
          sidebar.classList.remove('hidden');
          sidebar.classList.add('sidebar-enter');

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
                }
              });
            });
          });
        })
        .catch(err => {
          console.error('Wishlist loading error:', err);
        });
    });
  }

  window.closeWishlistSidebar = function() {
    const sidebar = document.getElementById('wishlistSidebar');
    sidebar.classList.add('hidden');
    sidebar.classList.remove('sidebar-enter');
  };

  // Enhanced Place Order Button - Redirect to delivery page
  const checkoutSidebarBtn = document.getElementById('checkoutSidebarBtn');
  if (checkoutSidebarBtn) {
    checkoutSidebarBtn.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Check if cart has items before redirecting
      fetch('/souvenirs/get-cart-items/')
        .then(res => res.json())
        .then(data => {
          if (data.items.length === 0) {
            alert('Your cart is empty');
            return;
          }
          
          // Redirect to delivery page
          window.location.href = '/souvenirs/delivery/';
        })
        .catch(err => {
          console.error('Error checking cart:', err);
          alert('Error accessing cart');
        });
    });
  }


  // Enhanced click outside and escape key to close sidebars
  function handleSidebarClose(e) {
    const cartSidebar = document.getElementById('cartSidebar');
    const wishlistSidebar = document.getElementById('wishlistSidebar');
    const cartBtn = document.getElementById('cartBtn');
    const wishlistBtn = document.getElementById('wishlistBtn');
    
    // Handle Escape key
    if (e.type === 'keydown' && e.key === 'Escape') {
      if (cartSidebar && !cartSidebar.classList.contains('hidden')) {
        closeCartSidebar();
      }
      if (wishlistSidebar && !wishlistSidebar.classList.contains('hidden')) {
        closeWishlistSidebar();
      }
      return;
    }
    
    // Handle click outside
    if (e.type === 'click') {
      // Check if cart sidebar is open
      if (cartSidebar && !cartSidebar.classList.contains('hidden')) {
        // Check if click is outside the cart sidebar and not on cart button
        if (!cartSidebar.contains(e.target) && 
            !cartBtn.contains(e.target) &&
            !e.target.closest('.add-to-cart-btn') && // Don't close when adding to cart
            !e.target.closest('.quantity-btn')) {    // Don't close when changing quantity
          closeCartSidebar();
        }
      }
      
      // Check if wishlist sidebar is open
      if (wishlistSidebar && !wishlistSidebar.classList.contains('hidden')) {
        // Check if click is outside the wishlist sidebar and not on wishlist button
        if (!wishlistSidebar.contains(e.target) && 
            !wishlistBtn.contains(e.target) &&
            !e.target.closest('.add-to-wishlist-btn')) { // Don't close when adding to wishlist
          closeWishlistSidebar();
        }
      }
    }
  }

  // Add event listeners
  document.addEventListener('click', handleSidebarClose);
  document.addEventListener('keydown', handleSidebarClose);

  // Alternative close button handler using data attributes
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('sidebar-close-btn')) {
      const closeType = e.target.getAttribute('data-close');
      if (closeType === 'cart') {
        closeCartSidebar();
      } else if (closeType === 'wishlist') {
        closeWishlistSidebar();
      }
    }
  });


});