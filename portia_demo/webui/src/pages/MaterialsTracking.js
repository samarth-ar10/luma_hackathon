import React, { useState, useEffect } from 'react';
import { Card, Table, Form, Button, Alert, Badge, Row, Col, InputGroup } from 'react-bootstrap';
import ApiService from '../services/api';

function MaterialsTracking({ role }) {
    const [materials, setMaterials] = useState([]);
    const [filteredMaterials, setFilteredMaterials] = useState([]);
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState({
        project: 'all',
        status: 'all',
        search: ''
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                const data = await ApiService.getRoleData(role);
                setMaterials(data.materials || []);
                setFilteredMaterials(data.materials || []);
                setProjects(data.projects || []);
            } catch (err) {
                console.error('Error fetching materials data:', err);
                setError('Failed to load materials data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [role]);

    useEffect(() => {
        // Apply filters whenever filter state changes
        applyFilters();
    }, [filter, materials]);

    const applyFilters = () => {
        let filtered = [...materials];

        // Filter by project
        if (filter.project !== 'all') {
            filtered = filtered.filter(material =>
                material.project_id === parseInt(filter.project)
            );
        }

        // Filter by status
        if (filter.status !== 'all') {
            filtered = filtered.filter(material =>
                material.status.toLowerCase() === filter.status.toLowerCase()
            );
        }

        // Filter by search term
        if (filter.search) {
            const searchTerm = filter.search.toLowerCase();
            filtered = filtered.filter(material =>
                material.name.toLowerCase().includes(searchTerm)
            );
        }

        setFilteredMaterials(filtered);
    };

    const handleFilterChange = (field, value) => {
        setFilter(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const calculateTotalCost = () => {
        return filteredMaterials.reduce((total, material) => {
            return total + (material.quantity * material.unit_price);
        }, 0);
    };

    // Get project name by ID
    const getProjectName = (projectId) => {
        const project = projects.find(p => p.id === projectId);
        return project ? project.name : 'Unknown Project';
    };

    return (
        <div className="materials-tracking">
            <h1 className="mb-4">Materials Tracking</h1>

            {loading ? (
                <div className="text-center p-5">Loading materials data...</div>
            ) : error ? (
                <Alert variant="danger">{error}</Alert>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col lg={3} md={6} className="mb-3 mb-md-0">
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>${calculateTotalCost().toLocaleString()}</h3>
                                    <Card.Title>Total Material Cost</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6} className="mb-3 mb-md-0">
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>{filteredMaterials.length}</h3>
                                    <Card.Title>Materials</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6} className="mb-3 mb-lg-0">
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>
                                        {filteredMaterials.filter(m => m.status === 'Ordered').length}
                                    </h3>
                                    <Card.Title>Pending Deliveries</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6}>
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>
                                        {filteredMaterials.filter(m => m.status === 'Delivered').length}
                                    </h3>
                                    <Card.Title>Delivered Materials</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Card className="mb-4">
                        <Card.Header>
                            <h5>Filters</h5>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                <Col md={4}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Project</Form.Label>
                                        <Form.Select
                                            value={filter.project}
                                            onChange={(e) => handleFilterChange('project', e.target.value)}
                                        >
                                            <option value="all">All Projects</option>
                                            {projects.map(project => (
                                                <option key={project.id} value={project.id}>
                                                    {project.name}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Status</Form.Label>
                                        <Form.Select
                                            value={filter.status}
                                            onChange={(e) => handleFilterChange('status', e.target.value)}
                                        >
                                            <option value="all">All Statuses</option>
                                            <option value="Ordered">Ordered</option>
                                            <option value="Delivered">Delivered</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Search</Form.Label>
                                        <InputGroup>
                                            <Form.Control
                                                type="text"
                                                placeholder="Search materials..."
                                                value={filter.search}
                                                onChange={(e) => handleFilterChange('search', e.target.value)}
                                            />
                                            {filter.search && (
                                                <Button
                                                    variant="outline-secondary"
                                                    onClick={() => handleFilterChange('search', '')}
                                                >
                                                    &times;
                                                </Button>
                                            )}
                                        </InputGroup>
                                    </Form.Group>
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>

                    <Card>
                        <Card.Header className="d-flex justify-content-between align-items-center">
                            <h5>Materials List</h5>
                            <Button variant="primary" size="sm">+ Add Material</Button>
                        </Card.Header>
                        <Card.Body>
                            <Table hover responsive>
                                <thead>
                                    <tr>
                                        <th>Material</th>
                                        <th>Quantity</th>
                                        <th>Unit Price</th>
                                        <th>Total Cost</th>
                                        <th>Project</th>
                                        <th>Delivery Date</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredMaterials.map(material => (
                                        <tr key={material.id}>
                                            <td>{material.name}</td>
                                            <td>{material.quantity} {material.unit}</td>
                                            <td>${material.unit_price.toFixed(2)}</td>
                                            <td>${(material.quantity * material.unit_price).toLocaleString()}</td>
                                            <td>{getProjectName(material.project_id)}</td>
                                            <td>{material.delivery_date || 'Not scheduled'}</td>
                                            <td>
                                                <Badge bg={
                                                    material.status === 'Delivered' ? 'success' :
                                                        material.status === 'Ordered' ? 'warning' : 'danger'
                                                }>
                                                    {material.status}
                                                </Badge>
                                            </td>
                                            <td>
                                                <Button
                                                    variant="outline-primary"
                                                    size="sm"
                                                    className="me-1"
                                                >
                                                    Edit
                                                </Button>
                                                {material.status === 'Ordered' && (
                                                    <Button
                                                        variant="outline-success"
                                                        size="sm"
                                                        onClick={() => {
                                                            // Mark as delivered logic would go here
                                                            alert(`Marked ${material.name} as delivered`);
                                                        }}
                                                    >
                                                        Mark Delivered
                                                    </Button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>

                            {filteredMaterials.length === 0 && (
                                <div className="text-center p-4">
                                    <p className="text-muted">No materials found matching the current filters.</p>
                                </div>
                            )}
                        </Card.Body>
                    </Card>
                </>
            )}
        </div>
    );
}

export default MaterialsTracking; 