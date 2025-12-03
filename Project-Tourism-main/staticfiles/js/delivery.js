// document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate on Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true
    });

    // Initialize Feather icons
    feather.replace();

    // Get DOM elements
    const codOption = document.getElementById('codOption');
    const esewaOption = document.getElementById('esewaOption');
    const esewaInfo = document.getElementById('esewaInfo');
    const codForm = document.getElementById('codForm');
    const codSubmitBtn = document.getElementById('codSubmitBtn');

    // Payment method change handlers
    function handlePaymentMethodChange() {
        if (esewaOption.checked) {
            esewaInfo.style.display = 'block';
            codSubmitBtn.textContent = 'Pay with eSewa';
            codSubmitBtn.innerHTML = 'Pay with eSewa <i data-feather="credit-card"></i>';
            feather.replace();
        } else {
            esewaInfo.style.display = 'none';
            codSubmitBtn.textContent = 'Complete Order';
            codSubmitBtn.innerHTML = 'Complete Order <i data-feather="check"></i>';
            feather.replace();
        }
    }

    // Add event listeners for payment method changes
    codOption.addEventListener('change', handlePaymentMethodChange);
    esewaOption.addEventListener('change', handlePaymentMethodChange);

    // Form validation functions
    function validateEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
    }

    function validatePhone(phone) {
        const mobilePattern = /^98[0-9]{8}$/;
        const landlinePattern = /^01-[0-9]{7}$/;
        return mobilePattern.test(phone) || landlinePattern.test(phone);
    }

    function validateWardNumber(zip) {
        const wardPattern = /^44800-0[1-9]|44800-10$/;
        return wardPattern.test(zip);
    }

    // Real-time validation
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');
    const cityInput = document.getElementById('city');
    const stateInput = document.getElementById('state');
    const zipInput = document.getElementById('zip');

    emailInput.addEventListener('blur', function() {
        const emailError = document.getElementById('emailError');
        if (this.value && !validateEmail(this.value)) {
            this.classList.add('is-invalid');
            emailError.style.display = 'block';
        } else {
            this.classList.remove('is-invalid');
            emailError.style.display = 'none';
        }
    });

    phoneInput.addEventListener('input', function() {
        // Remove any non-digit characters and format
        let value = this.value.replace(/\D/g, '');
        
        if (value.startsWith('01')) {
            // Landline format: 01-XXXXXXX
            if (value.length > 2) {
                value = value.substring(0, 2) + '-' + value.substring(2, 9);
            }
        } else if (value.startsWith('98')) {
            // Mobile format: 98XXXXXXXX (no formatting needed)
            value = value.substring(0, 10);
        }
        
        this.value = value;
    });

    phoneInput.addEventListener('blur', function() {
        if (this.value && !validatePhone(this.value)) {
            this.classList.add('is-invalid');
        } else {
            this.classList.remove('is-invalid');
        }
    });

    // City validation (should be Bhaktapur)
    cityInput.addEventListener('change', function() {
        if (this.value.toLowerCase() !== 'bhaktapur') {
            this.classList.add('is-invalid');
            showError('We only deliver within Bhaktapur city.');
        } else {
            this.classList.remove('is-invalid');
        }
    });

    // State validation (should be Bagmati)
    stateInput.addEventListener('change', function() {
        if (this.value !== 'Bagmati') {
            this.classList.add('is-invalid');
            showError('Please select Bagmati Province.');
        } else {
            this.classList.remove('is-invalid');
        }
    });

    // Ward number validation
    zipInput.addEventListener('change', function() {
        if (this.value && !validateWardNumber(this.value)) {
            this.classList.add('is-invalid');
            showError('Please select a valid ward number for Bhaktapur.');
        } else {
            this.classList.remove('is-invalid');
        }
    });

    // Form submission handler
    codForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form before submission
        if (!validateForm()) {
            return;
        }

        // Check payment method and handle accordingly
        if (esewaOption.checked) {
            handleEsewaPayment();
        } else {
            handleCODOrder();
        }
    });

    function validateForm() {
        const requiredFields = [
            'firstName', 'lastName', 'email', 'phone', 
            'address', 'city', 'state', 'zip'
        ];
        
        let isValid = true;
        
        requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Specific validations
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const city = document.getElementById('city').value;
        const state = document.getElementById('state').value;
        const zip = document.getElementById('zip').value;

        if (email && !validateEmail(email)) {
            document.getElementById('email').classList.add('is-invalid');
            isValid = false;
        }

        if (phone && !validatePhone(phone)) {
            document.getElementById('phone').classList.add('is-invalid');
            isValid = false;
        }

        if (city.toLowerCase() !== 'bhaktapur') {
            document.getElementById('city').classList.add('is-invalid');
            showError('We only deliver within Bhaktapur city.');
            isValid = false;
        }

        if (state !== 'Bagmati') {
            document.getElementById('state').classList.add('is-invalid');
            showError('Please select Bagmati Province.');
            isValid = false;
        }

        if (zip && !validateWardNumber(zip)) {
            document.getElementById('zip').classList.add('is-invalid');
            showError('Please select a valid ward number for Bhaktapur.');
            isValid = false;
        }

        if (!isValid) {
            showError('Please fill in all required fields correctly.');
        }

        return isValid;
    }

    function handleCODOrder() {
        // Disable submit button to prevent double submission
        codSubmitBtn.disabled = true;
        codSubmitBtn.innerHTML = 'Processing... <i data-feather="loader" class="rotating"></i>';
        feather.replace();

        // Create FormData from the form
        const formData = new FormData(codForm);

        fetch(codForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.redirected) {
                // If redirected (successful order), follow the redirect
                window.location.href = response.url;
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && !data.success) {
                showError(data.error || 'An error occurred. Please try again.');
                resetSubmitButton();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred. Please try again.');
            resetSubmitButton();
        });
    }

    function handleEsewaPayment() {
        // Disable submit button
        codSubmitBtn.disabled = true;
        codSubmitBtn.innerHTML = 'Processing... <i data-feather="loader" class="rotating"></i>';
        feather.replace();

        // For eSewa, we need to submit to process_delivery_order first to create the order
        // then redirect to initiate_payment
        const formData = new FormData(codForm);

        fetch(codForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.redirected) {
                // Follow the redirect to payment page
                window.location.href = response.url;
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && !data.success) {
                showError(data.error || 'An error occurred. Please try again.');
                resetSubmitButton();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred. Please try again.');
            resetSubmitButton();
        });
    }

    function resetSubmitButton() {
        codSubmitBtn.disabled = false;
        if (esewaOption.checked) {
            codSubmitBtn.innerHTML = 'Pay with eSewa <i data-feather="credit-card"></i>';
        } else {
            codSubmitBtn.innerHTML = 'Complete Order <i data-feather="check"></i>';
        }
        feather.replace();
    }

    function showError(message) {
        // Remove any existing error alerts
        const existingAlert = document.querySelector('.alert-danger');
        if (existingAlert) {
            existingAlert.remove();
        }

        // Create error alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the form
        const form = document.getElementById('codForm');
        form.insertBefore(alertDiv, form.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);

        // Scroll to top to show the error
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function showSuccess(message) {
        // Remove any existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create success alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <strong>Success:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the container
        const container = document.querySelector('.main-container');
        container.insertBefore(alertDiv, container.firstChild);

        // Scroll to top to show the success message
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Add CSS for rotating loader
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .rotating {
            animation: rotate 1s linear infinite;
        }
    `;
    document.head.appendChild(style);

    // Initialize form state
    handlePaymentMethodChange();


// Global function for redirecting after success (if needed)
function redirectToSouvenirs() {
    window.location.href = '/souvenirs/';
}