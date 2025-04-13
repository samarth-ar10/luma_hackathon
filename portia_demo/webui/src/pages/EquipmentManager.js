import React, { useState, useEffect } from 'react';
import { Card, Table, Form, Button, Alert, Badge, Row, Col, InputGroup, Modal, Tab, Tabs } from 'react-bootstrap';
import ApiService from '../services/api';
import { formatDate, formatCurrency, getUserById } from '../data/DataService';

function EquipmentManager({ role }) {
    const [equipment, setEquipment] = useState([]);
    const [maintenanceLogs, setMaintenanceLogs] = useState([]);
    const [filteredEquipment, setFilteredEquipment] = useState([]);
    const [projects, setProjects] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState({
        project: 'all',
        status: 'all',
        type: 'all',
        search: ''
    });

    // Modal states
    const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [selectedEquipment, setSelectedEquipment] = useState(null);
    const [maintenanceData, setMaintenanceData] = useState({
        equipment_id: null,
        maintenance_date: new Date().toISOString().split('T')[0],
        maintenance_type: 'Routine',
        description: '',
        performed_by: null,
        cost: 0
    });
    const [assignData, setAssignData] = useState({
        equipment_id: null,
        project_id: '',
        user_id: ''
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                const data = await ApiService.getRoleData(role);
                setEquipment(data.equipment || []);
                setFilteredEquipment(data.equipment || []);
                setProjects(data.projects || []);
                setUsers(data.users || []);
                setMaintenanceLogs(data.maintenanceLogs || []);
            } catch (err) {
                console.error('Error fetching equipment data:', err);
                setError('Failed to load equipment data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [role]);

    useEffect(() => {
        // Apply filters whenever filter state changes
        applyFilters();
    }, [filter, equipment]);

    const applyFilters = () => {
        let filtered = [...equipment];

        // Filter by project
        if (filter.project !== 'all') {
            if (filter.project === 'unassigned') {
                filtered = filtered.filter(item => !item.assigned_project);
            } else {
                filtered = filtered.filter(item =>
                    item.assigned_project === parseInt(filter.project)
                );
            }
        }

        // Filter by status
        if (filter.status !== 'all') {
            filtered = filtered.filter(item =>
                item.status === filter.status
            );
        }

        // Filter by type
        if (filter.type !== 'all') {
            filtered = filtered.filter(item =>
                item.type === filter.type
            );
        }

        // Filter by search term
        if (filter.search) {
            const searchTerm = filter.search.toLowerCase();
            filtered = filtered.filter(item =>
                item.name.toLowerCase().includes(searchTerm)
            );
        }

        setFilteredEquipment(filtered);
    };

    const handleFilterChange = (field, value) => {
        setFilter(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const calculateDailyCost = () => {
        return filteredEquipment.reduce((total, item) => {
            return total + (item.daily_cost || 0);
        }, 0);
    };

    const calculateMaintenanceCost = () => {
        return maintenanceLogs.reduce((total, log) => {
            return total + (log.cost || 0);
        }, 0);
    };

    // Get project name by ID
    const getProjectName = (projectId) => {
        if (!projectId) return 'Unassigned';
        const project = projects.find(p => p.id === projectId);
        return project ? project.name : 'Unknown Project';
    };

    // Get user name by ID
    const getUserName = (userId) => {
        if (!userId) return 'Unassigned';
        const user = users.find(u => u.id === userId);
        return user ? user.name : 'Unknown User';
    };

    // Get status badge variant
    const getStatusBadgeVariant = (status) => {
        switch (status) {
            case 'Operational':
                return 'success';
            case 'Under Maintenance':
                return 'warning';
            case 'Out of Service':
                return 'danger';
            default:
                return 'secondary';
        }
    };

    // Calculate days until next maintenance
    const getDaysUntilMaintenance = (nextMaintenance) => {
        if (!nextMaintenance) return null;

        const now = new Date();
        const maintenanceDate = new Date(nextMaintenance);
        const diffTime = maintenanceDate - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        return diffDays;
    };

    // Get maintenance logs for specific equipment
    const getEquipmentMaintenanceLogs = (equipmentId) => {
        return maintenanceLogs.filter(log => log.equipment_id === equipmentId);
    };

    // Handle opening maintenance modal
    const openMaintenanceModal = (equipment) => {
        setSelectedEquipment(equipment);
        setMaintenanceData({
            equipment_id: equipment.id,
            maintenance_date: new Date().toISOString().split('T')[0],
            maintenance_type: 'Routine',
            description: '',
            performed_by: role === 'foreman' ? 5 : (role === 'engineer' ? 3 : null), // Set default user based on role
            cost: 0
        });
        setShowMaintenanceModal(true);
    };

    // Handle opening assign modal
    const openAssignModal = (equipment) => {
        setSelectedEquipment(equipment);
        setAssignData({
            equipment_id: equipment.id,
            project_id: equipment.assigned_project || '',
            user_id: equipment.assigned_to || ''
        });
        setShowAssignModal(true);
    };

    // Handle maintenance form changes
    const handleMaintenanceChange = (field, value) => {
        setMaintenanceData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    // Handle assign form changes
    const handleAssignChange = (field, value) => {
        setAssignData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    // Submit maintenance log
    const submitMaintenance = async () => {
        try {
            setLoading(true);
            const result = await ApiService.logMaintenance(maintenanceData);

            if (result.success) {
                // Update equipment status if needed
                if (maintenanceData.maintenance_type === 'Repair' ||
                    maintenanceData.maintenance_type === 'Routine') {
                    await ApiService.updateEquipmentStatus(selectedEquipment.id, 'Operational');
                }

                // Refresh data
                const data = await ApiService.getRoleData(role);
                setEquipment(data.equipment || []);
                setMaintenanceLogs(data.maintenanceLogs || []);

                // Close modal
                setShowMaintenanceModal(false);
                alert('Maintenance log added successfully!');
            }
        } catch (err) {
            console.error('Error submitting maintenance:', err);
            setError('Failed to submit maintenance log');
        } finally {
            setLoading(false);
        }
    };

    // Submit equipment assignment
    const submitAssignment = async () => {
        try {
            setLoading(true);
            const result = await ApiService.assignEquipment(
                selectedEquipment.id,
                assignData.project_id || null,
                assignData.user_id || null
            );

            if (result.success) {
                // Refresh data
                const data = await ApiService.getRoleData(role);
                setEquipment(data.equipment || []);

                // Close modal
                setShowAssignModal(false);
                alert('Equipment assigned successfully!');
            }
        } catch (err) {
            console.error('Error assigning equipment:', err);
            setError('Failed to assign equipment');
        } finally {
            setLoading(false);
        }
    };

    // Get unique equipment types for filtering
    const equipmentTypes = [...new Set(equipment.map(item => item.type))];

    return (
        <div className="equipment-manager">
            <h1 className="mb-4">Equipment Manager</h1>

            {loading && !showMaintenanceModal && !showAssignModal ? (
                <div className="text-center p-5">Loading equipment data...</div>
            ) : error ? (
                <Alert variant="danger">{error}</Alert>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col lg={3} md={6} className="mb-3 mb-md-0">
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>{filteredEquipment.length}</h3>
                                    <Card.Title>Total Equipment</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6} className="mb-3 mb-md-0">
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>
                                        {filteredEquipment.filter(e => e.status === 'Operational').length}
                                    </h3>
                                    <Card.Title>Operational Equipment</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6} className="mb-3 mb-lg-0">
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>{formatCurrency(calculateDailyCost())}/day</h3>
                                    <Card.Title>Daily Equipment Cost</Card.Title>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={3} md={6}>
                            <Card className="h-100">
                                <Card.Body className="text-center">
                                    <h3>{formatCurrency(calculateMaintenanceCost())}</h3>
                                    <Card.Title>Maintenance Costs</Card.Title>
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
                                <Col md={3}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Project</Form.Label>
                                        <Form.Select
                                            value={filter.project}
                                            onChange={(e) => handleFilterChange('project', e.target.value)}
                                        >
                                            <option value="all">All Projects</option>
                                            <option value="unassigned">Unassigned</option>
                                            {projects.map(project => (
                                                <option key={project.id} value={project.id}>
                                                    {project.name}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={3}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Status</Form.Label>
                                        <Form.Select
                                            value={filter.status}
                                            onChange={(e) => handleFilterChange('status', e.target.value)}
                                        >
                                            <option value="all">All Statuses</option>
                                            <option value="Operational">Operational</option>
                                            <option value="Under Maintenance">Under Maintenance</option>
                                            <option value="Out of Service">Out of Service</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={3}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Equipment Type</Form.Label>
                                        <Form.Select
                                            value={filter.type}
                                            onChange={(e) => handleFilterChange('type', e.target.value)}
                                        >
                                            <option value="all">All Types</option>
                                            {equipmentTypes.map(type => (
                                                <option key={type} value={type}>
                                                    {type}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={3}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Search</Form.Label>
                                        <InputGroup>
                                            <Form.Control
                                                type="text"
                                                placeholder="Search equipment..."
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
                            <h5>Equipment Inventory</h5>
                            <Button variant="primary" size="sm">+ Add Equipment</Button>
                        </Card.Header>
                        <Card.Body>
                            <Table hover responsive>
                                <thead>
                                    <tr>
                                        <th>Equipment</th>
                                        <th>Type</th>
                                        <th>Status</th>
                                        <th>Project</th>
                                        <th>Assigned To</th>
                                        <th>Last Maintenance</th>
                                        <th>Next Maintenance</th>
                                        <th>Daily Cost</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredEquipment.map(item => {
                                        const daysUntilMaintenance = getDaysUntilMaintenance(item.next_maintenance);
                                        const maintenanceUrgent = daysUntilMaintenance !== null && daysUntilMaintenance <= 7;

                                        return (
                                            <tr key={item.id}>
                                                <td>{item.name}</td>
                                                <td>{item.type}</td>
                                                <td>
                                                    <Badge bg={getStatusBadgeVariant(item.status)}>
                                                        {item.status}
                                                    </Badge>
                                                </td>
                                                <td>{getProjectName(item.assigned_project)}</td>
                                                <td>{getUserName(item.assigned_to)}</td>
                                                <td>{formatDate(item.last_maintenance)}</td>
                                                <td>
                                                    {formatDate(item.next_maintenance)}
                                                    {maintenanceUrgent && (
                                                        <Badge bg="danger" className="ms-2">
                                                            {daysUntilMaintenance <= 0 ? 'Overdue' : `${daysUntilMaintenance} days`}
                                                        </Badge>
                                                    )}
                                                </td>
                                                <td>${item.daily_cost?.toFixed(2)}/day</td>
                                                <td>
                                                    <Button
                                                        variant="outline-primary"
                                                        size="sm"
                                                        className="me-1"
                                                        onClick={() => openMaintenanceModal(item)}
                                                    >
                                                        Log Maintenance
                                                    </Button>
                                                    <Button
                                                        variant="outline-secondary"
                                                        size="sm"
                                                        onClick={() => openAssignModal(item)}
                                                    >
                                                        Assign
                                                    </Button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </Table>

                            {filteredEquipment.length === 0 && (
                                <div className="text-center p-4">
                                    <p className="text-muted">No equipment found matching the current filters.</p>
                                </div>
                            )}
                        </Card.Body>
                    </Card>

                    {/* Maintenance Log Modal */}
                    <Modal show={showMaintenanceModal} onHide={() => setShowMaintenanceModal(false)} size="lg">
                        <Modal.Header closeButton>
                            <Modal.Title>
                                Log Maintenance for {selectedEquipment?.name}
                            </Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Tabs defaultActiveKey="logMaintenance" id="maintenance-tabs">
                                <Tab eventKey="logMaintenance" title="Log Maintenance">
                                    <Form className="mt-3">
                                        <Row>
                                            <Col md={6}>
                                                <Form.Group className="mb-3">
                                                    <Form.Label>Maintenance Date</Form.Label>
                                                    <Form.Control
                                                        type="date"
                                                        value={maintenanceData.maintenance_date}
                                                        onChange={(e) => handleMaintenanceChange('maintenance_date', e.target.value)}
                                                    />
                                                </Form.Group>
                                            </Col>
                                            <Col md={6}>
                                                <Form.Group className="mb-3">
                                                    <Form.Label>Maintenance Type</Form.Label>
                                                    <Form.Select
                                                        value={maintenanceData.maintenance_type}
                                                        onChange={(e) => handleMaintenanceChange('maintenance_type', e.target.value)}
                                                    >
                                                        <option value="Routine">Routine</option>
                                                        <option value="Repair">Repair</option>
                                                        <option value="Inspection">Inspection</option>
                                                        <option value="Calibration">Calibration</option>
                                                        <option value="Emergency">Emergency</option>
                                                    </Form.Select>
                                                </Form.Group>
                                            </Col>
                                        </Row>

                                        <Form.Group className="mb-3">
                                            <Form.Label>Description</Form.Label>
                                            <Form.Control
                                                as="textarea"
                                                rows={3}
                                                value={maintenanceData.description}
                                                onChange={(e) => handleMaintenanceChange('description', e.target.value)}
                                                placeholder="Describe the maintenance work performed..."
                                            />
                                        </Form.Group>

                                        <Row>
                                            <Col md={6}>
                                                <Form.Group className="mb-3">
                                                    <Form.Label>Performed By</Form.Label>
                                                    <Form.Select
                                                        value={maintenanceData.performed_by || ''}
                                                        onChange={(e) => handleMaintenanceChange('performed_by', e.target.value ? parseInt(e.target.value) : null)}
                                                    >
                                                        <option value="">Select User</option>
                                                        {users.map(user => (
                                                            <option key={user.id} value={user.id}>
                                                                {user.name} ({user.role})
                                                            </option>
                                                        ))}
                                                    </Form.Select>
                                                </Form.Group>
                                            </Col>
                                            <Col md={6}>
                                                <Form.Group className="mb-3">
                                                    <Form.Label>Cost</Form.Label>
                                                    <InputGroup>
                                                        <InputGroup.Text>$</InputGroup.Text>
                                                        <Form.Control
                                                            type="number"
                                                            min="0"
                                                            step="0.01"
                                                            value={maintenanceData.cost}
                                                            onChange={(e) => handleMaintenanceChange('cost', parseFloat(e.target.value))}
                                                        />
                                                    </InputGroup>
                                                </Form.Group>
                                            </Col>
                                        </Row>
                                    </Form>
                                </Tab>
                                <Tab eventKey="history" title="Maintenance History">
                                    {selectedEquipment && (
                                        <div className="mt-3">
                                            <h5>Maintenance History for {selectedEquipment.name}</h5>
                                            {getEquipmentMaintenanceLogs(selectedEquipment.id).length === 0 ? (
                                                <p className="text-muted">No maintenance logs found for this equipment.</p>
                                            ) : (
                                                <Table striped bordered hover size="sm">
                                                    <thead>
                                                        <tr>
                                                            <th>Date</th>
                                                            <th>Type</th>
                                                            <th>Description</th>
                                                            <th>Performed By</th>
                                                            <th>Cost</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {getEquipmentMaintenanceLogs(selectedEquipment.id)
                                                            .sort((a, b) => new Date(b.maintenance_date) - new Date(a.maintenance_date))
                                                            .map(log => (
                                                                <tr key={log.id}>
                                                                    <td>{formatDate(log.maintenance_date)}</td>
                                                                    <td>{log.maintenance_type}</td>
                                                                    <td>{log.description}</td>
                                                                    <td>{getUserName(log.performed_by)}</td>
                                                                    <td>${log.cost?.toFixed(2)}</td>
                                                                </tr>
                                                            ))
                                                        }
                                                    </tbody>
                                                </Table>
                                            )}
                                        </div>
                                    )}
                                </Tab>
                            </Tabs>
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="secondary" onClick={() => setShowMaintenanceModal(false)}>
                                Cancel
                            </Button>
                            <Button
                                variant="primary"
                                onClick={submitMaintenance}
                                disabled={!maintenanceData.maintenance_date || !maintenanceData.description || maintenanceData.performed_by === null}
                            >
                                Log Maintenance
                            </Button>
                        </Modal.Footer>
                    </Modal>

                    {/* Assign Equipment Modal */}
                    <Modal show={showAssignModal} onHide={() => setShowAssignModal(false)}>
                        <Modal.Header closeButton>
                            <Modal.Title>
                                Assign {selectedEquipment?.name}
                            </Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Form>
                                <Form.Group className="mb-3">
                                    <Form.Label>Project</Form.Label>
                                    <Form.Select
                                        value={assignData.project_id}
                                        onChange={(e) => handleAssignChange('project_id', e.target.value ? parseInt(e.target.value) : '')}
                                    >
                                        <option value="">Unassigned</option>
                                        {projects.map(project => (
                                            <option key={project.id} value={project.id}>
                                                {project.name}
                                            </option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>

                                <Form.Group className="mb-3">
                                    <Form.Label>Assigned To</Form.Label>
                                    <Form.Select
                                        value={assignData.user_id}
                                        onChange={(e) => handleAssignChange('user_id', e.target.value ? parseInt(e.target.value) : '')}
                                    >
                                        <option value="">Unassigned</option>
                                        {users.map(user => (
                                            <option key={user.id} value={user.id}>
                                                {user.name} ({user.role})
                                            </option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>
                            </Form>
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="secondary" onClick={() => setShowAssignModal(false)}>
                                Cancel
                            </Button>
                            <Button
                                variant="primary"
                                onClick={submitAssignment}
                            >
                                Assign Equipment
                            </Button>
                        </Modal.Footer>
                    </Modal>
                </>
            )}
        </div>
    );
}

export default EquipmentManager; 