import React, { useState, useEffect } from 'react';
import { Card, Table, Form, Button, Alert, Badge, Row, Col, Modal } from 'react-bootstrap';
import ApiService from '../services/api';

function SafetyReports({ role }) {
    const [safetyReports, setSafetyReports] = useState([]);
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showReportModal, setShowReportModal] = useState(false);
    const [selectedReport, setSelectedReport] = useState(null);
    const [stats, setStats] = useState({
        totalReports: 0,
        compliantReports: 0,
        warningReports: 0,
        violationReports: 0,
        incidentCount: 0
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                const data = await ApiService.getRoleData(role);
                setSafetyReports(data.safetyReports || []);
                setProjects(data.projects || []);

                // Calculate stats
                const reports = data.safetyReports || [];
                setStats({
                    totalReports: reports.length,
                    compliantReports: reports.filter(r => r.compliance_status === 'Compliant').length,
                    warningReports: reports.filter(r => r.compliance_status === 'Warning Issued').length,
                    violationReports: reports.filter(r => r.compliance_status === 'Violation').length,
                    incidentCount: reports.reduce((count, report) => count + (report.incident_count || 0), 0)
                });
            } catch (err) {
                console.error('Error fetching safety data:', err);
                setError('Failed to load safety reports');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [role]);

    const handleViewReport = (report) => {
        setSelectedReport(report);
        setShowReportModal(true);
    };

    const handleCloseModal = () => {
        setShowReportModal(false);
        setSelectedReport(null);
    };

    const handleSubmitNewReport = async (e) => {
        e.preventDefault();
        // Create new report logic would go here
        setShowReportModal(false);
    };

    // Get project name by ID
    const getProjectName = (projectId) => {
        const project = projects.find(p => p.id === projectId);
        return project ? project.name : 'Unknown Project';
    };

    // Calculate safety compliance rate
    const getComplianceRate = () => {
        if (stats.totalReports === 0) return 0;
        return Math.round((stats.compliantReports / stats.totalReports) * 100);
    };

    return (
        <div className="safety-reports">
            <h1 className="mb-4">Safety Management</h1>

            {loading ? (
                <div className="text-center p-5">Loading safety data...</div>
            ) : error ? (
                <Alert variant="danger">{error}</Alert>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col lg={3} md={6} className="mb-3 mb-lg-0">
                            <Card className="h-100 bg-light">
                                <Card.Body className="text-center">
                                    <h3>{getComplianceRate()}%</h3>
                                    <Card.Title>Compliance Rate</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6} className="mb-3 mb-lg-0">
                            <Card className="h-100 bg-light">
                                <Card.Body className="text-center">
                                    <h3>{stats.totalReports}</h3>
                                    <Card.Title>Total Reports</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6} className="mb-3 mb-md-0">
                            <Card className="h-100 bg-light">
                                <Card.Body className="text-center">
                                    <h3>{stats.incidentCount}</h3>
                                    <Card.Title>Total Incidents</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6}>
                            <Card className="h-100 bg-light">
                                <Card.Body className="text-center">
                                    <h3>
                                        {stats.warningReports + stats.violationReports}
                                    </h3>
                                    <Card.Title>Issues Found</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Card className="mb-4">
                        <Card.Header className="d-flex justify-content-between align-items-center">
                            <h5>Safety Compliance by Project</h5>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                {projects.map(project => {
                                    // Calculate project-specific stats
                                    const projectReports = safetyReports.filter(r => r.project_id === project.id);
                                    const total = projectReports.length;
                                    const compliant = projectReports.filter(r => r.compliance_status === 'Compliant').length;
                                    const rate = total > 0 ? Math.round((compliant / total) * 100) : 0;

                                    return (
                                        <Col lg={4} md={6} key={project.id} className="mb-3">
                                            <Card>
                                                <Card.Header>
                                                    <h6 className="mb-0">{project.name}</h6>
                                                </Card.Header>
                                                <Card.Body>
                                                    <div className="d-flex justify-content-between mb-2">
                                                        <span>Compliance Rate:</span>
                                                        <strong>{rate}%</strong>
                                                    </div>
                                                    <div className="progress mb-3">
                                                        <div
                                                            className={`progress-bar ${rate >= 80 ? 'bg-success' : rate >= 60 ? 'bg-warning' : 'bg-danger'}`}
                                                            role="progressbar"
                                                            style={{ width: `${rate}%` }}
                                                            aria-valuenow={rate}
                                                            aria-valuemin="0"
                                                            aria-valuemax="100"
                                                        ></div>
                                                    </div>
                                                    <div className="d-flex justify-content-between text-muted small">
                                                        <span>Reports: {total}</span>
                                                        <span>Incidents: {
                                                            projectReports.reduce((count, report) => count + (report.incident_count || 0), 0)
                                                        }</span>
                                                    </div>
                                                </Card.Body>
                                            </Card>
                                        </Col>
                                    );
                                })}
                            </Row>
                        </Card.Body>
                    </Card>

                    <Card>
                        <Card.Header className="d-flex justify-content-between align-items-center">
                            <h5>Safety Inspection Reports</h5>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    setSelectedReport(null);
                                    setShowReportModal(true);
                                }}
                            >
                                + New Report
                            </Button>
                        </Card.Header>
                        <Card.Body>
                            <Table hover responsive>
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Project</th>
                                        <th>Inspector</th>
                                        <th>Compliance Status</th>
                                        <th>Incidents</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {safetyReports.map(report => (
                                        <tr key={report.id}>
                                            <td>{report.report_date}</td>
                                            <td>{getProjectName(report.project_id)}</td>
                                            <td>{report.inspector_name}</td>
                                            <td>
                                                <Badge bg={
                                                    report.compliance_status === 'Compliant' ? 'success' :
                                                        report.compliance_status === 'Warning Issued' ? 'warning' : 'danger'
                                                }>
                                                    {report.compliance_status}
                                                </Badge>
                                            </td>
                                            <td>{report.incident_count || 0}</td>
                                            <td>
                                                <Button
                                                    variant="outline-primary"
                                                    size="sm"
                                                    onClick={() => handleViewReport(report)}
                                                >
                                                    View Details
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>

                            {safetyReports.length === 0 && (
                                <div className="text-center p-4">
                                    <p className="text-muted">No safety reports found.</p>
                                </div>
                            )}
                        </Card.Body>
                    </Card>

                    {/* Report Modal */}
                    <Modal show={showReportModal} onHide={handleCloseModal} size="lg">
                        <Modal.Header closeButton>
                            <Modal.Title>
                                {selectedReport ? 'Safety Report Details' : 'Create New Safety Report'}
                            </Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            {selectedReport ? (
                                <div>
                                    <Row className="mb-3">
                                        <Col md={6}>
                                            <p><strong>Date:</strong> {selectedReport.report_date}</p>
                                            <p><strong>Project:</strong> {getProjectName(selectedReport.project_id)}</p>
                                            <p><strong>Inspector:</strong> {selectedReport.inspector_name}</p>
                                        </Col>
                                        <Col md={6}>
                                            <p>
                                                <strong>Compliance Status:</strong>{' '}
                                                <Badge bg={
                                                    selectedReport.compliance_status === 'Compliant' ? 'success' :
                                                        selectedReport.compliance_status === 'Warning Issued' ? 'warning' : 'danger'
                                                }>
                                                    {selectedReport.compliance_status}
                                                </Badge>
                                            </p>
                                            <p><strong>Incidents:</strong> {selectedReport.incident_count || 0}</p>
                                        </Col>
                                    </Row>

                                    <Card>
                                        <Card.Header>Description</Card.Header>
                                        <Card.Body>
                                            <p>{selectedReport.description}</p>
                                        </Card.Body>
                                    </Card>
                                </div>
                            ) : (
                                <Form onSubmit={handleSubmitNewReport}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Project</Form.Label>
                                        <Form.Select required>
                                            <option value="">Select Project</option>
                                            {projects.map(project => (
                                                <option key={project.id} value={project.id}>
                                                    {project.name}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Inspection Date</Form.Label>
                                        <Form.Control
                                            type="date"
                                            required
                                            defaultValue={new Date().toISOString().split('T')[0]}
                                        />
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Compliance Status</Form.Label>
                                        <Form.Select required>
                                            <option value="Compliant">Compliant</option>
                                            <option value="Warning Issued">Warning Issued</option>
                                            <option value="Violation">Violation</option>
                                        </Form.Select>
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Number of Incidents</Form.Label>
                                        <Form.Control
                                            type="number"
                                            min="0"
                                            defaultValue="0"
                                        />
                                    </Form.Group>

                                    <Form.Group className="mb-3">
                                        <Form.Label>Description</Form.Label>
                                        <Form.Control
                                            as="textarea"
                                            rows={4}
                                            placeholder="Provide details about the inspection..."
                                        />
                                    </Form.Group>
                                </Form>
                            )}
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="secondary" onClick={handleCloseModal}>
                                {selectedReport ? 'Close' : 'Cancel'}
                            </Button>
                            {!selectedReport && (
                                <Button variant="primary" type="submit" onClick={handleSubmitNewReport}>
                                    Submit Report
                                </Button>
                            )}
                        </Modal.Footer>
                    </Modal>
                </>
            )}
        </div>
    );
}

export default SafetyReports; 