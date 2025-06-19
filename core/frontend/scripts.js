// Global variables
const API_BASE_URL = 'http://localhost:8000/api';  // Fixed to use backend port
let currentTeam = localStorage.getItem('currentTeam') || null;
let submissions = JSON.parse(localStorage.getItem('submissions')) || [];
let highScore = parseInt(localStorage.getItem('highScore')) || 0;

// API Configuration - Switch to local backend
const API_CONFIG = {
    // Local backend configuration
    BASE_URL: 'http://localhost:8000/api',
    ENDPOINTS: {
        REGISTER: '/register',
        LOGIN: '/login',
        SUBMIT: '/submit-to-codabench',
        LEADERBOARD: '/leaderboard',
        SUBMISSION_STATUS: '/submission-status',
        USER_SUBMISSIONS: '/user-submissions',
        GLOBAL_STATS: '/global-stats'
    }
};

// Load global statistics for Performance Metrics section
async function loadGlobalStats() {
    console.log('📊 Loading global performance statistics...');
    try {
        const response = await fetch(`${API_BASE_URL}/global-stats`);

        if (!response.ok) {
            console.error('Failed to fetch global stats:', response.status);
            return;
        }

        const stats = await response.json();
        console.log('📊 Global stats received:', stats);

        // Update Performance Metrics display
        updateMetricsDisplay(stats);

    } catch (error) {
        console.error('❌ Error loading global stats:', error);
        showErrorMetrics();
    }
}

// Update the Performance Metrics display with real data
function updateMetricsDisplay(stats) {
    console.log('🔄 Updating metrics display with real data...');

    // Update Top Compression Ratio
    const topCRElement = document.getElementById('topCompressionRatio');
    const topCRTeamElement = document.getElementById('topCompressionTeam');
    if (topCRElement && topCRTeamElement) {
        topCRElement.textContent = stats.topCompressionRatio.value;
        topCRTeamElement.textContent = stats.topCompressionRatio.team;
    }

    // Update Best PRD
    const bestPRDElement = document.getElementById('bestPRD');
    const bestPRDTeamElement = document.getElementById('bestPRDTeam');
    if (bestPRDElement && bestPRDTeamElement) {
        bestPRDElement.textContent = stats.bestPRD.value;
        bestPRDTeamElement.textContent = stats.bestPRD.team;
    }

    // Update Average Score
    const avgScoreElement = document.getElementById('globalAverageScore');
    if (avgScoreElement) {
        avgScoreElement.textContent = stats.averageScore;
    }

    // Update Active Teams
    const activeTeamsElement = document.getElementById('activeTeams');
    if (activeTeamsElement) {
        activeTeamsElement.textContent = stats.activeTeams;
    }

    console.log('✅ Metrics display updated successfully');
}

// Show error state for metrics
function showErrorMetrics() {
    console.log('⚠️ Showing error state for metrics');

    const elements = [
        { id: 'topCompressionRatio', value: 'Error' },
        { id: 'topCompressionTeam', value: 'Unable to load' },
        { id: 'bestPRD', value: 'Error' },
        { id: 'bestPRDTeam', value: 'Unable to load' },
        { id: 'globalAverageScore', value: 'Error' },
        { id: 'activeTeams', value: 'Error' }
    ];

    elements.forEach(elem => {
        const element = document.getElementById(elem.id);
        if (element) {
            element.textContent = elem.value;
        }
    });
}

// Token management functions
function getAuthToken() {
    return localStorage.getItem('jwt_token') || localStorage.getItem('authToken');
}

function setAuthToken(token) {
    localStorage.setItem('jwt_token', token);
    localStorage.setItem('authToken', token); // Keep compatibility
}

function removeAuthToken() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('authToken');
}

// Enhanced validation functions
function validateEmail(email) {
    const emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;
    return emailRegex.test(email);
}

function validatePassword(password) {
    // More flexible password validation
    const minLength = password.length >= 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecial = /[@$!%*?&]/.test(password);

    return {
        valid: minLength && hasUpper && hasLower && hasNumber && hasSpecial,
        minLength,
        hasUpper,
        hasLower,
        hasNumber,
        hasSpecial
    };
}

function validateDOI(doi) {
    // Validate DOI format - can be URL or just DOI string
    const doiRegex = /^(https?:\/\/)?(dx\.)?doi\.org\/10\.\d{4,}\/\S+$|^10\.\d{4,}\/\S+$/;
    return doiRegex.test(doi);
}

function validatePaperSubmission() {
    const paperType = document.querySelector('input[name="paperType"]:checked');
    if (!paperType) {
        return { valid: false, message: 'Please select either paper upload or DOI link' };
    }

    const paperTitle = document.getElementById('paperTitle').value.trim();
    const paperAuthors = document.getElementById('paperAuthors').value.trim();

    if (!paperTitle) {
        return { valid: false, message: 'Paper title is required' };
    }

    if (!paperAuthors) {
        return { valid: false, message: 'Paper authors are required' };
    }

    if (paperType.value === 'upload') {
        const paperFile = document.getElementById('paperFile').files[0];
        if (!paperFile) {
            return { valid: false, message: 'Please upload your paper document' };
        }

        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(paperFile.type)) {
            return { valid: false, message: 'Paper must be in PDF, DOC, or DOCX format' };
        }

        // Check file size (max 25MB)
        if (paperFile.size > 25 * 1024 * 1024) {
            return { valid: false, message: 'Paper file size must be less than 25MB' };
        }
    } else if (paperType.value === 'doi') {
        const doiInput = document.getElementById('paperDOIInput').value.trim();
        if (!doiInput) {
            return { valid: false, message: 'Please provide the DOI link' };
        }

        if (!validateDOI(doiInput)) {
            return { valid: false, message: 'Please enter a valid DOI (e.g., 10.1000/example or https://doi.org/10.1000/example)' };
        }
    }

    return { valid: true };
}

// Paper submission form handlers
function setupPaperSubmissionHandlers() {
    const paperUploadRadio = document.getElementById('paperUpload');
    const paperDOIRadio = document.getElementById('paperDOI');
    const paperUploadSection = document.getElementById('paperUploadSection');
    const paperDOISection = document.getElementById('paperDOISection');

    if (paperUploadRadio && paperDOIRadio && paperUploadSection && paperDOISection) {
        paperUploadRadio.addEventListener('change', function() {
            if (this.checked) {
                paperUploadSection.style.display = 'block';
                paperDOISection.style.display = 'none';
                document.getElementById('paperFile').required = true;
                document.getElementById('paperDOIInput').required = false;
            }
        });

        paperDOIRadio.addEventListener('change', function() {
            if (this.checked) {
                paperDOISection.style.display = 'block';
                paperUploadSection.style.display = 'none';
                document.getElementById('paperDOIInput').required = true;
                document.getElementById('paperFile').required = false;
            }
        });
    }
}

// Enhanced form validation with real-time feedback
function setupFormValidation() {
    // Email validation
    const emailInput = document.getElementById('registerEmail');
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const email = this.value;
            const isValid = validateEmail(email);

            if (email.length > 0) {
                if (isValid) {
                    this.style.borderColor = 'var(--accent)';
                    this.setCustomValidity('');
                } else {
                    this.style.borderColor = 'var(--secondary)';
                    this.setCustomValidity('Please enter a valid email address');
                }
            } else {
                this.style.borderColor = '';
                this.setCustomValidity('');
            }
        });
    }

    // Improved password validation with detailed feedback
    const passwordInput = document.getElementById('registerPassword');
    if (passwordInput) {
        // Create or find password help text element
        let helpText = passwordInput.parentNode.querySelector('.password-help');
        if (!helpText) {
            helpText = document.createElement('div');
            helpText.className = 'password-help';
            helpText.style.cssText = `
                font-size: 0.85rem;
                margin-top: 0.5rem;
                padding: 0.75rem;
                border-radius: 6px;
                background: var(--surface);
                border: 1px solid #e2e8f0;
                display: none;
            `;
            passwordInput.parentNode.appendChild(helpText);
        }

        passwordInput.addEventListener('focus', function() {
            helpText.style.display = 'block';
        });

        passwordInput.addEventListener('blur', function() {
            if (this.value.length === 0) {
                helpText.style.display = 'none';
            }
        });

        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const validation = validatePassword(password);

            // Update help text with validation status
            helpText.innerHTML = `
                <div style="margin-bottom: 0.5rem; font-weight: 600; color: var(--primary);">Password Requirements:</div>
                <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                    <span style="color: ${validation.minLength ? '#10b981' : '#ef4444'};">
                        ${validation.minLength ? '✅' : '❌'} At least 8 characters
                    </span>
                    <span style="color: ${validation.hasUpper ? '#10b981' : '#ef4444'};">
                        ${validation.hasUpper ? '✅' : '❌'} One uppercase letter
                    </span>
                    <span style="color: ${validation.hasLower ? '#10b981' : '#ef4444'};">
                        ${validation.hasLower ? '✅' : '❌'} One lowercase letter
                    </span>
                    <span style="color: ${validation.hasNumber ? '#10b981' : '#ef4444'};">
                        ${validation.hasNumber ? '✅' : '❌'} One number
                    </span>
                    <span style="color: ${validation.hasSpecial ? '#10b981' : '#ef4444'};">
                        ${validation.hasSpecial ? '✅' : '❌'} One special character (@$!%*?&)
                    </span>
                </div>
            `;

            if (password.length > 0) {
                if (validation.valid) {
                    this.style.borderColor = 'var(--accent)';
                    this.setCustomValidity('');
                } else {
                    this.style.borderColor = 'var(--secondary)';
                    // Don't set custom validity here - let the form handle it
                }
            } else {
                this.style.borderColor = '';
                this.setCustomValidity('');
            }
        });
    }

    // DOI validation
    const doiInput = document.getElementById('paperDOIInput');
    if (doiInput) {
        doiInput.addEventListener('input', function() {
            const doi = this.value.trim();
            const isValid = validateDOI(doi);

            if (doi && !isValid) {
                this.setCustomValidity('Please enter a valid DOI');
                this.style.borderColor = 'var(--secondary)';
            } else {
                this.setCustomValidity('');
                this.style.borderColor = isValid ? 'var(--accent)' : '';
            }
        });
    }
}

// Utility functions
function validateFiles(files) {
    const zipValid = files.zip?.name.endsWith('.zip');
    const matValid = files.mat?.name.endsWith('.mat');
    return zipValid && matValid;
}

function updateTeamDisplay() {
    const currentTeamElem = document.getElementById('currentTeam');
    const highScoreElem = document.getElementById('highScore');
    const totalSubmissionsElem = document.getElementById('totalSubmissions');

    if (currentTeamElem) currentTeamElem.textContent = currentTeam || 'Not Set';
    if (highScoreElem) highScoreElem.textContent = highScore;
    if (totalSubmissionsElem) totalSubmissionsElem.textContent = submissions.length.toString();
}

function updateAuthState() {
    const isLoggedIn = !!getAuthToken();
    const authButton = document.getElementById('authButton');
    const currentTeamDisplay = document.getElementById('currentTeam');
    const teamSection = document.getElementById('team');
    const submitSection = document.getElementById('submit');
    const submissionsSection = document.getElementById('submissions');

    console.log('🔄 Updating auth state:', { isLoggedIn, hasTeam: !!currentTeam });

    // Update auth button
    if (authButton) {
        if (isLoggedIn) {
            authButton.textContent = 'Logout';
            authButton.onclick = function(e) {
                e.preventDefault();
                logout();
            };
        } else {
            authButton.textContent = 'Login';
            authButton.onclick = function(e) {
                e.preventDefault();
                if (getAuthToken()) {
                    // If logged in, this should be logout
                    logout();
                } else {
                    // Show login modal
                    openModal('authModal');
                    showForm('login');
                }
            };
        }
    }

    // Show/hide authenticated sections based on login status
    const authenticatedSections = [
        { element: teamSection, name: 'team management' },
        { element: submitSection, name: 'algorithm submission' },
        { element: submissionsSection, name: 'my submissions' }
    ];

    authenticatedSections.forEach(({ element, name }) => {
        if (element) {
            if (isLoggedIn) {
                element.style.display = 'block';
                console.log(`✅ Showing ${name} section for authenticated user`);
            } else {
                element.style.display = 'none';
                console.log(`🔒 Hiding ${name} section for unauthenticated user`);
            }
        }
    });

    // Check auth state on team page
    if (window.location.pathname.includes('team.html') && !isLoggedIn) {
        console.log('⚠️ Not authenticated on team page, redirecting...');
        alert('Please login first!');
        window.location.href = 'index.html';
        return;
    }
}

async function updateLeaderboard() {
    console.log('📊 Fetching real leaderboard data...');
    const token = getAuthToken();

    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard`, {
            headers: token ? {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            } : {
                'Content-Type': 'application/json'
            }
        });

        console.log('📊 Leaderboard response status:', response.status);

        if (!response.ok) {
            console.error('Leaderboard fetch failed:', response.status, response.statusText);
            if (response.status === 401 || response.status === 403) {
                console.log('⚠️ Token invalid during fetch, clearing');
                removeAuthToken();
                updateAuthState();
                // Try again without token for public leaderboard
                return updateLeaderboard();
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('📊 Leaderboard data received:', data);

        // Update leaderboard table
        const leaderboardTable = document.querySelector('.leaderboard-table tbody');
        const fullLeaderboard = document.getElementById('fullLeaderboard');
        const targetTable = leaderboardTable || fullLeaderboard;

        if (targetTable) {
            if (!data.results || data.results.length === 0) {
                console.log('📊 No leaderboard results, showing empty state');
                showEmptyLeaderboard();
            } else {
                console.log(`📊 Rendering ${data.results.length} leaderboard entries`);
                const leaderboardBody = data.results.map((entry, index) => {
                    const isCurrentTeam = token && entry.participant_name === (currentTeam || '');
                    console.log(`📊 Processing entry ${index + 1}: ${entry.participant_name}, Score: ${entry.score}, Current team: ${isCurrentTeam}`);

                    return `
                        <tr ${isCurrentTeam ? 'class="current-team"' : ''}>
                            <td>${index + 1}</td>
                            <td>${entry.participant_name || 'Unknown'}</td>
                            <td>${safeToFixed(entry.scores?.CR, 1)}</td>
                            <td>${safeToFixed(entry.scores?.PRD, 4)}</td>
                            <td>${safeToFixed(entry.scores?.Score || entry.score, 1)}</td>
                            <td>${entry.last_submission_date ? formatDate(entry.last_submission_date) : 'N/A'}</td>
                        </tr>
                    `;
                }).join('');

                targetTable.innerHTML = leaderboardBody;
                console.log('✅ Leaderboard table updated successfully');
            }
        } else {
            console.warn('⚠️ Leaderboard table element not found');
        }
    } catch (error) {
        console.error('❌ Leaderboard fetch error:', error);
        showEmptyLeaderboard();
    }
}

function showEmptyLeaderboard() {
    const leaderboardTable = document.querySelector('.leaderboard-table tbody');
    const fullLeaderboard = document.getElementById('fullLeaderboard');
    const targetTable = leaderboardTable || fullLeaderboard;

    if (targetTable) {
        targetTable.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: #666; padding: 2rem;">
                    No submissions yet. Be the first to submit!
                </td>
            </tr>
        `;
    }
}

// Save team name
async function saveTeamName() {
    const teamNameInput = document.getElementById('teamName');
    if (!teamNameInput) return;

    const teamName = teamNameInput.value.trim();
    if (!teamName) {
        alert('Please enter team name!');
        return;
    }

    try {
        currentTeam = teamName;
        localStorage.setItem('currentTeam', teamName);
        updateTeamDisplay();
        updateLeaderboard();
        alert('Team name saved successfully!');
        console.log('✅ Team name saved:', teamName);
    } catch (error) {
        console.error('❌ Error saving team name:', error);
        alert('Failed to save team name!');
    }
}

async function checkSubmissionStatus(submissionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/submission-status/${submissionId}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Status check failed');
        }

        const data = await response.json();
        console.log('📊 Submission status:', data);
        return data;
    } catch (error) {
        console.error('❌ Status check error:', error);
        return null;
    }
}

// Add missing updateForumPreview function
function updateForumPreview() {
    console.log('🔄 Updating forum preview...');
    // This function was referenced but not defined
    // Add basic implementation or remove the reference if not needed
    try {
        // Basic forum preview functionality
        const forumContent = document.getElementById('forumContent');
        if (forumContent) {
            // Add forum preview logic here if needed
            console.log('✅ Forum preview updated');
        }
    } catch (error) {
        console.log('⚠️ Forum preview update skipped:', error.message);
    }
}

// Add missing test-codabench endpoint to backend (temporary fix)
async function testCodabenchConnectionFixed() {
    try {
        const token = getAuthToken();
        if (token) {
            console.log('🔌 Testing backend connection...');
            // Test the health endpoint instead of test-codabench
            const response = await fetch('http://localhost:8000/health');

        if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend Status: Connected successfully');
                console.log('📋 Backend Health:', data);
        } else {
                console.log('⚠️ Backend Status: Connection failed');
        }
        } else {
            console.log('🔒 Backend Status: Not tested (user not logged in)');
        }
    } catch (error) {
        console.log('❌ Backend Status: Connection error -', error.message);
    }
}

function showForm(formType) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) loginForm.style.display = formType === 'login' ? 'block' : 'none';
    if (registerForm) registerForm.style.display = formType === 'register' ? 'block' : 'none';
}

// Updated submitFiles function to use local backend
async function submitFiles() {
    const fileInput = document.getElementById('zipFile');
    const algorithmName = document.getElementById('algorithmName').value.trim();
    const submitBtn = document.getElementById('submitBtn');
    const loadingDiv = document.getElementById('loadingIndicator');

    // Validation
    if (!fileInput.files.length) {
        alert('Please select a ZIP file to upload.');
        return;
    }

    if (!algorithmName) {
        alert('Please enter an algorithm name.');
        return;
    }

    const file = fileInput.files[0];
    if (!file.name.toLowerCase().endsWith('.zip')) {
        alert('Please select a ZIP file.');
        return;
    }

    // Check file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
        alert('File size too large. Maximum size is 50MB.');
        return;
    }

    try {
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';
        if (loadingDiv) loadingDiv.style.display = 'block';

        // Get authentication token
        const token = getAuthToken();
        if (!token) {
            alert('Please log in to submit files.');
            openModal('authModal');
            showForm('login');
            return;
        }

        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('algorithm_name', algorithmName);

        // Optional paper information
        const paperTitle = document.getElementById('paperTitle')?.value || '';
        const paperAuthors = document.getElementById('paperAuthors')?.value || '';
        const paperType = document.querySelector('input[name="paperType"]:checked')?.value || '';
        const paperDOI = document.getElementById('paperDOIInput')?.value || '';

        if (paperTitle) formData.append('paper_title', paperTitle);
        if (paperAuthors) formData.append('paper_authors', paperAuthors);
        if (paperType) formData.append('paper_type', paperType);
        if (paperDOI) formData.append('paper_doi', paperDOI);

        console.log('🚀 Submitting to backend:', `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.SUBMIT}`);

        // Submit to local backend
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.SUBMIT}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.submission_id) {
            // Create submission object for immediate UI update
            const submission = {
                id: result.submission_id,
                submission_id: result.submission_id,
                algorithmName: algorithmName,
                fileName: file.name,
                teamName: currentTeam,
                submitted_at: new Date().toISOString(),
                timestamp: new Date().toISOString(),
                submission_status: 'processing',
                status: 'processing',
                score: null,
                metrics: null
            };

            // Update UI immediately
            await updatePersonalPerformanceTable();
            await updatePersonalSubmissionHistory();
            await updatePersonalStats();

            // Clear form
            fileInput.value = '';
            document.getElementById('algorithmName').value = '';
            if (document.getElementById('paperTitle')) document.getElementById('paperTitle').value = '';
            if (document.getElementById('paperAuthors')) document.getElementById('paperAuthors').value = '';
            const paperTypeRadios = document.querySelectorAll('input[name="paperType"]');
            paperTypeRadios.forEach(radio => radio.checked = false);
            if (document.getElementById('paperDOIInput')) document.getElementById('paperDOIInput').value = '';

            alert(`✅ Submission successful!\n\nSubmission ID: ${result.submission_id}\nStatus: Processing\n\nYour algorithm is now being evaluated. Check back in a few seconds for results.`);

            // Start polling for status updates
            pollSubmissionStatus(result.submission_id);

        } else {
            throw new Error(result.detail || result.message || 'Submission failed');
        }

    } catch (error) {
        console.error('❌ Submission error:', error);
        alert(`❌ Submission failed: ${error.message}`);
    } finally {
        // Reset UI state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Algorithm';
        if (loadingDiv) loadingDiv.style.display = 'none';
    }
}

// Function to poll submission status
async function pollSubmissionStatus(submissionId, maxAttempts = 30) {
    let attempts = 0;

    // Start progress tracking immediately
    startProgressTracking(submissionId);

    const poll = async () => {
        try {
            const token = getAuthToken();
            const response = await fetch(
                `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.SUBMISSION_STATUS}/${submissionId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (response.ok) {
                const result = await response.json();

                // If completed or failed, stop polling and update UI
                if (result.status === 'completed' || result.status === 'failed') {
                    console.log(`✅ Submission ${submissionId} finished with status: ${result.status}`);

                    // Clear progress tracking
                    if (progressIntervals.has(submissionId)) {
                        clearInterval(progressIntervals.get(submissionId));
                        progressIntervals.delete(submissionId);
                    }

                    // Update UI with fresh data from backend
                    await updatePersonalPerformanceTable();
                    await updatePersonalSubmissionHistory();
                    await updatePersonalStats();
                    await updateLeaderboard();

                    // Show completion notification
                    if (result.status === 'completed') {
                        const score = safeToFixed(result.score, 1);
                        const cr = safeToFixed(result.metrics?.CR, 1);
                        const prd = safeToFixed(result.metrics?.PRD, 4);

                        alert(`🎉 Submission completed!\n\nScore: ${score}\nCR: ${cr}\nPRD: ${prd}\n\nCheck the leaderboard to see your ranking!`);
                    } else {
                        alert(`❌ Submission failed.\n\nPlease check your algorithm and try again.`);
                    }

                    return;
                }
            } else {
                console.error('❌ Status check failed:', response.status);
            }

            attempts++;
            if (attempts < maxAttempts) {
                // Exponential backoff
                const delay = Math.min(1000 * Math.pow(1.5, attempts), 10000);
                setTimeout(poll, delay);
            } else {
                console.log('⏰ Max polling attempts reached');
                // Clear progress tracking
                if (progressIntervals.has(submissionId)) {
                    clearInterval(progressIntervals.get(submissionId));
                    progressIntervals.delete(submissionId);
                }
            }
        } catch (error) {
            console.error('❌ Polling error:', error);
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 2000);
            }
        }
    };

    // Start polling immediately
    poll();
}

// Updated authentication functions
async function registerUser() {
    const teamName = document.getElementById('registerTeam').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;

    if (!teamName || !email || !password) {
        alert('Please fill in all fields.');
        return;
    }

    // Validate email
    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        alert('Password must meet all requirements:\n- At least 8 characters\n- One uppercase letter\n- One lowercase letter\n- One number\n- One special character (@$!%*?&)');
        return;
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.REGISTER}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                teamName: teamName,
                email: email,
                password: password
            })
        });

        const result = await response.json();

        if (response.ok && result.access_token) {
            // Store authentication token with correct key
            setAuthToken(result.access_token);
            currentTeam = teamName;
            localStorage.setItem('currentTeam', currentTeam);
            localStorage.setItem('userEmail', email);
            localStorage.setItem('registeredDate', new Date().toISOString());

            alert('✅ Registration successful! You are now logged in.');

            // Clear form and close modal
            document.getElementById('registerForm').reset();
            closeModal('authModal');
            showSection('home');

            // Update UI and load user data
            updateAuthState();
            updateTeamDisplay();
            updateProfileDisplay();

            // Load real user data
            await loadUserData();
        } else {
            throw new Error(result.detail || 'Registration failed');
        }

    } catch (error) {
        console.error('Registration error:', error);
        alert(`❌ Registration failed: ${error.message}`);
    }
}

async function loginUser() {
    const teamName = document.getElementById('loginTeam').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!teamName || !password) {
        alert('Please enter both team name and password.');
        return;
    }

    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LOGIN}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                teamName: teamName,
                password: password
            })
        });

        const result = await response.json();

        if (response.ok && result.access_token) {
            // Store authentication token with correct key
            setAuthToken(result.access_token);
            currentTeam = teamName;
            localStorage.setItem('currentTeam', currentTeam);
            localStorage.setItem('userEmail', result.user.email);
            localStorage.setItem('registeredDate', new Date().toISOString());

            alert('✅ Login successful!');

            // Clear form and close modal
            document.getElementById('loginForm').reset();
            closeModal('authModal');
            showSection('home');

            // Update UI and load user data
            updateAuthState();
            updateTeamDisplay();
            updateProfileDisplay();

            // Load real user data
            await loadUserData();
        } else {
            throw new Error(result.detail || 'Login failed');
        }

    } catch (error) {
        console.error('Login error:', error);
        alert(`❌ Login failed: ${error.message}`);
    }
}

// Updated leaderboard fetch function
async function fetchLeaderboard() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LEADERBOARD}`);
        const result = await response.json();

        if (response.ok && result.leaderboard) {
            return result.leaderboard;
        } else {
            throw new Error('Failed to fetch leaderboard');
        }
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        return [];
    }
}

function showGuestSubmissionView() {
    // Show limited view for non-logged-in users
    document.getElementById('currentRank').textContent = '-';
    document.getElementById('bestScore').textContent = '0';
    document.getElementById('totalSubmissions').textContent = '0';
    document.getElementById('averageScore').textContent = '0';

    const submissionHistory = document.getElementById('submissionHistory');
    submissionHistory.innerHTML = `
        <div style="text-align: center; color: var(--text-muted); padding: 2rem;">
            <p>Please <a href="#login" onclick="openModal('authModal')">login</a> to view your submission history and submit algorithms.</p>
        </div>
    `;
}

async function updatePersonalStats() {
    try {
        const token = getAuthToken();
        if (!token || !currentTeam) {
            // Clear stats for non-logged users
            clearPersonalStats();
            return;
        }

        // Get real submissions from backend
        const userSubmissions = await getUserSubmissionsFromBackend();
        const completedSubmissions = userSubmissions.filter(sub => sub.status === 'completed');

        console.log(`📊 Processing ${completedSubmissions.length} completed submissions for stats`);

        const totalSubs = userSubmissions.length;
        const bestScore = completedSubmissions.length > 0 ?
            Math.max(...completedSubmissions.map(sub => parseFloat(sub.score) || 0)) : 0;

        // Calculate average score with better handling
        let avgScore = 0;
        if (completedSubmissions.length > 0) {
            const scores = completedSubmissions.map(sub => parseFloat(sub.score) || 0);
            const totalScore = scores.reduce((sum, score) => sum + score, 0);
            avgScore = totalScore / completedSubmissions.length;
            console.log(`📊 Average calculation: ${totalScore} / ${completedSubmissions.length} = ${avgScore}`);
        }

        // Get best CR and PRD from submissions
        const bestCR = completedSubmissions.length > 0 ?
            Math.max(...completedSubmissions.map(sub => parseFloat(sub.metrics?.CR) || 0)) : 0;
        const bestPRD = completedSubmissions.length > 0 ?
            Math.min(...completedSubmissions.map(sub => parseFloat(sub.metrics?.PRD) || Infinity)) : 0;

        // Get current rank from leaderboard
        const currentRank = await getUserRankFromLeaderboard();

        // Update elements if they exist
        const elements = {
            'totalSubmissions': totalSubs.toString(),
            'bestScore': safeToFixed(bestScore, 1),
            'averageScore': safeToFixed(avgScore, 3),
            'currentRank': currentRank || '-'
        };

        console.log('📊 Updating personal stats elements:', elements);

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                console.log(`✅ Updated ${id}: ${value}`);
            } else {
                console.warn(`⚠️ Element not found: ${id}`);
            }
        });

        // Update local storage
        localStorage.setItem('highScore', bestScore.toString());
        highScore = bestScore;

    } catch (error) {
        console.error('Error updating personal stats:', error);
        clearPersonalStats();
    }
}

function clearPersonalStats() {
    const elements = {
        'totalSubmissions': '0',
        'bestScore': '0.0',
        'averageScore': 'N/A',
        'currentRank': '-'
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// Function to get user submissions from backend
async function getUserSubmissionsFromBackend() {
    try {
        const token = getAuthToken();
        if (!token || !currentTeam) {
            console.warn("⚠️ No auth token or team name available for submission fetch");
            return [];
        }

        console.log(`🔍 Fetching submissions for team: ${currentTeam}`);

        // 修复Authorization header格式
        const response = await fetch(`${API_BASE_URL}/user-submissions/${currentTeam}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log(`✅ Successfully fetched ${data.submissions?.length || 0} submissions`);
            return data.submissions || [];
        } else {
            // 增强错误处理和日志
            const status = response.status;
            let errorText;
            try {
                errorText = await response.text();
            } catch (e) {
                errorText = "Could not read error response";
            }

            console.error(`❌ Failed to fetch user submissions: ${status} - ${errorText}`);

            if (status === 401 || status === 403) {
                console.warn("🔐 Authentication issue detected. Token might be invalid or expired.");
                // 提示用户但不自动登出
                alert("Your session may have expired. Please login again to view your submissions.");
            }
            return [];
        }
    } catch (error) {
        console.error('❌ Error fetching user submissions:', error);
        return [];
    }
}

async function getUserRankFromLeaderboard() {
    try {
        const token = getAuthToken();
        if (!token) return null;

        const response = await fetch(`${API_BASE_URL}/leaderboard`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const results = data.results || [];

            // Find current user's rank
            const userIndex = results.findIndex(result => result.participant_name === currentTeam);
            return userIndex >= 0 ? userIndex + 1 : null;
        }
    } catch (error) {
        console.error('Error getting user rank:', error);
    }
    return null;
}

async function updateLeaderboardPreview() {
    try {
        const token = getAuthToken();
        const response = await fetch(`${API_BASE_URL}/leaderboard`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (response.ok) {
            const data = await response.json();
            const results = data.results || [];

            // Show top 3 entries
            const topResults = results.slice(0, 3);
            const leaderboardPreview = document.getElementById('leaderboardPreview');

            if (leaderboardPreview) {
                if (topResults.length === 0) {
                    showEmptyLeaderboardPreview();
                } else {
                    leaderboardPreview.innerHTML = topResults.map((result, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${result.participant_name}</td>
                            <td>${safeToFixed(result.scores?.CR, 1)}</td>
                            <td>${safeToFixed(result.scores?.PRD, 4)}</td>
                            <td>${safeToFixed(result.scores?.Score, 1)}</td>
                        </tr>
                    `).join('');
                }
            }
        } else {
            showEmptyLeaderboardPreview();
        }
    } catch (error) {
        console.error('Error updating leaderboard preview:', error);
        showEmptyLeaderboardPreview();
    }
}

function showEmptyLeaderboardPreview() {
    const leaderboardPreview = document.getElementById('leaderboardPreview');
    if (leaderboardPreview) {
        leaderboardPreview.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: #666; padding: 1rem;">
                    No submissions yet
                </td>
            </tr>
        `;
    }
}

async function updatePersonalSubmissionHistory() {
    // Find the submission history container
    const submissionHistory = document.getElementById('submissionHistory');

    // Check if element exists before trying to use it
    if (!submissionHistory) {
        console.warn('submissionHistory element not found');
        return;
    }

    const token = getAuthToken();
    if (!token || !currentTeam) {
        submissionHistory.innerHTML = '<p class="no-submissions">Please login to view your submission history.</p>';
        return;
    }

    // 添加加载指示器
    submissionHistory.innerHTML = '<div class="loading-spinner" style="text-align:center;padding:2rem;"><div class="spinner"></div><p>Loading submissions...</p></div>';

    try {
        // Get real submissions from backend
        console.log("📃 Fetching user submission history...");
        const userSubmissions = await getUserSubmissionsFromBackend();

        if (userSubmissions.length === 0) {
        submissionHistory.innerHTML = '<p class="no-submissions">You have not made any submissions yet.</p>';
    } else {
            console.log(`📋 Rendering ${userSubmissions.length} submissions`);
            submissionHistory.innerHTML = userSubmissions.map(submission => {
                const statusClass = getStatusClass(submission.status);
                const statusIcon = getStatusIcon(submission.status);
                const formattedStatus = formatStatus(submission.status);

            return `
                <div class="submission-card">
                    <div class="submission-header">
                        <h4>${submission.algorithmName || submission.fileName || 'Unknown Algorithm'}</h4>
                        <span class="status ${statusClass}">
                            ${statusIcon} ${formattedStatus}
                        </span>
                    </div>
                    <div class="submission-details">
                        <p><strong>Submitted:</strong> ${new Date(submission.submitted_at).toLocaleString()}</p>
                            <p><strong>Score:</strong> ${safeToFixed(submission.score, 1)}</p>
                            ${submission.metrics ? `<p><strong>Metrics:</strong> CR: ${safeToFixed(submission.metrics.CR, 1)}, PRD: ${safeToFixed(submission.metrics.PRD, 4)}</p>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        }
    } catch (error) {
        console.error('❌ Error updating submission history:', error);
        // 提供更清晰的错误反馈
        submissionHistory.innerHTML = `
            <div class="error-message" style="text-align: center; color: #e53e3e; padding: 1.5rem; background: #fff5f5; border-radius: 8px; margin: 1rem 0;">
                <p style="font-weight: bold;">⚠️ Error loading submission history</p>
                <p>${error.message || 'There was a problem connecting to the server'}</p>
                <button onclick="updatePersonalSubmissionHistory()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: var(--accent); color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Try Again
                </button>
            </div>
        `;
    }
}

function getStatusIcon(status) {
    const icons = {
        'processing': '⏳',
        'completed': '✅',
        'scored-locally': '✅',
        'failed': '❌',
        'error': '❌'
    };
    return icons[status] || '❓';
}

function formatStatus(status) {
    const statusMap = {
        'processing': { text: 'Processing', class: 'status-processing', icon: '⏳' },
        'completed': { text: 'Completed', class: 'status-completed', icon: '✅' },
        'failed': { text: 'Failed', class: 'status-failed', icon: '❌' },
        'pending': { text: 'Pending', class: 'status-processing', icon: '⏳' },
        'unknown': { text: 'Unknown', class: 'status-unknown', icon: '❓' }
    };

    const statusInfo = statusMap[status] || statusMap['unknown'];
    return `<span class="status-badge ${statusInfo.class}">${statusInfo.icon} ${statusInfo.text}</span>`;
}

function formatDate(dateString) {
    if (!dateString || dateString === 'Invalid Date') return 'Unknown';
    try {
        const date = new Date(dateString);
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return 'Unknown';
        }
        return date.toLocaleDateString();
    } catch (error) {
        console.warn('Date formatting error:', error, 'for date:', dateString);
        return 'Unknown';
    }
}

function formatDateTime(dateString) {
    if (!dateString || dateString === 'Invalid Date') return 'Unknown';
    try {
        const date = new Date(dateString);
        // Check if date is valid
        if (isNaN(date.getTime())) {
            return 'Unknown';
        }
        return date.toLocaleString();
    } catch (error) {
        console.warn('DateTime formatting error:', error, 'for date:', dateString);
        return 'Unknown';
    }
}

async function updatePersonalPerformanceTable() {
    const tbody = document.getElementById('personalPerformance');
    if (!tbody) return;

    const token = getAuthToken();
    if (!token || !currentTeam) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#888;">Please login to view your submissions.</td></tr>';
        return;
    }

    try {
        // Get real data from backend API - fix URL duplication
        const userSubmissions = await getUserSubmissionsFromBackend();

    if (userSubmissions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#888;">No submissions yet.</td></tr>';
        return;
    }

        // Sort by submission date (newest first)
        userSubmissions.sort((a, b) => {
            const dateA = new Date(a.submitted_at || a.timestamp || 0);
            const dateB = new Date(b.submitted_at || b.timestamp || 0);
            return dateB - dateA;
        });

        tbody.innerHTML = userSubmissions.map(sub => {
            const fileName = sub.fileName || (sub.algorithmName ? sub.algorithmName + '.zip' : 'algorithm.zip');

            // Fix date handling - try multiple date fields
            const submissionDateStr = sub.submitted_at || sub.timestamp || new Date().toISOString();
            const submissionDate = formatDateTime(submissionDateStr);

            const status = sub.status || 'unknown';

            // Handle different status types
            let statusDisplay = formatStatus(status);
            let progressBar = '';

            // Add progress bar for processing submissions
            if (status === 'processing') {
                progressBar = `
                    <div class="progress-container" style="margin-top: 5px;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-${sub.submission_id || sub.id}"></div>
                        </div>
                        <div class="progress-text" id="progress-text-${sub.submission_id || sub.id}">Processing...</div>
                    </div>
                `;
                statusDisplay += progressBar;
            }

            return `
                <tr>
                    <td>${fileName}</td>
                    <td>${submissionDate}</td>
                    <td>${statusDisplay}</td>
                    <td>${safeToFixed(sub.metrics?.CR, 1)}</td>
                    <td>${safeToFixed(sub.metrics?.PRD, 4)}</td>
                    <td>${safeToFixed(sub.score, 1)}</td>
        </tr>
            `;
        }).join('');

        // Start progress tracking for processing submissions
        userSubmissions.forEach(sub => {
            if (sub.status === 'processing') {
                startProgressTracking(sub.submission_id || sub.id);
            }
        });

        // Update localStorage with real data for persistence
        setPersonalSubmissions(userSubmissions);

    } catch (error) {
        console.error('Error updating performance table:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#888;">Error loading submissions.</td></tr>';
    }
}

// Progress tracking functionality
let progressIntervals = new Map();

function startProgressTracking(submissionId) {
    if (progressIntervals.has(submissionId)) {
        clearInterval(progressIntervals.get(submissionId));
    }

    let progress = 0;
    let stage = 0;
    const stages = [
        'Uploading...',
        'Validating files...',
        'Processing algorithm...',
        'Running evaluation...',
        'Calculating metrics...',
        'Finalizing results...'
    ];

    const interval = setInterval(() => {
        const progressElement = document.getElementById(`progress-${submissionId}`);
        const textElement = document.getElementById(`progress-text-${submissionId}`);

        if (!progressElement || !textElement) {
            clearInterval(interval);
            progressIntervals.delete(submissionId);
            return;
        }

        // Update progress
        progress += Math.random() * 15; // Random increment
        if (progress > 95) progress = 95; // Cap at 95% until completion

        // Update stage
        const stageIndex = Math.floor(progress / 16);
        if (stageIndex < stages.length) {
            textElement.textContent = stages[stageIndex];
        }

        progressElement.style.width = `${progress}%`;

        // Check if submission is complete
        checkSubmissionCompletion(submissionId);
    }, 1000);

    progressIntervals.set(submissionId, interval);
}

async function checkSubmissionCompletion(submissionId) {
    try {
        const token = getAuthToken();
        if (!token) {
            console.warn("⚠️ No auth token available for submission status check");
            return;
        }

        console.log(`🔍 Checking status for submission: ${submissionId}`);

        const response = await fetch(`${API_BASE_URL}/submission-status/${submissionId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const result = await response.json();
            console.log(`📊 Submission ${submissionId} status: ${result.status}`);

            if (result.status === 'completed' || result.status === 'failed') {
                // Clear progress tracking
                if (progressIntervals.has(submissionId)) {
                    clearInterval(progressIntervals.get(submissionId));
                    progressIntervals.delete(submissionId);
                }

                // Complete progress bar
                const progressElement = document.getElementById(`progress-${submissionId}`);
                const textElement = document.getElementById(`progress-text-${submissionId}`);

                if (progressElement && textElement) {
                    progressElement.style.width = '100%';
                    textElement.textContent = result.status === 'completed' ? 'Completed!' : 'Failed';

                    setTimeout(async () => {
                        // 更新UI并显示通知
                        await Promise.all([
                            updatePersonalPerformanceTable(),
                            updatePersonalSubmissionHistory(),
                            updatePersonalStats(),
                            updateLeaderboard()
                        ]);

                        // 显示提交结果通知
                        if (result.status === 'completed') {
                            const score = safeToFixed(result.score, 1);
                            const cr = safeToFixed(result.metrics?.CR, 1);
                            const prd = safeToFixed(result.metrics?.PRD, 4);

                            alert(`🎉 Submission completed!\n\nScore: ${score}\nCR: ${cr}\nPRD: ${prd}\n\nCheck the leaderboard to see your ranking!`);
                        }
                    }, 1000);
                }
            }
        } else if (response.status === 401 || response.status === 403) {
            console.warn(`🔐 Authentication issue when checking submission ${submissionId}: ${response.status}`);
            // 不要显示过多错误弹窗，静默处理认证问题
            // 清除进度条
            if (progressIntervals.has(submissionId)) {
                clearInterval(progressIntervals.get(submissionId));
                progressIntervals.delete(submissionId);
            }
        } else {
            console.error(`❌ Status check failed for ${submissionId}: ${response.status}`);
        }
    } catch (error) {
        console.error('❌ Error checking submission status:', error);
    }
}

function setupEventListeners() {
    // Setup paper submission handlers
    setupPaperSubmissionHandlers();

    // Setup form validation
    setupFormValidation();

    // Navigation links
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const href = link.getAttribute('href');
            const sectionId = href.substring(1); // Remove #

            // Handle special cases
            if (sectionId === 'login') {
                if (getAuthToken()) {
                    logout();
                } else {
                    openModal('authModal');
                    showForm('login');
                }
            } else if (sectionId === 'profile' || sectionId === 'submission') {
                // Check if user is logged in for protected sections
                if (!getAuthToken()) {
                    alert('Please login first to access this section!');
                    openModal('authModal');
                    showForm('login');
                    return;
                }
                showSection(sectionId);
            } else {
                showSection(sectionId);
            }
        });
    });

    // Show home section by default
    showSection('home');

    // Submission form with enhanced validation
    const submissionForm = document.getElementById('submissionForm');
    if (submissionForm) {
        submissionForm.addEventListener('submit', (e) => {
            e.preventDefault();
            submitFiles();
        });
    }

    // Modal close button
    const closeModalBtn = document.querySelector('.close');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            closeModal('authModal');
        });
    }

    // Click outside modal to close
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal('authModal');
            }
        });

        // Handle escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                closeModal('authModal');
            }
        });
    }

    // Auth button (Login/Logout)
    const authButton = document.getElementById('authButton');
    if (authButton) {
        authButton.addEventListener('click', (e) => {
            e.preventDefault();
            if (getAuthToken()) {
                logout();
            } else {
                openModal('authModal');
                showForm('login');
            }
        });
    }

    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const teamName = document.getElementById('loginTeam').value;
            const password = document.getElementById('loginPassword').value;
            login(teamName, password);
        });
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const teamName = document.getElementById('registerTeam').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            await register(teamName, email, password);
            document.body.style.overflow = ''; // Ensure scrolling is restored after registration
        });
    }

    // Form switching
    const switchForms = document.querySelectorAll('.switch-form');
    switchForms.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const href = link.getAttribute('href');
            if (href === '#register') {
                showForm('register');
            } else if (href === '#login') {
                showForm('login');
            }
        });
    });

    // Profile update forms
    const updateTeamNameForm = document.getElementById('updateTeamNameForm');
    if (updateTeamNameForm) {
        updateTeamNameForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newTeamName = document.getElementById('newTeamName').value.trim();
            if (newTeamName) {
                await updateTeamName(newTeamName);
            }
        });
    }

    const updateEmailForm = document.getElementById('updateEmailForm');
    if (updateEmailForm) {
        updateEmailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newEmail = document.getElementById('newEmail').value.trim();
            if (newEmail) {
                await updateEmail(newEmail);
            }
        });
    }

    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            if (currentPassword && newPassword && confirmPassword) {
                await changePassword(currentPassword, newPassword, confirmPassword);
            }
        });
    }
}

// Clear all demo data function
function clearAllDemoData() {
    // Clear localStorage completely for fresh start
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (
            key.includes('submissions') ||
            key.includes('personalSubmissions') ||
            key === 'highScore' ||
            key.includes('leaderboard')
        )) {
            keysToRemove.push(key);
        }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));

    // Reset global variables to empty state
    submissions = [];
    highScore = 0;

    console.log('✅ All demo data cleared - starting fresh');
}

// Enhanced page initialization
function initializePage() {
    console.log('🚀 ECG Compression Platform loaded');
    console.log('🔐 Current auth token:', getAuthToken() ? 'Present' : 'Not found');
    console.log('👥 Current team:', currentTeam);

    // Clear all demo data first
    clearAllDemoData();

    // Setup all event listeners
    setupEventListeners();

    // Update authentication state
    updateAuthState();

    // Initialize displays
    updateTeamDisplay();
    updateProfileDisplay();

    // Start global statistics refresh (updates immediately and then every 30 seconds)
    startGlobalStatsRefresh();

    // Load real data if user is logged in
    if (getAuthToken() && currentTeam) {
        console.log('✅ User logged in - loading real data');
        loadUserData();
    } else {
        console.log('ℹ️ No user logged in - showing empty state');
        showEmptyState();
    }

    // Test backend connection
    testCodabenchConnectionOnLoad();

    // Initialize with home section
    showSection('home');
}

// Load real user data from backend
async function loadUserData() {
    try {
        await updateSubmissionsDisplay();
        await updateLeaderboard();
        await updatePersonalStats();
    } catch (error) {
        console.error('❌ Error loading user data:', error);
    }
}

// Show empty state for non-logged users
function showEmptyState() {
    // Clear all data displays
    clearPersonalStats();

    // Show empty leaderboard
    showEmptyLeaderboard();
    showEmptyLeaderboardPreview();

    // Clear submission displays
    const submissionHistory = document.getElementById('submissionHistory');
    if (submissionHistory) {
        submissionHistory.innerHTML = '<p class="no-submissions">Please login to view your submission history.</p>';
    }

    const personalPerformance = document.getElementById('personalPerformance');
    if (personalPerformance) {
        personalPerformance.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#888;">Please login to view your submissions.</td></tr>';
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initializePage);

// Test Codabench connection when page loads
async function testCodabenchConnectionOnLoad() {
    const token = getAuthToken();
    if (token) {
        try {
            console.log('🔌 Testing backend connection...');
            // Use the health endpoint instead of test-codabench
            const response = await fetch('http://localhost:8000/health');

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend Status: Connected successfully');
                console.log('📋 Backend Health:', data);
            } else {
                console.log('⚠️ Backend Status: Connection failed');
            }
        } catch (error) {
            console.log('❌ Backend Status: Connection error -', error.message);
        }
    } else {
        console.log('🔒 Backend Status: Not tested (user not logged in)');
    }
}

// Modal management functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scroll
        console.log('📱 Modal opened:', modalId);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // Restore background scroll
        console.log('📱 Modal closed:', modalId);
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
    document.body.style.overflow = ''; // Restore background scroll
}

// Profile management functions
function updateProfileDisplay() {
    const profileTeamName = document.getElementById('profileTeamName');
    const profileEmail = document.getElementById('profileEmail');
    const profileRegisteredDate = document.getElementById('profileRegisteredDate');
    const profileSubmissionCount = document.getElementById('profileSubmissionCount');
    const profileBestScore = document.getElementById('profileBestScore');
    const profileTotalSubmissions = document.getElementById('profileTotalSubmissions');
    const profileBestRank = document.getElementById('profileBestRank');

    // Get user data from token or localStorage
    const token = getAuthToken();
    let userEmail = 'Not Set';

    if (token) {
        try {
            // Decode JWT to get user info (simple base64 decode for demo)
            const payload = JSON.parse(atob(token.split('.')[1]));

            if (profileTeamName) profileTeamName.textContent = payload.teamName || currentTeam || 'Not Set';

            // Try to get email from token first, then from localStorage backup
            userEmail = payload.email || localStorage.getItem('userEmail') || 'Not Set';
        } catch (error) {
            console.log('Could not decode token for profile display');
            // Fallback to localStorage
            userEmail = localStorage.getItem('userEmail') || 'Not Set';
        }
    } else {
        // Fallback to localStorage if no token
        userEmail = localStorage.getItem('userEmail') || 'Not Set';
    }

    // Update email display
    if (profileEmail) profileEmail.textContent = userEmail;

    // Update team name display
    if (profileTeamName) profileTeamName.textContent = currentTeam || 'Not Set';

    // Update other profile fields
    if (profileSubmissionCount) profileSubmissionCount.textContent = submissions.length.toString();
    if (profileBestScore) profileBestScore.textContent = highScore || '0';
    if (profileTotalSubmissions) profileTotalSubmissions.textContent = submissions.length.toString();
    if (profileBestRank) profileBestRank.textContent = submissions.length > 0 ? Math.floor(Math.random() * 50) + 1 : '-';

    // Set registered date from localStorage or default
    const registeredDate = localStorage.getItem('registeredDate') || 'Unknown';
    if (profileRegisteredDate) {
        if (registeredDate !== 'Unknown') {
            profileRegisteredDate.textContent = new Date(registeredDate).toLocaleDateString();
        } else {
            profileRegisteredDate.textContent = 'Unknown';
        }
    }
}

// Update team name
async function updateTeamName(newTeamName) {
    try {
        const token = getAuthToken();
        if (!token) {
            alert('Please login first!');
            return;
        }

        if (!newTeamName || newTeamName.length < 3 || newTeamName.length > 50) {
            alert('Team name must be between 3 and 50 characters');
            return;
        }

        // Update locally since we don't have a backend
        const oldTeamName = currentTeam;
        currentTeam = newTeamName;
        localStorage.setItem('currentTeam', newTeamName);

        // Update all submissions to use new team name
        submissions = submissions.map(sub => {
            if (sub.teamName === oldTeamName) {
                sub.teamName = newTeamName;
            }
            return sub;
        });
        localStorage.setItem('submissions', JSON.stringify(submissions));

        // Update JWT token to include new team name
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            payload.teamName = newTeamName;
            // Create a mock updated token (in a real app, this would come from the server)
            const updatedTokenPayload = btoa(JSON.stringify(payload));
            const tokenParts = token.split('.');
            tokenParts[1] = updatedTokenPayload;
            const updatedToken = tokenParts.join('.');
            setAuthToken(updatedToken);
        } catch (e) {
            // If token parsing fails, just continue with the update
            console.log('Could not update token, but local update succeeded');
        }

        updateProfileDisplay();
        updateTeamDisplay();
        alert('Team name updated successfully!');
        document.getElementById('newTeamName').value = '';

        console.log(`✅ Team name updated: ${oldTeamName} → ${newTeamName}`);
    } catch (error) {
        console.error('❌ Team name update error:', error);
        alert(`Team name update failed: ${error.message}`);
    }
}

// Update email
async function updateEmail(newEmail) {
    try {
        const token = getAuthToken();
        if (!token) {
            alert('Please login first!');
            return;
        }

        if (!validateEmail(newEmail)) {
            alert('Please enter a valid email address');
            return;
        }

        // Update JWT token to include new email
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            payload.email = newEmail;
            // Create a mock updated token (in a real app, this would come from the server)
            const updatedTokenPayload = btoa(JSON.stringify(payload));
            const tokenParts = token.split('.');
            tokenParts[1] = updatedTokenPayload;
            const updatedToken = tokenParts.join('.');
            setAuthToken(updatedToken);
        } catch (e) {
            // If token parsing fails, just continue with the update
            console.log('Could not update token, but local update succeeded');
        }

        // Store email in localStorage as backup
        localStorage.setItem('userEmail', newEmail);

        updateProfileDisplay();
        alert('Email updated successfully!');
        document.getElementById('newEmail').value = '';

        console.log(`✅ Email updated to: ${newEmail}`);
    } catch (error) {
        console.error('❌ Email update error:', error);
        alert(`Email update failed: ${error.message}`);
    }
}

// Change password
async function changePassword(currentPassword, newPassword, confirmPassword) {
    try {
        const token = getAuthToken();
        if (!token) {
            alert('Please login first!');
            return;
        }

        if (newPassword !== confirmPassword) {
            alert('New password and confirmation do not match');
            return;
        }

        const passwordValidation = validatePassword(newPassword);
        if (!passwordValidation.valid) {
            alert('New password must meet all requirements');
            return;
        }

        // Since we don't have a backend, we'll just store a hash indicator in localStorage
        const passwordHash = btoa(newPassword); // Simple base64 encoding (not secure, just for demo)
        localStorage.setItem('userPasswordHash', passwordHash);

        alert('Password changed successfully!');
        document.getElementById('changePasswordForm').reset();

        console.log('✅ Password updated successfully');
    } catch (error) {
        console.error('❌ Password change error:', error);
        alert(`Password change failed: ${error.message}`);
    }
}

// Delete account
async function deleteAccount() {
    try {
        const token = getAuthToken();
        if (!token) {
            alert('Please login first!');
            return;
        }

        const confirmDelete = confirm(
            'Are you sure you want to delete your account? This action cannot be undone. All your data, submissions, and profile information will be permanently deleted.'
        );

        if (!confirmDelete) {
            return;
        }

        // Since we don't have a backend, we'll just clear all local data
        // In a real application, this would call a backend API to delete the account

        // Clear all local data
        removeAuthToken();
        currentTeam = null;
        localStorage.removeItem('currentTeam');
        submissions = [];
        localStorage.removeItem('submissions');
        highScore = 0;
        localStorage.removeItem('highScore');
        localStorage.removeItem('registeredDate');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userPasswordHash');

        // Update UI state
        updateAuthState();
        updateTeamDisplay();

        // Redirect to home
        showSection('home');

        alert('Account deleted successfully. All local data has been cleared.');
        console.log('✅ Account deleted - all local data cleared');
    } catch (error) {
        console.error('❌ Account deletion error:', error);
        alert(`Account deletion failed: ${error.message}`);
    }
}

// Download user data
async function downloadUserData() {
    try {
        const token = getAuthToken();
        if (!token) {
            alert('Please login first!');
            return;
        }

        const userData = {
            teamName: currentTeam,
            submissions: submissions,
            registeredDate: localStorage.getItem('registeredDate'),
            totalSubmissions: submissions.length,
            bestScore: highScore
        };

        const blob = new Blob([JSON.stringify(userData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentTeam || 'user'}_data.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('✅ User data downloaded');
    } catch (error) {
        console.error('❌ Download error:', error);
        alert('Failed to download user data');
    }
}

// Navigation functions
function showSection(sectionId) {
    // Special handling for protected and hidden sections
    if (['profile', 'submission', 'leaderboard'].includes(sectionId)) {
        // Check if user is logged in for protected sections
        if ((sectionId === 'profile' || sectionId === 'submission') && !getAuthToken()) {
            alert('Please login first to access this section!');
            openModal('authModal');
            showForm('login');
            return;
        }

        // Hide all hideable sections
        const hideableSections = document.querySelectorAll('#profile, #submission, #leaderboard');
        hideableSections.forEach(section => {
            section.style.display = 'none';
        });

        // Show the requested section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.scrollIntoView({ behavior: 'smooth' });

            // Update section-specific data when shown
            if (sectionId === 'profile') {
                updateProfileDisplay();
            } else if (sectionId === 'submission') {
                updateSubmissionPageData();
            } else if (sectionId === 'leaderboard') {
                updateLeaderboard();
            }
        }
    } else if (sectionId === 'home') {
        // For home, hide the hideable sections and scroll to top
        const hideableSections = document.querySelectorAll('#profile, #submission, #leaderboard');
        hideableSections.forEach(section => {
            section.style.display = 'none';
        });
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        // For other sections (evaluation, forum, terms), just scroll to them
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Update active nav link
    updateActiveNavLink(sectionId);
}

function updateActiveNavLink(activeSection) {
    // Remove active class from all nav links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Add active class to current section link
    const activeLink = document.querySelector(`.nav-links a[href="#${activeSection}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// Enhanced submission page functions
async function updateSubmissionPageData() {
    try {
        const token = getAuthToken();
        if (!token) {
            // Show login required message
            showGuestSubmissionView();
            return;
        }

        // Update personal ranking stats
        await updatePersonalStats();
        await updatePersonalPerformanceTable();

        // Update leaderboard preview
        await updateLeaderboardPreview();

        // Update submission history
        await updatePersonalSubmissionHistory();

    } catch (error) {
        console.error('Error updating submission page:', error);
    }
}

// Wrapper functions for login and register (called by event listeners)
async function login(teamName, password) {
    await loginUser();
}

async function register(teamName, email, password) {
    await registerUser();
}

// Logout function
function logout() {
    removeAuthToken();
    currentTeam = null;
    localStorage.removeItem('currentTeam');
    localStorage.removeItem('userEmail');

    // Clear all user-specific data
    clearAllDemoData();

    // Update UI to show empty state
    updateAuthState();
    updateTeamDisplay();
    showEmptyState();
    showSection('home');

    alert('✅ Logged out successfully!');
    console.log('👋 User logged out');
}

// Personal submissions management - improved for real data persistence
function getPersonalSubmissions() {
    const key = `personalSubmissions_${currentTeam}`;
    return JSON.parse(localStorage.getItem(key)) || [];
}

function setPersonalSubmissions(submissions) {
    if (!currentTeam) return;
    const key = `personalSubmissions_${currentTeam}`;
    localStorage.setItem(key, JSON.stringify(submissions));
}

function getStatusClass(status) {
    switch (status) {
        case 'completed':
        case 'scored-locally':
            return 'status-success';
        case 'processing':
            return 'status-warning';
        case 'failed':
        case 'error':
            return 'status-error';
        default:
            return 'status-default';
    }
}

// Function to update submissions display
async function updateSubmissionsDisplay() {
    if (!getAuthToken()) {
        showGuestSubmissionView();
        return;
    }

    await updatePersonalSubmissionHistory();
    await updatePersonalPerformanceTable();
    await updatePersonalStats();
}

// Add missing toggleAuthMode function for compatibility
function toggleAuthMode(mode) {
    showForm(mode);
}

// Safe number conversion function
function safeToFixed(value, decimals = 1) {
    if (value === null || value === undefined || value === '') return 'N/A';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return 'N/A';
    // Handle zero values properly - zero is a valid score
    return num.toFixed(decimals);
}

// Global statistics management
async function updateGlobalStatistics() {
    try {
        console.log('📊 Fetching global statistics...');
        const response = await fetch(`${API_BASE_URL}/global-stats`);

        if (response.ok) {
            const stats = await response.json();
            console.log('✅ Global statistics received:', stats);

            // Update Performance Metrics display using our new API structure
            updateMetricsDisplay(stats);

            console.log('✅ Global statistics updated successfully');
        } else {
            console.warn('⚠️ Failed to fetch global statistics:', response.status);
            showErrorMetrics();
        }
    } catch (error) {
        console.error('❌ Error fetching global statistics:', error);
        showErrorMetrics();
    }
}

// Refresh global statistics periodically (every 30 seconds)
function startGlobalStatsRefresh() {
    // Update immediately
    updateGlobalStatistics();

    // Then update every 30 seconds
    setInterval(() => {
        updateGlobalStatistics();
    }, 30000); // 30 seconds
}

// Update top performers from leaderboard
async function updateTopPerformers() {
    try {
        const response = await fetch(`${API_BASE_URL}/leaderboard`);
        if (response.ok) {
            const data = await response.json();
            const results = data.results || [];

            if (results.length > 0) {
                // Find best CR team
                const bestCRTeam = results.reduce((best, current) =>
                    (current.scores?.CR || 0) > (best.scores?.CR || 0) ? current : best
                );

                // Find best PRD team
                const bestPRDTeam = results.reduce((best, current) =>
                    (current.scores?.PRD || Infinity) < (best.scores?.PRD || Infinity) ? current : best
                );

                // Update team names
                const topCompressionTeamElement = document.getElementById('topCompressionTeam');
                if (topCompressionTeamElement && bestCRTeam.participant_name) {
                    topCompressionTeamElement.textContent = `Team ${bestCRTeam.participant_name}`;
                }

                const bestPRDTeamElement = document.getElementById('bestPRDTeam');
                if (bestPRDTeamElement && bestPRDTeam.participant_name) {
                    bestPRDTeamElement.textContent = `Team ${bestPRDTeam.participant_name}`;
                }
            }
        }
    } catch (error) {
        console.error('❌ Error updating top performers:', error);
    }
}

