import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useParams } from 'react-router-dom';
import { Container, Nav, Navbar, Button, Spinner } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import { UserProvider, useUserContext, useWorkerAI } from './contexts/UserContext';

// Pages
import Dashboard from './pages/Dashboard';
import ProjectTimeline from './pages/ProjectTimeline';
import MaterialsTracking from './pages/MaterialsTracking';
import SafetyReports from './pages/SafetyReports';
import TaskManager from './pages/TaskManager';
import AIVisualizer from './pages/AIVisualizer';

// Role definitions
const ROLES = {
  CEO: 'ceo',
  PROJECT_MANAGER: 'project-manager',
  ENGINEER: 'engineer',
  SAFETY_MANAGER: 'safety-manager',
  FOREMAN: 'foreman'
};

// Role-specific app configuration
const ROLE_CONFIG = {
  [ROLES.CEO]: {
    title: 'CEO Dashboard',
    navItems: ['dashboard', 'projects', 'ai-visualizer']
  },
  [ROLES.PROJECT_MANAGER]: {
    title: 'Project Manager Portal',
    navItems: ['dashboard', 'projects', 'tasks', 'materials', 'ai-visualizer']
  },
  [ROLES.ENGINEER]: {
    title: 'Engineer Workspace',
    navItems: ['dashboard', 'projects', 'tasks', 'ai-visualizer']
  },
  [ROLES.SAFETY_MANAGER]: {
    title: 'Safety Management',
    navItems: ['dashboard', 'safety', 'projects', 'ai-visualizer']
  },
  [ROLES.FOREMAN]: {
    title: 'Foreman Portal',
    navItems: ['dashboard', 'tasks', 'materials', 'ai-visualizer']
  }
};

// Role-based route wrapper
function RoleRoute({ children }) {
  const { companyDomain, role } = useParams();

  // Verify role is valid
  if (!Object.values(ROLES).includes(role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function App() {
  const [companyDomain] = useState('constructco');

  return (
    <UserProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Landing/Login page */}
            <Route path="/" element={
              <LandingPage companyDomain={companyDomain} />
            } />

            {/* Role-based routes */}
            <Route path="/:companyDomain/:role/*" element={
              <RoleDashboard />
            } />
          </Routes>
        </div>
      </Router>
    </UserProvider>
  );
}

// Landing page with role selection
function LandingPage({ companyDomain }) {
  return (
    <div className="landing-page">
      <Container className="text-center py-5">
        <h1 className="display-4 mb-4">ConstructComm AI</h1>
        <h2 className="mb-5">Construction Company Internal Communication System</h2>

        <div className="role-selection">
          <h3 className="mb-4">Select Your Role</h3>
          <div className="d-flex flex-wrap justify-content-center gap-3">
            {Object.entries(ROLES).map(([roleName, roleValue]) => (
              <Link
                key={roleValue}
                to={`/${companyDomain}/${roleValue}`}
                className="text-decoration-none"
              >
                <Button variant="primary" size="lg" className="role-button">
                  {roleName.replace('_', ' ')}
                </Button>
              </Link>
            ))}
          </div>
        </div>
      </Container>
    </div>
  );
}

// Role-based dashboard with navigation
function RoleDashboard() {
  const { companyDomain, role } = useParams();
  const config = ROLE_CONFIG[role] || ROLE_CONFIG[ROLES.ENGINEER];
  const [message, setMessage] = useState('');
  const { user, updateUserRole } = useUserContext();
  const { aiResponse, loading, sendMessage, clearAiResponse } = useWorkerAI();

  // Update user role when route changes
  useEffect(() => {
    if (role) {
      updateUserRole(role);
    }
  }, [role, updateUserRole]);

  // Handle sending message to Worker AI
  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!message.trim()) return;

    // Send message and get response
    await sendMessage(role, message, { source: 'bottom_bar' });
    setMessage('');
  };

  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand as={Link} to={`/${companyDomain}/${role}`}>
            {config.title}
          </Navbar.Brand>
          <div className="role-display">
            Role: {role.replace('-', ' ').toUpperCase()}
          </div>
          <Navbar.Toggle aria-controls="main-navbar" />
          <Navbar.Collapse id="main-navbar">
            <Nav className="me-auto">
              {config.navItems.includes('dashboard') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}`}>Dashboard</Nav.Link>
              )}
              {config.navItems.includes('projects') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/projects`}>Projects</Nav.Link>
              )}
              {config.navItems.includes('tasks') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/tasks`}>Tasks</Nav.Link>
              )}
              {config.navItems.includes('materials') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/materials`}>Materials</Nav.Link>
              )}
              {config.navItems.includes('safety') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/safety`}>Safety Reports</Nav.Link>
              )}
              {config.navItems.includes('ai-visualizer') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/ai-visualizer`}>AI Visualizer</Nav.Link>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container>
        <Routes>
          <Route index element={<Dashboard role={role} />} />
          <Route path="projects" element={<ProjectTimeline role={role} />} />
          <Route path="tasks" element={<TaskManager role={role} />} />
          <Route path="materials" element={<MaterialsTracking role={role} />} />
          <Route path="safety" element={<SafetyReports role={role} />} />
          <Route path="ai-visualizer" element={<AIVisualizer role={role} />} />
        </Routes>
      </Container>

      {/* Integrated Worker AI Bottom Bar */}
      <div className="bottom-bar">
        <Container>
          {aiResponse && (
            <div className="ai-response mb-2">
              <div className="ai-message">
                <strong>{role.toUpperCase()} AI:</strong> {aiResponse}
                <button
                  className="btn-close float-end"
                  onClick={clearAiResponse}
                  aria-label="Close"
                ></button>
              </div>
            </div>
          )}
          <form onSubmit={handleSendMessage} className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder={`Ask the ${role.replace('-', ' ').toUpperCase()} AI anything...`}
              aria-label="Message input"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={loading}
            />
            <Button
              variant="primary"
              type="submit"
              disabled={loading || !message.trim()}
            >
              {loading ?
                <>
                  <Spinner animation="border" size="sm" className="me-1" role="status" aria-hidden="true" />
                  Processing...
                </> : 'Send'}
            </Button>
          </form>
        </Container>
      </div>

      {/* Styles for AI integration */}
      <style>{`
        .bottom-bar {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: #f8f9fa;
          padding: 1rem;
          box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
          z-index: 1000;
        }
        
        .ai-response {
          max-height: 200px;
          overflow-y: auto;
        }
        
        .ai-message {
          background-color: #e3f2fd;
          padding: 0.75rem;
          border-radius: 0.5rem;
          position: relative;
        }
        
        .btn-close {
          font-size: 0.75rem;
          padding: 0.25rem;
        }
        
        /* Add margin to main container to prevent content from being hidden behind bottom bar */
        .container {
          margin-bottom: 80px;
        }
      `}</style>
    </>
  );
}

export default App;
