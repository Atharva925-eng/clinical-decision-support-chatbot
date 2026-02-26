/**
 * Clinical Decision-Support Chatbot - Frontend Script
 * Handles form submission, results display, and user interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    const symptomForm = document.getElementById('symptomForm');
    const symptomsInput = document.getElementById('symptoms');
    const resultsSection = document.getElementById('resultsSection');
    const emptyState = document.getElementById('emptyState');

    // Form submission handler
    symptomForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Capture and validate symptom input
        const symptoms = symptomsInput.value.trim();
        
        console.log('=== Symptom Analysis Started ===');
        console.log('Raw input:', symptomsInput.value);
        console.log('Trimmed input:', symptoms);
        
        // Prevent empty submissions
        if (!symptoms) {
            console.warn('Submission blocked: Empty symptom input');
            showNotification('Please enter at least one symptom', 'error');
            symptomsInput.focus();
            return;
        }

        console.log('Input validation passed');

        // Show results section and hide empty state
        resultsSection.style.display = 'block';
        emptyState.style.display = 'none';

        // Show loading state
        setLoadingState();

        try {
            // Send symptoms to Flask backend API
            console.log('Sending request to /predict endpoint...');
            const data = await analyzeWithAPI(symptoms);
            
            console.log('✅ Analysis successful');
            console.log('Backend response:', data);
            
            // Populate results
            displayResults(data);
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error('❌ Error during analysis:', error);
            console.error('Error message:', error.message);
            
            // Display error message gracefully
            if (error.message.includes('insufficient')) {
                showNotification('Please provide more symptoms for accurate analysis', 'error');
            } else {
                showNotification('An error occurred while analyzing symptoms. Please try again.', 'error');
            }
            
            // Clear loading state on error
            const containers = ['diseasesContainer', 'reasoningContainer', 'descriptionContainer', 
                              'medicationsContainer', 'precautionsContainer', 'dietContainer'];
            containers.forEach(id => {
                document.getElementById(id).innerHTML = '<p class="error-message">Error loading results. Please try again.</p>';
            });
        }
    });



    /**
     * Sends symptom data to Flask backend for analysis
     * Handles the API request with proper error handling
     * @param {String} symptoms - User input symptoms
     * @returns {Promise<Object>} Analysis data from Flask API
     * @throws {Error} If API call fails or returns invalid response
     */
    async function analyzeWithAPI(symptoms) {
        try {
            // Prepare request payload
            const payload = {
                symptoms: symptoms
            };

            console.log('--- API Request Details ---');
            console.log('Endpoint:', '/predict');
            console.log('Method:', 'POST');
            console.log('Headers:', { 'Content-Type': 'application/json' });
            console.log('Payload:', payload);

            // Send POST request to Flask /predict endpoint
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            console.log('--- API Response Details ---');
            console.log('Status:', response.status);
            console.log('Status Text:', response.statusText);
            console.log('Headers:', {
                'Content-Type': response.headers.get('Content-Type')
            });

            // Parse JSON response safely (even for error responses)
            let data;
            try {
                const responseText = await response.text();
                console.log('Raw Response Body:', responseText);
                
                data = JSON.parse(responseText);
                console.log('Parsed JSON:', data);
            } catch (parseError) {
                console.error('Failed to parse JSON response:', parseError);
                throw new Error('Invalid response format from server');
            }

            // Check if API returned an error (even if HTTP status was 400)
            if (!response.ok || (data && data.error)) {
                const errorMessage = data?.error || `HTTP ${response.status}: ${response.statusText}`;
                console.error('API returned error:', errorMessage);
                
                // Throw error with original message (form handler will catch and handle appropriately)
                throw new Error(errorMessage);
            }

            // Validate response structure
            if (!data || typeof data !== 'object') {
                throw new Error('Empty or invalid response from server');
            }

            // Check if analysis was successful
            if (!data.success) {
                throw new Error(data.error || 'Analysis failed');
            }

            // Return data with fallback values for missing fields
            const result = {
                success: data.success || false,
                received_symptoms: data.received_symptoms || '',
                matched_symptoms: data.matched_symptoms || [],
                diseases: data.diseases || [],
                reasoning: data.reasoning || 'No reasoning available',
                description: data.description || 'No description available',
                medications: data.medications || [],
                precautions: data.precautions || [],
                diet: data.diet || { recommended: [], avoid: [] },
                disclaimer: data.disclaimer || ''
            };
            
            console.log('--- Processed Result ---');
            console.log('Final data structure:', result);
            
            return result;

        } catch (error) {
            console.error('=== API Error Summary ===');
            console.error('Error Type:', error.constructor.name);
            console.error('Error Message:', error.message);
            console.error('Full Error:', error);
            throw error;
        }
    }



    /**
     * Sets loading state in all result containers
     */
    function setLoadingState() {
        const containers = [
            'diseasesContainer',
            'reasoningContainer',
            'descriptionContainer',
            'medicationsContainer',
            'precautionsContainer',
            'dietContainer'
        ];

        containers.forEach(id => {
            const container = document.getElementById(id);
            container.innerHTML = '<p class="loading">Analyzing symptoms...</p>';
        });
    }

    /**
     * Displays results from the analysis
     * @param {Object} data - Response data (from API or placeholder)
     */
    function displayResults(data) {
        // Display predicted diseases
        displayDiseases(data.diseases || []);

        // Display reasoning
        displayReasoning(data.reasoning || 'No reasoning available');

        // Display description
        displayDescription(data.description || 'No description available');

        // Display medications
        displayMedications(data.medications || []);

        // Display precautions
        displayPrecautions(data.precautions || []);

        // Display diet recommendations
        displayDiet(data.diet || 'No diet recommendations available');
        
        // Display disclaimer from backend
        if (data.disclaimer) {
            displayDisclaimer(data.disclaimer);
        }
    }

    /**
     * Displays predicted diseases with confidence scores
     * @param {Array} diseases - Array of disease objects with name and confidence
     */
    function displayDiseases(diseases) {
        const container = document.getElementById('diseasesContainer');
        
        if (!diseases || !Array.isArray(diseases) || diseases.length === 0) {
            container.innerHTML = '<p class="text-muted">No diseases identified based on symptoms</p>';
            return;
        }

        try {
            container.innerHTML = diseases.map((disease, index) => {
                if (!disease || !disease.name) return '';
                const confidence = disease.confidence ? (disease.confidence * 100).toFixed(1) : 'N/A';
                return `
                    <div class="disease-item">
                        <span class="disease-name">${index + 1}. ${escapeHtml(disease.name)}</span>
                        <span class="disease-confidence">${confidence}${disease.confidence ? '%' : ''}</span>
                    </div>
                `;
            }).filter(html => html).join('');
        } catch (error) {
            console.error('Error displaying diseases:', error);
            container.innerHTML = '<p class="error-message">Error displaying disease results</p>';
        }
    }

    /**
     * Displays clinical reasoning for diagnosis
     * @param {String} reasoning - Detailed reasoning text
     */
    function displayReasoning(reasoning) {
        const container = document.getElementById('reasoningContainer');
        
        if (!reasoning || reasoning.trim() === '') {
            container.innerHTML = '<p class="text-muted">No reasoning available</p>';
            return;
        }

        try {
            container.innerHTML = `<p>${escapeHtml(reasoning)}</p>`;
        } catch (error) {
            console.error('Error displaying reasoning:', error);
            container.innerHTML = '<p class="error-message">Error displaying reasoning</p>';
        }
    }

    /**
     * Displays disease description and overview
     * @param {String} description - Disease description text
     */
    function displayDescription(description) {
        const container = document.getElementById('descriptionContainer');
        
        if (!description || description.trim() === '') {
            container.innerHTML = '<p class="text-muted">No description available</p>';
            return;
        }

        try {
            container.innerHTML = `<p>${escapeHtml(description)}</p>`;
        } catch (error) {
            console.error('Error displaying description:', error);
            container.innerHTML = '<p class="error-message">Error displaying description</p>';
        }
    }

    /**
     * Displays recommended medications with dosage information
     * @param {Array} medications - Array of medication objects
     */
    function displayMedications(medications) {
        const container = document.getElementById('medicationsContainer');
        
        if (!medications || !Array.isArray(medications) || medications.length === 0) {
            container.innerHTML = '<p class="text-muted">No medications recommended</p>';
            return;
        }

        try {
            container.innerHTML = medications.map((med, index) => {
                if (!med || !med.name) return '';
                return `
                    <div class="medication-item">
                        <div class="medication-name">${index + 1}. ${escapeHtml(med.name)}</div>
                        <div class="medication-dosage">${escapeHtml(med.dosage || 'As prescribed by healthcare provider')}</div>
                    </div>
                `;
            }).filter(html => html).join('');
        } catch (error) {
            console.error('Error displaying medications:', error);
            container.innerHTML = '<p class="error-message">Error displaying medications</p>';
        }
    }

    /**
     * Displays important precautions and warnings
     * @param {Array} precautions - Array of precaution strings
     */
    function displayPrecautions(precautions) {
        const container = document.getElementById('precautionsContainer');
        
        if (!precautions || !Array.isArray(precautions) || precautions.length === 0) {
            container.innerHTML = '<p class="text-muted">No precautions available</p>';
            return;
        }

        try {
            container.innerHTML = precautions.map((precaution, index) => {
                if (!precaution || precaution.trim() === '') return '';
                return `
                    <div class="precaution-item">
                        <span class="precaution-icon">⚠️</span>
                        <span class="precaution-text">${escapeHtml(precaution)}</span>
                    </div>
                `;
            }).filter(html => html).join('');
        } catch (error) {
            console.error('Error displaying precautions:', error);
            container.innerHTML = '<p class="error-message">Error displaying precautions</p>';
        }
    }

    /**
     * Displays diet recommendations with recommended and foods to avoid
     * @param {String|Object} diet - Diet recommendations (text or structured object)
     */
    function displayDiet(diet) {
        const container = document.getElementById('dietContainer');
        
        if (!diet) {
            container.innerHTML = '<p class="text-muted">No diet recommendations available</p>';
            return;
        }

        try {
            if (typeof diet === 'object' && diet !== null) {
                let html = '';
                
                // Display recommended foods
                if (diet.recommended && Array.isArray(diet.recommended) && diet.recommended.length > 0) {
                    html += `
                        <div class="diet-section">
                            <h4>✅ Recommended Foods:</h4>
                            <ul class="diet-list">
                                ${diet.recommended.map(food => {
                                    if (!food || food.trim() === '') return '';
                                    return `<li>${escapeHtml(food)}</li>`;
                                }).filter(item => item).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                // Display foods to avoid
                if (diet.avoid && Array.isArray(diet.avoid) && diet.avoid.length > 0) {
                    html += `
                        <div class="diet-section">
                            <h4>❌ Foods to Avoid:</h4>
                            <ul class="diet-list diet-avoid">
                                ${diet.avoid.map(food => {
                                    if (!food || food.trim() === '') return '';
                                    return `<li>${escapeHtml(food)}</li>`;
                                }).filter(item => item).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                container.innerHTML = html || '<p class="text-muted">No specific diet recommendations</p>';
            } else if (typeof diet === 'string') {
                container.innerHTML = `<p>${escapeHtml(diet)}</p>`;
            } else {
                container.innerHTML = '<p class="text-muted">No diet recommendations available</p>';
            }
        } catch (error) {
            console.error('Error displaying diet:', error);
            container.innerHTML = '<p class="error-message">Error displaying diet recommendations</p>';
        }
    }

    /**
     * Displays medical disclaimer from backend response
     * @param {String} disclaimer - Disclaimer text from backend
     */
    function displayDisclaimer(disclaimer) {
        const container = document.getElementById('disclaimerContainer');
        
        if (!disclaimer || disclaimer.trim() === '') {
            return;
        }

        try {
            // Replace line breaks with proper formatting
            const disclaimerText = escapeHtml(disclaimer)
                .split('\n')
                .filter(line => line.trim() !== '')
                .join('<br>');
            
            container.innerHTML = disclaimerText;
            
            console.log('✅ Disclaimer displayed');
        } catch (error) {
            console.error('Error displaying disclaimer:', error);
        }
    }

    /**
     * Escapes HTML special characters to prevent XSS attacks
     * @param {String} text - Text to escape
     * @returns {String} Escaped text safe for HTML display
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Keyboard shortcut: Ctrl+Enter to submit form
     */
    symptomsInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            symptomForm.dispatchEvent(new Event('submit'));
        }
    });
});

/**
 * Utility function to format percentage values
 * @param {Number} value - Value between 0 and 1
 * @returns {String} Formatted percentage string
 */
function formatPercentage(value) {
    return `${(value * 100).toFixed(1)}%`;
}

/**
 * Utility function to display notifications
 * @param {String} message - Message to display
 * @param {String} type - Type: 'success', 'error', 'info', 'warning'
 */
function showNotification(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] [${type.toUpperCase()}] ${message}`);
    
    // TODO: Future enhancement - add visual toast notifications to UI
    // This can be implemented with a notification component
}
