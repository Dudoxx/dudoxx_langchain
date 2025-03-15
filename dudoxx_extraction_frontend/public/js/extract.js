/**
 * Dudoxx Extraction Frontend - Extract.js
 * 
 * This script handles the extraction functionality for the Dudoxx Extraction Frontend.
 * It manages form submissions, API calls, and result display.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize forms
  const textExtractionForm = document.getElementById('textExtractionForm');
  const fileExtractionForm = document.getElementById('fileExtractionForm');
  const multiQueryExtractionForm = document.getElementById('multiQueryExtractionForm');
  
  // Initialize progress and results sections
  const progressSection = document.getElementById('progressSection');
  const progressBar = document.getElementById('progressBar');
  const progressMessage = document.getElementById('progressMessage');
  const resultsSection = document.getElementById('resultsSection');
  
  // Initialize result display elements
  const jsonResult = document.getElementById('jsonResult');
  const textResult = document.getElementById('textResult');
  const metadataResult = document.getElementById('metadataResult');
  const viewFullResultsButton = document.getElementById('viewFullResultsButton');
  
  // Set up form validation
  setupFormValidation(textExtractionForm);
  setupFormValidation(fileExtractionForm);
  setupFormValidation(multiQueryExtractionForm);
  
  // Set up form submission handlers
  if (textExtractionForm) {
    textExtractionForm.addEventListener('submit', function(event) {
      event.preventDefault();
      if (textExtractionForm.checkValidity()) {
        handleTextExtraction();
      }
      textExtractionForm.classList.add('was-validated');
    });
  }
  
  if (fileExtractionForm) {
    fileExtractionForm.addEventListener('submit', function(event) {
      event.preventDefault();
      if (fileExtractionForm.checkValidity()) {
        handleFileExtraction();
      }
      fileExtractionForm.classList.add('was-validated');
    });
  }
  
  if (multiQueryExtractionForm) {
    multiQueryExtractionForm.addEventListener('submit', function(event) {
      event.preventDefault();
      if (multiQueryExtractionForm.checkValidity()) {
        handleMultiQueryExtraction();
      }
      multiQueryExtractionForm.classList.add('was-validated');
    });
  }
  
  // Set up view full results button
  if (viewFullResultsButton) {
    viewFullResultsButton.addEventListener('click', function() {
      // Save the current result to session and redirect to results page
      if (window.currentResult) {
        fetch('/results/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(window.currentResult)
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            window.location.href = '/results';
          }
        })
        .catch(error => {
          console.error('Error saving results:', error);
        });
      }
    });
  }
  
  /**
   * Set up form validation
   * 
   * @param {HTMLFormElement} form - The form to set up validation for
   */
  function setupFormValidation(form) {
    if (!form) return;
    
    // Add event listener to prevent form submission if invalid
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  }
  
  /**
   * Handle text extraction form submission
   */
  function handleTextExtraction() {
    // Show progress section
    showProgress();
    
    // Get form data
    const query = document.getElementById('textQuery').value;
    const text = document.getElementById('textContent').value;
    const domain = document.getElementById('textDomain').value;
    const useParallel = document.getElementById('textUseParallel').checked;
    
    // Prepare request data
    const requestData = {
      query,
      text,
      domain: domain || undefined,
      useParallel: useParallel ? 'true' : 'false',
      outputFormats: ['json', 'text']
    };
    
    // Show loading spinner
    toggleLoadingSpinner('textExtractButton', true);
    
    // Send request to API
    fetch('/api/extract/text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
      // Hide loading spinner
      toggleLoadingSpinner('textExtractButton', false);
      
      // Handle response
      handleExtractionResponse(data);
    })
    .catch(error => {
      // Hide loading spinner
      toggleLoadingSpinner('textExtractButton', false);
      
      // Show error
      console.error('Error extracting text:', error);
      updateProgress({
        status: 'error',
        message: 'Error extracting text: ' + error.message
      });
    });
  }
  
  /**
   * Handle file extraction form submission
   */
  function handleFileExtraction() {
    // Show progress section
    showProgress();
    
    // Get form data
    const query = document.getElementById('fileQuery').value;
    const fileInput = document.getElementById('fileUpload');
    const domain = document.getElementById('fileDomain').value;
    const useParallel = document.getElementById('fileUseParallel').checked;
    
    // Check if file is selected
    if (!fileInput.files || fileInput.files.length === 0) {
      updateProgress({
        status: 'error',
        message: 'Please select a file to upload'
      });
      return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('query', query);
    if (domain) formData.append('domain', domain);
    formData.append('useParallel', useParallel ? 'true' : 'false');
    formData.append('outputFormats', 'json,text');
    
    // Show loading spinner
    toggleLoadingSpinner('fileExtractButton', true);
    
    // Send request to API
    fetch('/api/extract/file', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      // Hide loading spinner
      toggleLoadingSpinner('fileExtractButton', false);
      
      // Handle response
      handleExtractionResponse(data);
    })
    .catch(error => {
      // Hide loading spinner
      toggleLoadingSpinner('fileExtractButton', false);
      
      // Show error
      console.error('Error extracting file:', error);
      updateProgress({
        status: 'error',
        message: 'Error extracting file: ' + error.message
      });
    });
  }
  
  /**
   * Handle multi-query extraction form submission
   */
  function handleMultiQueryExtraction() {
    // Show progress section
    showProgress();
    
    // Get form data
    const queriesText = document.getElementById('multiQueryList').value;
    const text = document.getElementById('multiQueryContent').value;
    const domain = document.getElementById('multiQueryDomain').value;
    const useParallel = document.getElementById('multiQueryUseParallel').checked;
    
    // Parse queries (one per line)
    const queries = queriesText.split('\n')
      .map(q => q.trim())
      .filter(q => q.length > 0);
    
    // Check if queries are provided
    if (queries.length === 0) {
      updateProgress({
        status: 'error',
        message: 'Please enter at least one query'
      });
      return;
    }
    
    // Prepare request data
    const requestData = {
      queries,
      text,
      domain: domain || undefined,
      useParallel: useParallel ? 'true' : 'false',
      outputFormats: ['json', 'text']
    };
    
    // Show loading spinner
    toggleLoadingSpinner('multiQueryExtractButton', true);
    
    // Send request to API
    fetch('/api/extract/multi-query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
      // Hide loading spinner
      toggleLoadingSpinner('multiQueryExtractButton', false);
      
      // Handle response
      handleExtractionResponse(data);
    })
    .catch(error => {
      // Hide loading spinner
      toggleLoadingSpinner('multiQueryExtractButton', false);
      
      // Show error
      console.error('Error extracting with multiple queries:', error);
      updateProgress({
        status: 'error',
        message: 'Error extracting with multiple queries: ' + error.message
      });
    });
  }
  
  /**
   * Handle extraction response
   * 
   * @param {Object} data - The response data from the API
   */
  function handleExtractionResponse(data) {
    // Store current result for later use
    window.currentResult = data;
    
    // Update progress
    updateProgress({
      status: data.status === 'success' ? 'completed' : 'error',
      message: data.status === 'success' ? 'Extraction completed successfully' : 'Extraction failed: ' + (data.error_message || 'Unknown error')
    });
    
    // Show results if successful
    if (data.status === 'success' && data.extraction_result) {
      showResults(data.extraction_result);
    }
  }
  
  /**
   * Show progress section and reset progress
   */
  function showProgress() {
    progressSection.classList.remove('d-none');
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.classList.remove('bg-success', 'bg-danger');
    progressBar.classList.add('bg-primary');
    progressMessage.textContent = 'Preparing extraction...';
    
    // Hide results section
    resultsSection.classList.add('d-none');
  }
  
  /**
   * Update progress based on status
   * 
   * @param {Object} data - The progress data
   * @param {string} data.status - The progress status (starting, processing, completed, error)
   * @param {string} data.message - The progress message
   */
  function updateProgress(data) {
    let percentage = 0;
    
    // Set percentage based on status
    switch (data.status) {
      case 'starting':
        percentage = 10;
        progressBar.classList.remove('bg-success', 'bg-danger');
        progressBar.classList.add('bg-primary');
        break;
      case 'processing':
        percentage = 50;
        progressBar.classList.remove('bg-success', 'bg-danger');
        progressBar.classList.add('bg-primary');
        break;
      case 'completed':
        percentage = 100;
        progressBar.classList.remove('bg-primary', 'bg-danger');
        progressBar.classList.add('bg-success');
        break;
      case 'error':
        percentage = 100;
        progressBar.classList.remove('bg-primary', 'bg-success');
        progressBar.classList.add('bg-danger');
        break;
      default:
        percentage = 0;
    }
    
    // Update progress bar
    progressBar.style.width = percentage + '%';
    progressBar.setAttribute('aria-valuenow', percentage);
    
    // Update progress message
    progressMessage.textContent = data.message || 'Processing...';
  }
  
  /**
   * Show results section and populate with data
   * 
   * @param {Object} result - The extraction result
   */
  function showResults(result) {
    resultsSection.classList.remove('d-none');
    
    // Populate JSON result
    if (result.json_output) {
      jsonResult.textContent = JSON.stringify(result.json_output, null, 2);
    } else {
      jsonResult.textContent = 'No JSON output available';
    }
    
    // Populate text result
    if (result.text_output) {
      textResult.textContent = result.text_output;
    } else {
      textResult.textContent = 'No text output available';
    }
    
    // Populate metadata result
    if (result.metadata) {
      metadataResult.textContent = JSON.stringify(result.metadata, null, 2);
    } else {
      metadataResult.textContent = 'No metadata available';
    }
  }
  
  /**
   * Toggle loading spinner on a button
   * 
   * @param {string} buttonId - The ID of the button
   * @param {boolean} show - Whether to show or hide the spinner
   */
  function toggleLoadingSpinner(buttonId, show) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    const spinner = button.querySelector('.spinner-border');
    if (!spinner) return;
    
    if (show) {
      spinner.classList.remove('d-none');
      button.disabled = true;
    } else {
      spinner.classList.add('d-none');
      button.disabled = false;
    }
  }
});

/**
 * Update progress from socket.io events
 * This function is called from the socket.io event listener in the extract.ejs template
 * 
 * @param {Object} data - The progress data
 */
function updateProgress(data) {
  const progressSection = document.getElementById('progressSection');
  const progressBar = document.getElementById('progressBar');
  const progressMessage = document.getElementById('progressMessage');
  
  if (!progressSection || !progressBar || !progressMessage) return;
  
  let percentage = 0;
  
  // Set percentage based on status
  switch (data.status) {
    case 'starting':
      percentage = 10;
      progressBar.classList.remove('bg-success', 'bg-danger');
      progressBar.classList.add('bg-primary');
      break;
    case 'processing':
      percentage = 50;
      progressBar.classList.remove('bg-success', 'bg-danger');
      progressBar.classList.add('bg-primary');
      break;
    case 'completed':
      percentage = 100;
      progressBar.classList.remove('bg-primary', 'bg-danger');
      progressBar.classList.add('bg-success');
      break;
    case 'error':
      percentage = 100;
      progressBar.classList.remove('bg-primary', 'bg-success');
      progressBar.classList.add('bg-danger');
      break;
    default:
      percentage = 0;
  }
  
  // Update progress bar
  progressBar.style.width = percentage + '%';
  progressBar.setAttribute('aria-valuenow', percentage);
  
  // Update progress message
  progressMessage.textContent = data.message || 'Processing...';
  
  // Show progress section if hidden
  progressSection.classList.remove('d-none');
}
