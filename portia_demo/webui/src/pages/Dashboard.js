import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Alert, Button, Spinner, Table, Badge } from 'react-bootstrap';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useConstructionData, formatDate, formatCurrency, calculateProjectCompletion } from '../data/DataService';

// Tile component with drag-and-drop capability
function DraggableTile({ id, title, size = 'medium', children, onSizeChange }) {
    const [currentSize, setCurrentSize] = useState(size);

    const handleSizeChange = () => {
        const sizeMap = {
            'small': 'medium',
            'medium': 'large',
            'large': 'small'
        };
        const newSize = sizeMap[currentSize];
        setCurrentSize(newSize);
        if (onSizeChange) {
            onSizeChange(id, newSize);
        }
    };

    const sizeToColMap = {
        'small': 4,
        'medium': 6,
        'large': 12
    };

    return (
        <Col md={sizeToColMap[currentSize]} className="mb-4">
            <Card className="tile h-100">
                <Card.Header className="d-flex justify-content-between align-items-center">
                    <strong>{title}</strong>
                    <div>
                        <Button
                            variant="outline-secondary"
                            size="sm"
                            onClick={handleSizeChange}
                        >
                            {currentSize === 'small' ? '⬛' : currentSize === 'medium' ? '⬜' : '⬜⬜'}
                        </Button>
                    </div>
                </Card.Header>
                <Card.Body>{children}</Card.Body>
            </Card>
        </Col>
    );
}

function Dashboard({ role, financeView = false }) {
    const { projects, tasks, materials, safetyReports, users, loading, error } = useConstructionData();
    const [tiles, setTiles] = useState([]);

    useEffect(() => {
        // Set up role-specific tiles
        if (projects.length > 0) {
            setupTiles(role, financeView);
        }
    }, [role, financeView, projects]);

    const setupTiles = (role, financeView) => {
        let roleTiles = [];

        // Common tiles for all roles
        roleTiles.push({ id: 'projects', title: 'Project Overview', size: 'medium' });

        // Role-specific tiles
        switch (role) {
            case 'ceo':
                roleTiles.push({ id: 'finances', title: 'Financial Overview', size: 'medium' });
                roleTiles.push({ id: 'safety', title: 'Safety Statistics', size: 'small' });
                roleTiles.push({ id: 'tasks', title: 'Task Completion', size: 'small' });
                if (financeView) {
                    roleTiles = [
                        { id: 'finances', title: 'Financial Overview', size: 'large' },
                        { id: 'budgetBreakdown', title: 'Budget Breakdown', size: 'medium' },
                        { id: 'costForecast', title: 'Cost Forecast', size: 'medium' }
                    ];
                }
                break;

            case 'project-manager':
                roleTiles.push({ id: 'tasks', title: 'Tasks', size: 'large' });
                roleTiles.push({ id: 'materials', title: 'Materials Tracking', size: 'medium' });
                break;

            case 'engineer':
                roleTiles.push({ id: 'tasks', title: 'Engineering Tasks', size: 'large' });
                roleTiles.push({ id: 'materials', title: 'Materials Specifications', size: 'medium' });
                break;

            case 'safety-manager':
                roleTiles.push({ id: 'safety', title: 'Safety Reports', size: 'large' });
                roleTiles.push({ id: 'safetyTasks', title: 'Safety Tasks', size: 'medium' });
                break;

            case 'foreman':
                roleTiles.push({ id: 'tasks', title: 'Site Tasks', size: 'large' });
                roleTiles.push({ id: 'materials', title: 'Materials Status', size: 'medium' });
                roleTiles.push({ id: 'labor', title: 'Labor Allocation', size: 'medium' });
                break;

            default:
                roleTiles.push({ id: 'tasks', title: 'Tasks', size: 'medium' });
        }

        // Add mail tile for all roles
        roleTiles.push({ id: 'mail', title: 'Mail', size: 'small' });

        setTiles(roleTiles);
    };

    const handleTileSizeChange = (id, newSize) => {
        setTiles(prevTiles =>
            prevTiles.map(tile =>
                tile.id === id ? { ...tile, size: newSize } : tile
            )
        );
    };

    if (loading) {
        return (
            <div className="text-center p-5">
                <Spinner animation="border" variant="primary" />
                <p className="mt-3">Loading dashboard data...</p>
            </div>
        );
    }

    if (error) {
        return <Alert variant="danger">{error}</Alert>;
    }

    const pageTitle = financeView ? 'Financial Dashboard' :
        role === 'ceo' ? 'Executive Dashboard' :
            role === 'project-manager' ? 'Project Management Dashboard' :
                role === 'engineer' ? 'Engineering Dashboard' :
                    role === 'safety-manager' ? 'Safety Dashboard' :
                        role === 'foreman' ? 'Site Management Dashboard' :
                            'Dashboard';

    // Render content for different tile types
    const renderTileContent = (tileId) => {
        switch (tileId) {
            case 'projects':
                return (
                    <div>
                        <Table hover responsive>
                            <thead>
                                <tr>
                                    <th>Project Name</th>
                                    <th>Status</th>
                                    <th>Progress</th>
                                </tr>
                            </thead>
                            <tbody>
                                {projects.map(project => {
                                    const completionPercentage = calculateProjectCompletion(tasks, project.id);
                                    return (
                                        <tr key={project.id}>
                                            <td>{project.name}</td>
                                            <td>
                                                <Badge bg={
                                                    project.status === 'In Progress' ? 'primary' :
                                                        project.status === 'Planning' ? 'warning' :
                                                            project.status === 'Completed' ? 'success' : 'secondary'
                                                }>
                                                    {project.status}
                                                </Badge>
                                            </td>
                                            <td>
                                                <div className="progress">
                                                    <div
                                                        className="progress-bar"
                                                        role="progressbar"
                                                        style={{ width: `${completionPercentage}%` }}
                                                        aria-valuenow={completionPercentage}
                                                        aria-valuemin="0"
                                                        aria-valuemax="100"
                                                    >
                                                        {completionPercentage}%
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </Table>
                    </div>
                );

            case 'tasks':
                return (
                    <div>
                        <Table hover responsive>
                            <thead>
                                <tr>
                                    <th>Task</th>
                                    <th>Project</th>
                                    <th>Priority</th>
                                    <th>Status</th>
                                    <th>Due Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tasks.map(task => (
                                    <tr key={task.id}>
                                        <td>{task.name}</td>
                                        <td>{task.project_name}</td>
                                        <td>
                                            <Badge bg={
                                                task.priority === 'High' ? 'danger' :
                                                    task.priority === 'Medium' ? 'warning' : 'info'
                                            }>
                                                {task.priority}
                                            </Badge>
                                        </td>
                                        <td>
                                            <Badge bg={
                                                task.status === 'Completed' ? 'success' :
                                                    task.status === 'In Progress' ? 'primary' : 'secondary'
                                            }>
                                                {task.status}
                                            </Badge>
                                        </td>
                                        <td>{formatDate(task.due_date)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </div>
                );

            case 'materials':
                return (
                    <div>
                        <Table hover responsive>
                            <thead>
                                <tr>
                                    <th>Material</th>
                                    <th>Project</th>
                                    <th>Quantity</th>
                                    <th>Status</th>
                                    <th>Delivery</th>
                                </tr>
                            </thead>
                            <tbody>
                                {materials.map(material => (
                                    <tr key={material.id}>
                                        <td>{material.name}</td>
                                        <td>{material.project_name}</td>
                                        <td>{material.quantity} {material.unit}</td>
                                        <td>
                                            <Badge bg={
                                                material.status === 'Delivered' ? 'success' :
                                                    material.status === 'Ordered' ? 'warning' : 'danger'
                                            }>
                                                {material.status}
                                            </Badge>
                                        </td>
                                        <td>{formatDate(material.delivery_date)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </div>
                );

            case 'safety':
                return (
                    <div>
                        <Table hover responsive>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Project</th>
                                    <th>Inspector</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {safetyReports.map(report => (
                                    <tr key={report.id}>
                                        <td>{formatDate(report.report_date)}</td>
                                        <td>{report.project_name}</td>
                                        <td>{report.inspector_name}</td>
                                        <td>
                                            <Badge bg={
                                                report.compliance_status === 'Compliant' ? 'success' :
                                                    report.compliance_status === 'Warning Issued' ? 'warning' : 'danger'
                                            }>
                                                {report.compliance_status}
                                            </Badge>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </div>
                );

            case 'finances':
                return (
                    <div>
                        <h5>Project Budgets</h5>
                        {projects.map(project => {
                            // Calculate spend based on material costs
                            const projectMaterials = materials.filter(m => m.project_id === project.id);
                            const materialCost = projectMaterials.reduce((total, mat) =>
                                total + (mat.quantity * mat.unit_price), 0);

                            // Assume materials cost is 40% of total spend for demo purposes
                            const estimatedTotalSpend = materialCost / 0.4;
                            const spentPercentage = Math.min(100, Math.round((estimatedTotalSpend / project.budget) * 100));

                            return (
                                <div key={project.id} className="mb-3">
                                    <div className="d-flex justify-content-between">
                                        <span>{project.name}</span>
                                        <span>{formatCurrency(project.budget)}</span>
                                    </div>
                                    <div className="progress">
                                        <div
                                            className={`progress-bar ${spentPercentage > 90 ? 'bg-danger' : 'bg-success'}`}
                                            role="progressbar"
                                            style={{ width: `${spentPercentage}%` }}
                                            aria-valuenow={spentPercentage}
                                            aria-valuemin="0"
                                            aria-valuemax="100"
                                        >
                                            {spentPercentage}%
                                        </div>
                                    </div>
                                    <small className="text-muted">
                                        Spent: {formatCurrency(estimatedTotalSpend)} / {formatCurrency(project.budget)}
                                    </small>
                                </div>
                            );
                        })}
                    </div>
                );

            case 'mail':
                return (
                    <div>
                        <div className="mail-item d-flex align-items-center p-2 border-bottom">
                            <div className="mail-sender me-auto">
                                <strong>Sarah Johnson</strong>
                            </div>
                            <div className="mail-date text-muted">10:45 AM</div>
                        </div>
                        <div className="mail-item d-flex align-items-center p-2 border-bottom">
                            <div className="mail-sender me-auto">
                                <strong>Mike Chen</strong>
                            </div>
                            <div className="mail-date text-muted">Yesterday</div>
                        </div>
                        <div className="text-center mt-2">
                            <Button variant="link" size="sm">View All Messages</Button>
                        </div>
                    </div>
                );

            default:
                return <p>No data available</p>;
        }
    };

    return (
        <DndProvider backend={HTML5Backend}>
        <div className="dashboard">
                <h1 className="mb-4">{pageTitle}</h1>

            <Row>
                    {tiles.map(tile => (
                        <DraggableTile
                            key={tile.id}
                            id={tile.id}
                            title={tile.title}
                            size={tile.size}
                            onSizeChange={handleTileSizeChange}
                        >
                            {renderTileContent(tile.id)}
                        </DraggableTile>
                    ))}
                    </Row>
        </div>
        </DndProvider>
    );
}

export default Dashboard; 