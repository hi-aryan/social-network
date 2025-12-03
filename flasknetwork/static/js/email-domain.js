// Email domain button functionality
function setupEmailDomainButton(emailFieldId, buttonId) {
    const emailField = document.getElementById(emailFieldId);
    const domainBtn = document.getElementById(buttonId);
    
    if (emailField && domainBtn) {
        domainBtn.addEventListener('click', function() {
            const currentValue = emailField.value.trim();
            const domain = '@kth.se';
            
            // If field is empty, set to @kth.se
            if (currentValue === '') {
                emailField.value = domain;
            }
            // If field doesn't already end with @kth.se, append it
            else if (!currentValue.toLowerCase().endsWith(domain.toLowerCase())) {
                // Remove any existing @ symbol and domain, then add @kth.se
                const baseValue = currentValue.split('@')[0];
                emailField.value = baseValue + domain;
            }
            // If already has @kth.se, do nothing
            
            // Remove any error styling
            emailField.classList.remove('is-invalid');
            // Trigger input event for validation
            emailField.dispatchEvent(new Event('input'));
        });
    }
}

