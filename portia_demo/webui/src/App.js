import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useParams } from 'react-router-dom';
import { Container, Nav, Navbar, Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import { UserProvider } from './contexts/UserContext';

// Pages
import Dashboard from './pages/Dashboard';
import ProjectTimeline from './pages/ProjectTimeline';
import MaterialsTracking from './pages/MaterialsTracking';
import SafetyReports from './pages/SafetyReports';
import TaskManager from './pages/TaskManager';
import AIAssistant from './pages/AIAssistant';
import EquipmentManager from './pages/EquipmentManager';
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
    navItems: ['dashboard', 'projects', 'finances', 'equipment', 'ai-assistant', 'ai-visualizer']
  },
  [ROLES.PROJECT_MANAGER]: {
    title: 'Project Manager Portal',
    navItems: ['dashboard', 'projects', 'tasks', 'materials', 'equipment', 'ai-assistant', 'ai-visualizer']
  },
  [ROLES.ENGINEER]: {
    title: 'Engineer Workspace',
    navItems: ['dashboard', 'projects', 'tasks', 'equipment', 'ai-assistant', 'ai-visualizer']
  },
  [ROLES.SAFETY_MANAGER]: {
    title: 'Safety Management',
    navItems: ['dashboard', 'safety', 'projects', 'equipment', 'ai-assistant', 'ai-visualizer']
  },
  [ROLES.FOREMAN]: {
    title: 'Foreman Portal',
    navItems: ['dashboard', 'tasks', 'materials', 'equipment', 'ai-assistant', 'ai-visualizer']
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
              {config.navItems.includes('finances') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/finances`}>Finances</Nav.Link>
              )}
              {config.navItems.includes('equipment') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/equipment`}>Equipment</Nav.Link>
              )}
              {config.navItems.includes('ai-assistant') && (
                <Nav.Link as={Link} to={`/${companyDomain}/${role}/ai-assistant`}>AI Assistant</Nav.Link>
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
          <Route path="finances" element={<Dashboard role={role} financeView={true} />} />
          <Route path="equipment" element={<EquipmentManager role={role} />} />
          <Route path="ai-assistant" element={<AIAssistant role={role} />} />
          <Route path="ai-visualizer" element={<AIVisualizer role={role} />} />
        </Routes>
      </Container>

      <div className="bottom-bar">
        <Container>
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Type your message or question here..."
              aria-label="Message input"
            />
            <Button variant="primary">Send</Button>
          </div>
        </Container>
      </div>
    </>
  );
}

export default App;
