import React, { useState, useCallback, useEffect, useRef } from 'react';
import './App.css';

// API base URL - update to use our new Flask server on port 5002
const API_BASE_URL = 'http://localhost:5002';

function App() {
  // State variables for the form
  const [companyType, setCompanyType] = useState('');
  const [userRole, setUserRole] = useState('Construction Worker');
  const [loading, setLoading] = useState(false);
  const [generatedData, setGeneratedData] = useState(null);
  const [generatedUI, setGeneratedUI] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking');

  // Check server status on component mount
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
          setServerStatus('connected');
        } else {
          setServerStatus('error');
        }
      } catch (err) {
        console.error('Server connection error:', err);
        setServerStatus('error');
      }
    };

    checkServerStatus();
  }, []);

  // Function to generate random company data
  const generateRandomData = async () => {
    setLoading(true);
    setError(null);
    setCurrentStage('Generating company data');
    setProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev < 90) return prev + 5;
          return prev;
        });
      }, 200);

      // Get company type directly from the ref for real-time value
      const currentCompanyType = document.getElementById('company-type-input')?.value || '';

      // Make API call to backend with company type parameter if provided
      const url = currentCompanyType
        ? `${API_BASE_URL}/construction-data?company_type=${encodeURIComponent(currentCompanyType)}`
        : `${API_BASE_URL}/construction-data`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to generate data: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.status === 'error') {
        throw new Error(result.message || 'Error generating data');
      }

      // Clear interval and set progress to 100
      clearInterval(progressInterval);
      setProgress(100);

      // Set the generated data
      setGeneratedData(result.data);

    } catch (err) {
      console.error('Error generating data:', err);
      setError(err.message || 'Failed to generate company data');
    } finally {
      setLoading(false);
    }
  };

  // Function to generate UI based on company data and user role
  const generateUI = async () => {
    // Get company type directly from the input element for real-time value
    const currentCompanyType = document.getElementById('company-type-input')?.value || '';

    if (!currentCompanyType) {
      setError('Please enter a company type');
      return;
    }

    if (!generatedData) {
      setError('Please generate company data first');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStage('Generating customized dashboard UI');
    setProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev < 90) return prev + 2;
          return prev;
        });
      }, 200);

      // Create a prompt based on user role and company type
      const roleBasedPrompt = generatePromptBasedOnRole(userRole, currentCompanyType);

      // Make API call to backend
      const response = await fetch(`${API_BASE_URL}/generate-construction-ui`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_data: generatedData.company_data,
          design_restrictions: generatedData.design_restrictions,
          // Add role-specific requirements to the request
          additional_requirements: roleBasedPrompt
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate UI: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.status === 'error') {
        throw new Error(result.message || 'Error generating UI');
      }

      // Clear interval and set progress to 100
      clearInterval(progressInterval);
      setProgress(100);

      // Set the generated UI
      setGeneratedUI({
        html: result.html,
        css: result.css
      });

    } catch (err) {
      console.error('Error generating UI:', err);
      setError(err.message || 'Failed to generate UI');
    } finally {
      setLoading(false);
    }
  };

  // Generate role-specific prompts for the UI
  const generatePromptBasedOnRole = (role, company) => {
    let prompt = `Generate a professional dashboard UI for a ${company} company targeting a ${role} user. `;

    switch (role) {
      case 'Investor':
        prompt += 'Focus on financial metrics, ROI, and growth projections. Use charts to display financial performance and include actual numbers and percentages. Make financial information the most prominent part of the dashboard.';
        break;
      case 'Construction Worker':
        prompt += 'Prioritize task lists, schedules, and materials information. Include a prominent Bill of Materials (BOM) section, equipment status, and safety protocols. Design should be practical with clear task-focused elements.';
        break;
      case 'Project Manager':
        prompt += 'Highlight project timelines, resource allocation, and task status. Include Gantt charts, progress indicators, and team performance metrics. Make the project overview the central element of the dashboard.';
        break;
      case 'CEO':
        prompt += 'Present a high-level overview of all company aspects. Include KPIs, department performance, financial summaries, and strategic objectives. Design should be executive-level with emphasis on decision-making data.';
        break;
      case 'Inventory Manager':
        prompt += 'Focus on inventory levels, stock alerts, supplier information, and procurement status. Include detailed tables of materials with stock levels and reorder points. Make inventory management tools the central element.';
        break;
      default:
        prompt += 'Create a general dashboard with company information and relevant metrics.';
    }

    return prompt;
  };

  // Render preview of generated UI
  const renderPreview = () => {
    if (!generatedUI) return null;

    // Create a composite HTML document with the generated HTML and CSS
    const fullHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <style>${generatedUI.css}</style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      </head>
      <body>
        ${generatedUI.html}
      </body>
      </html>
    `;

    return (
      <div className="preview-container">
        <div className="preview-header">
          <h2>Generated Dashboard for {companyType} - {userRole} View</h2>
          <button className="back-button" onClick={() => setShowPreview(false)}>
            Back to Generator
          </button>
        </div>
        <iframe
          title="Dashboard Preview"
          className="preview-frame"
          srcDoc={fullHtml}
          width="100%"
          height="700px"
          sandbox="allow-scripts"
        />
      </div>
    );
  };

  // Loading indicator component
  const LoadingIndicator = () => (
    <div className="loading-screen">
      <div className="loading-content">
        <h2>Building Your Dashboard</h2>
        <p>{currentStage}</p>
        <div className="progress-bar-container">
          <div
            className="progress-bar"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="progress-text">{Math.round(progress)}% complete</div>
      </div>
    </div>
  );

  // Server Error component
  const ServerError = () => (
    <div className="error-container">
      <h2>Server Connection Error</h2>
      <p>Unable to connect to the Flask server at {API_BASE_URL}.</p>
      <p>Please make sure the server is running using:</p>
      <pre>cd flask_server && source venv/bin/activate && python app.py</pre>
    </div>
  );

  // Main generator form
  const GeneratorForm = () => {
    const handleSubmit = (e) => {
      e.preventDefault();
      // Prevent form submission
    };

    // Reference for uncontrolled input
    const companyTypeRef = useRef(null);

    // Get company type value directly from DOM when needed
    const getCompanyType = () => {
      return companyTypeRef.current ? companyTypeRef.current.value : '';
    };

    // Update company type state when needed (like for form submission)
    const updateCompanyTypeState = () => {
      if (companyTypeRef.current) {
        setCompanyType(companyTypeRef.current.value);
      }
    };

    return (
      <form className="generator-container" onSubmit={handleSubmit}>
        <h1>Tailored Dashboard Generator</h1>
        <p>Create a customized dashboard UI based on company type and user role</p>

        <div className="form-group">
          <label htmlFor="company-type-input">Company Type</label>
          <input
            id="company-type-input"
            type="text"
            defaultValue={companyType}
            ref={companyTypeRef}
            placeholder="e.g. Construction, Technology, Healthcare"
            className="text-input"
            autoComplete="off"
          />
        </div>

        <div className="form-group">
          <button
            type="button"
            className="generate-data-button"
            onClick={() => {
              updateCompanyTypeState();
              generateRandomData();
            }}
            disabled={loading}
          >
            Generate Random Company Data
          </button>
          {generatedData && (
            <div className="success-badge">
              <i className="fa fa-check-circle"></i> Data Generated
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="user-role-select">User Role</label>
          <select
            id="user-role-select"
            value={userRole}
            onChange={(e) => setUserRole(e.target.value)}
            className="select-input"
          >
            <option value="Construction Worker">Construction Worker</option>
            <option value="Project Manager">Project Manager</option>
            <option value="Investor">Investor</option>
            <option value="CEO">CEO</option>
            <option value="Inventory Manager">Inventory Manager</option>
          </select>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          type="button"
          className="generate-ui-button"
          onClick={() => {
            updateCompanyTypeState();
            generateUI();
          }}
          disabled={loading || !generatedData}
        >
          Generate Dashboard UI
        </button>

        {generatedUI && !showPreview && (
          <div className="success-container">
            <p>Dashboard UI successfully generated!</p>
            <button
              type="button"
              className="preview-button"
              onClick={() => setShowPreview(true)}
            >
              Preview Dashboard
            </button>
          </div>
        )}
      </form>
    );
  };

  return (
    <div className="App">
      {serverStatus === 'error' ? (
        <ServerError />
      ) : loading ? (
        <LoadingIndicator />
      ) : showPreview && generatedUI ? (
        renderPreview()
      ) : (
        <GeneratorForm />
      )}
    </div>
  );
}

export default App;
