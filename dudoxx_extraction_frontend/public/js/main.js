/**
 * Dudoxx Extraction Frontend - Main.js
 * 
 * This script provides common functionality for the Dudoxx Extraction Frontend.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
  
  // Auto-dismiss alerts
  const autoDismissAlerts = document.querySelectorAll('.alert-dismissible.auto-dismiss');
  autoDismissAlerts.forEach(function(alert) {
    setTimeout(function() {
      const closeButton = alert.querySelector('.btn-close');
      if (closeButton) {
        closeButton.click();
      } else {
        alert.classList.add('fade');
        setTimeout(function() {
          alert.remove();
        }, 150);
      }
    }, 5000);
  });
  
  // Handle tab selection from URL hash
  const handleTabFromHash = () => {
    const hash = window.location.hash;
    if (hash) {
      const tabId = hash.replace('#', '');
      const tab = document.querySelector(`[data-bs-target="#${tabId}"]`);
      if (tab) {
        const tabInstance = new bootstrap.Tab(tab);
        tabInstance.show();
      }
    }
  };
  
  // Call on page load
  handleTabFromHash();
  
  // Call when hash changes
  window.addEventListener('hashchange', handleTabFromHash);
  
  // Update hash when tab is shown
  const tabElList = [].slice.call(document.querySelectorAll('a[data-bs-toggle="tab"]'));
  tabElList.forEach(function(tabEl) {
    tabEl.addEventListener('shown.bs.tab', function(event) {
      const target = event.target.getAttribute('data-bs-target');
      if (target) {
        const targetId = target.replace('#', '');
        window.location.hash = targetId;
      }
    });
  });
  
  // Format JSON output with syntax highlighting
  const formatJsonOutput = () => {
    const jsonElements = document.querySelectorAll('.json-output');
    jsonElements.forEach(function(element) {
      try {
        const jsonText = element.textContent;
        const json = JSON.parse(jsonText);
        const formattedJson = JSON.stringify(json, null, 2);
        
        // Replace JSON syntax with HTML for syntax highlighting
        const highlighted = formattedJson
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
            let cls = 'json-number';
            if (/^"/.test(match)) {
              if (/:$/.test(match)) {
                cls = 'json-key';
              } else {
                cls = 'json-string';
              }
            } else if (/true|false/.test(match)) {
              cls = 'json-boolean';
            } else if (/null/.test(match)) {
              cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
          });
        
        element.innerHTML = highlighted;
      } catch (e) {
        console.error('Error formatting JSON:', e);
      }
    });
  };
  
  // Format JSON on page load
  formatJsonOutput();
  
  // Copy to clipboard functionality
  const copyButtons = document.querySelectorAll('.btn-copy');
  copyButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      const target = document.querySelector(button.getAttribute('data-copy-target'));
      if (target) {
        navigator.clipboard.writeText(target.textContent)
          .then(() => {
            // Show success message
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.classList.add('btn-success');
            button.classList.remove('btn-secondary');
            
            // Reset button after 2 seconds
            setTimeout(() => {
              button.textContent = originalText;
              button.classList.remove('btn-success');
              button.classList.add('btn-secondary');
            }, 2000);
          })
          .catch(err => {
            console.error('Error copying text:', err);
          });
      }
    });
  });
  
  // Handle form submission with AJAX
  const ajaxForms = document.querySelectorAll('form.ajax-form');
  ajaxForms.forEach(function(form) {
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      
      // Get form data
      const formData = new FormData(form);
      
      // Get form action and method
      const action = form.getAttribute('action') || window.location.href;
      const method = form.getAttribute('method') || 'POST';
      
      // Show loading indicator
      const submitButton = form.querySelector('[type="submit"]');
      if (submitButton) {
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
      }
      
      // Send request
      fetch(action, {
        method: method,
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        // Handle response
        if (data.success) {
          // Show success message
          const successMessage = form.getAttribute('data-success-message') || 'Operation completed successfully';
          showAlert('success', successMessage);
          
          // Redirect if specified
          const redirectUrl = form.getAttribute('data-redirect');
          if (redirectUrl) {
            window.location.href = redirectUrl;
          }
          
          // Reset form if specified
          if (form.getAttribute('data-reset') === 'true') {
            form.reset();
          }
        } else {
          // Show error message
          const errorMessage = data.message || 'An error occurred';
          showAlert('danger', errorMessage);
        }
      })
      .catch(error => {
        // Show error message
        showAlert('danger', 'An error occurred: ' + error.message);
      })
      .finally(() => {
        // Reset submit button
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = originalText;
        }
      });
    });
  });
  
  /**
   * Show an alert message
   * 
   * @param {string} type - The alert type (success, danger, warning, info)
   * @param {string} message - The alert message
   */
  function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alert.classList.remove('show');
      setTimeout(() => {
        alert.remove();
      }, 150);
    }, 5000);
  }
});
