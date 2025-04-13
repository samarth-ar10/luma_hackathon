import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Form, Button, Alert, Badge, ProgressBar } from 'react-bootstrap';
import ApiService from '../services/api';

function ProjectTimeline({ role }) {
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [timelineView, setTimelineView] = useState('month'); // month, week, day

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                setLoading(true);
                setError(null);

                const data = await ApiService.getRoleData(role);
                setProjects(data.projects || []);

                if (data.projects && data.projects.length > 0) {
                    setSelectedProject(data.projects[0].id);
                }
            } catch (err) {
                console.error('Error fetching projects:', err);
                setError('Failed to load project data');
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, [role]);

    // Calculate timeline data for the selected project
    const getProjectTimeline = () => {
        if (!selectedProject) return [];

        const project = projects.find(p => p.id === selectedProject);
        if (!project) return [];

        // Get all tasks for the selected project
        const projectTasks = project.tasks || [];

        // Set up timeline - we'll create a simplified timeline representation
        const startDate = new Date(project.start_date);
        const endDate = new Date(project.end_date);

        // Calculate months between start and end date
        const months = [];
        const currentDate = new Date(startDate);
        while (currentDate <= endDate) {
            months.push(new Date(currentDate));
            currentDate.setMonth(currentDate.getMonth() + 1);
        }

        return { project, months };
    };

    const timelineData = getProjectTimeline();

    // Generate month labels for the timeline
    const getMonthLabel = (date) => {
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    };

    return (
        <div className="project-timeline">
            <h1 className="mb-4">Project Timeline</h1>

            {loading ? (
                <div className="text-center p-5">Loading project data...</div>
            ) : error ? (
                <Alert variant="danger">{error}</Alert>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col md={6}>
                            <Form.Group>
                                <Form.Label>Select Project</Form.Label>
                                <Form.Select
                                    value={selectedProject || ''}
                                    onChange={e => setSelectedProject(Number(e.target.value))}
                                >
                                    {projects.map(project => (
                                        <option key={project.id} value={project.id}>
                                            {project.name}
                                        </option>
                                    ))}
                                </Form.Select>
                            </Form.Group>
                        </Col>
                        <Col md={6}>
                            <Form.Group>
                                <Form.Label>Timeline View</Form.Label>
                                <div>
                                    <Button
                                        variant={timelineView === 'day' ? 'primary' : 'outline-primary'}
                                        className="me-2"
                                        onClick={() => setTimelineView('day')}
                                    >
                                        Day
                                    </Button>
                                    <Button
                                        variant={timelineView === 'week' ? 'primary' : 'outline-primary'}
                                        className="me-2"
                                        onClick={() => setTimelineView('week')}
                                    >
                                        Week
                                    </Button>
                                    <Button
                                        variant={timelineView === 'month' ? 'primary' : 'outline-primary'}
                                        onClick={() => setTimelineView('month')}
                                    >
                                        Month
                                    </Button>
                                </div>
                            </Form.Group>
                        </Col>
                    </Row>

                    {timelineData.project && (
                        <Card>
                            <Card.Header>
                                <div className="d-flex justify-content-between align-items-center">
                                    <h5>{timelineData.project.name} Timeline</h5>
                                    <Badge bg={
                                        timelineData.project.status === 'In Progress' ? 'primary' :
                                            timelineData.project.status === 'Planning' ? 'warning' :
                                                timelineData.project.status === 'Completed' ? 'success' : 'secondary'
                                    }>
                                        {timelineData.project.status}
                                    </Badge>
                                </div>
                            </Card.Header>
                            <Card.Body>
                                <div className="project-info mb-4">
                                    <Row>
                                        <Col md={4}>
                                            <p><strong>Start Date:</strong> {timelineData.project.start_date}</p>
                                        </Col>
                                        <Col md={4}>
                                            <p><strong>End Date:</strong> {timelineData.project.end_date}</p>
                                        </Col>
                                        <Col md={4}>
                                            <p><strong>Progress:</strong></p>
                                            <ProgressBar
                                                now={timelineData.project.completion_percentage || 0}
                                                label={`${timelineData.project.completion_percentage || 0}%`}
                                            />
                                        </Col>
                                    </Row>
                                </div>

                                <div className="gantt-chart">
                                    <div className="timeline-headers d-flex">
                                        <div className="task-label" style={{ width: '200px' }}>
                                            <strong>Task</strong>
                                        </div>
                                        <div className="timeline-cells d-flex flex-grow-1">
                                            {timelineData.months.map((month, index) => (
                                                <div
                                                    key={index}
                                                    className="timeline-cell text-center"
                                                    style={{ flex: 1 }}
                                                >
                                                    {getMonthLabel(month)}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Tasks would go here, with bars representing their duration */}
                                    <div className="timeline-tasks">
                                        <div className="timeline-task d-flex align-items-center">
                                            <div className="task-label" style={{ width: '200px' }}>
                                                Foundation
                                            </div>
                                            <div className="timeline-cells d-flex flex-grow-1 position-relative">
                                                <div
                                                    className="task-bar bg-primary"
                                                    style={{
                                                        position: 'absolute',
                                                        left: '0%',
                                                        width: '30%',
                                                        height: '20px',
                                                        borderRadius: '4px'
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                        <div className="timeline-task d-flex align-items-center mt-2">
                                            <div className="task-label" style={{ width: '200px' }}>
                                                Framework
                                            </div>
                                            <div className="timeline-cells d-flex flex-grow-1 position-relative">
                                                <div
                                                    className="task-bar bg-success"
                                                    style={{
                                                        position: 'absolute',
                                                        left: '20%',
                                                        width: '40%',
                                                        height: '20px',
                                                        borderRadius: '4px'
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                        <div className="timeline-task d-flex align-items-center mt-2">
                                            <div className="task-label" style={{ width: '200px' }}>
                                                Electrical
                                            </div>
                                            <div className="timeline-cells d-flex flex-grow-1 position-relative">
                                                <div
                                                    className="task-bar bg-warning"
                                                    style={{
                                                        position: 'absolute',
                                                        left: '50%',
                                                        width: '25%',
                                                        height: '20px',
                                                        borderRadius: '4px'
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-end mt-4">
                                    <Button variant="outline-primary" className="me-2">
                                        Export Timeline
                                    </Button>
                                    <Button variant="primary">
                                        Update Timeline
                                    </Button>
                                </div>
                            </Card.Body>
                        </Card>
                    )}

                    <Card className="mt-4">
                        <Card.Header>
                            <h5>Project Milestones</h5>
                        </Card.Header>
                        <Card.Body>
                            <Table hover responsive>
                                <thead>
                                    <tr>
                                        <th>Milestone</th>
                                        <th>Due Date</th>
                                        <th>Status</th>
                                        <th>Assigned To</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Project Kickoff</td>
                                        <td>Jan 15, 2024</td>
                                        <td>
                                            <Badge bg="success">Completed</Badge>
                                        </td>
                                        <td>Sarah Johnson</td>
                                    </tr>
                                    <tr>
                                        <td>Foundation Completion</td>
                                        <td>Mar 30, 2024</td>
                                        <td>
                                            <Badge bg="success">Completed</Badge>
                                        </td>
                                        <td>Mike Chen</td>
                                    </tr>
                                    <tr>
                                        <td>Framework Installation</td>
                                        <td>Jun 15, 2024</td>
                                        <td>
                                            <Badge bg="primary">In Progress</Badge>
                                        </td>
                                        <td>David Lee</td>
                                    </tr>
                                    <tr>
                                        <td>Electrical Systems</td>
                                        <td>Aug 30, 2024</td>
                                        <td>
                                            <Badge bg="secondary">Pending</Badge>
                                        </td>
                                        <td>Mike Chen</td>
                                    </tr>
                                </tbody>
                            </Table>
                        </Card.Body>
                    </Card>
                </>
            )}
        </div>
    );
}

export default ProjectTimeline; 