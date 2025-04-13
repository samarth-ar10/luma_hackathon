import React, { useState, useEffect } from 'react';
import { Card, Table, Form, Button, Alert, Badge, Row, Col, Dropdown, ProgressBar, Modal } from 'react-bootstrap';
import ApiService from '../services/api';

// Task status and priority constants
const STATUS_COLORS = {
    'Completed': 'success',
    'In Progress': 'primary',
    'Pending': 'secondary',
    'Delayed': 'danger',
    'Cancelled': 'dark'
};

const PRIORITY_COLORS = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
};

function TaskManager({ role }) {
    const [tasks, setTasks] = useState([]);
    const [filteredTasks, setFilteredTasks] = useState([]);
    const [projects, setProjects] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showTaskModal, setShowTaskModal] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [filter, setFilter] = useState({
        project: 'all',
        status: 'all',
        priority: 'all',
        assignee: 'all',
        search: ''
    });

    // Task statistics
    const [stats, setStats] = useState({
        total: 0,
        completed: 0,
        inProgress: 0,
        pending: 0,
        delayed: 0,
        completionRate: 0
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                const data = await ApiService.getRoleData(role);
                const taskData = data.tasks || [];

                setTasks(taskData);
                setFilteredTasks(taskData);
                setProjects(data.projects || []);

                // Set up demo users based on the data 
                const uniqueAssignees = [...new Set(taskData.map(task => task.assigned_to))];
                setUsers(uniqueAssignees.filter(Boolean).map(name => ({ name })));

                // Calculate task stats
                updateTaskStats(taskData);
            } catch (err) {
                console.error('Error fetching task data:', err);
                setError('Failed to load task data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [role]);

    useEffect(() => {
        // Apply filters whenever filter state changes
        applyFilters();
    }, [filter, tasks]);

    const updateTaskStats = (taskData) => {
        const total = taskData.length;
        const completed = taskData.filter(t => t.status === 'Completed').length;
        const inProgress = taskData.filter(t => t.status === 'In Progress').length;
        const pending = taskData.filter(t => t.status === 'Pending').length;
        const delayed = taskData.filter(t => t.status === 'Delayed').length;

        setStats({
            total,
            completed,
            inProgress,
            pending,
            delayed,
            completionRate: total > 0 ? Math.round((completed / total) * 100) : 0
        });
    };

    const applyFilters = () => {
        let filtered = [...tasks];

        // Filter by project
        if (filter.project !== 'all') {
            filtered = filtered.filter(task =>
                task.project_id === parseInt(filter.project)
            );
        }

        // Filter by status
        if (filter.status !== 'all') {
            filtered = filtered.filter(task =>
                task.status === filter.status
            );
        }

        // Filter by priority
        if (filter.priority !== 'all') {
            filtered = filtered.filter(task =>
                task.priority === filter.priority
            );
        }

        // Filter by assignee
        if (filter.assignee !== 'all') {
            filtered = filtered.filter(task =>
                task.assigned_to === filter.assignee
            );
        }

        // Filter by search term
        if (filter.search) {
            const searchTerm = filter.search.toLowerCase();
            filtered = filtered.filter(task =>
                task.name.toLowerCase().includes(searchTerm) ||
                (task.description && task.description.toLowerCase().includes(searchTerm))
            );
        }

        setFilteredTasks(filtered);
    };

    const handleFilterChange = (field, value) => {
        setFilter(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleStatusChange = async (taskId, newStatus) => {
        try {
            // Call API to update task status
            const result = await ApiService.updateTaskStatus(taskId, newStatus);

            if (result.success) {
                // Update local task data
                setTasks(prevTasks =>
                    prevTasks.map(task =>
                        task.id === taskId ? { ...task, status: newStatus } : task
                    )
                );

                // Recalculate stats
                updateTaskStats(tasks.map(task =>
                    task.id === taskId ? { ...task, status: newStatus } : task
                ));
            }
        } catch (err) {
            console.error('Error updating task status:', err);
            alert('Failed to update task status. Please try again.');
        }
    };

    const handleEditTask = (task) => {
        setEditingTask(task);
        setShowTaskModal(true);
    };

    const handleAddTask = () => {
        setEditingTask(null);
        setShowTaskModal(true);
    };

    const handleCloseModal = () => {
        setShowTaskModal(false);
        setEditingTask(null);
    };

    const handleSaveTask = async (e) => {
        e.preventDefault();
        // Save task logic would go here
        setShowTaskModal(false);
    };

    // Get project name by ID
    const getProjectName = (projectId) => {
        const project = projects.find(p => p.id === projectId);
        return project ? project.name : 'Unknown Project';
    };

    return (
        <div className="task-manager">
            <h1 className="mb-4">Task Management</h1>

            {loading ? (
                <div className="text-center p-5">Loading task data...</div>
            ) : error ? (
                <Alert variant="danger">{error}</Alert>
            ) : (
                <>
                    <Row className="mb-4">
                        <Col lg={4} md={6} className="mb-3 mb-lg-0">
                            <Card className="h-100">
                                <Card.Body>
                                    <h5 className="mb-3">Task Completion</h5>
                                    <ProgressBar
                                        now={stats.completionRate}
                                        label={`${stats.completionRate}%`}
                                        variant="success"
                                        className="mb-3"
                                    />
                                    <div className="d-flex justify-content-between">
                                        <small>{stats.completed} of {stats.total} tasks completed</small>
                                        <small>{stats.inProgress} in progress</small>
                                    </div>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col lg={8} md={6}>
                            <Card className="h-100">
                                <Card.Body>
                                    <h5 className="mb-3">Task Summary</h5>
                                    <Row>
                                        <Col xs={3} className="text-center">
                                            <div className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                                                <h4 className="mb-0">{stats.inProgress}</h4>
                                            </div>
                                            <p className="mt-2 mb-0">In Progress</p>
                                        </Col>
                                        <Col xs={3} className="text-center">
                                            <div className="rounded-circle bg-success text-white d-inline-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                                                <h4 className="mb-0">{stats.completed}</h4>
                                            </div>
                                            <p className="mt-2 mb-0">Completed</p>
                                        </Col>
                                        <Col xs={3} className="text-center">
                                            <div className="rounded-circle bg-secondary text-white d-inline-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                                                <h4 className="mb-0">{stats.pending}</h4>
                                            </div>
                                            <p className="mt-2 mb-0">Pending</p>
                                        </Col>
                                        <Col xs={3} className="text-center">
                                            <div className="rounded-circle bg-danger text-white d-inline-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                                                <h4 className="mb-0">{stats.delayed}</h4>
                                            </div>
                                            <p className="mt-2 mb-0">Delayed</p>
                                        </Col>
                                    </Row>
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
                                <Col md={3} className="mb-3">
                                    <Form.Group>
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
                                <Col md={3} className="mb-3">
                                    <Form.Group>
                                        <Form.Label>Status</Form.Label>
                                        <Form.Select
                                            value={filter.status}
                                            onChange={(e) => handleFilterChange('status', e.target.value)}
                                        >
                                            <option value="all">All Statuses</option>
                                            {Object.keys(STATUS_COLORS).map(status => (
                                                <option key={status} value={status}>
                                                    {status}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={3} className="mb-3">
                                    <Form.Group>
                                        <Form.Label>Priority</Form.Label>
                                        <Form.Select
                                            value={filter.priority}
                                            onChange={(e) => handleFilterChange('priority', e.target.value)}
                                        >
                                            <option value="all">All Priorities</option>
                                            {Object.keys(PRIORITY_COLORS).map(priority => (
                                                <option key={priority} value={priority}>
                                                    {priority}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={3} className="mb-3">
                                    <Form.Group>
                                        <Form.Label>Assignee</Form.Label>
                                        <Form.Select
                                            value={filter.assignee}
                                            onChange={(e) => handleFilterChange('assignee', e.target.value)}
                                        >
                                            <option value="all">All Assignees</option>
                                            {users.map(user => (
                                                <option key={user.name} value={user.name}>
                                                    {user.name}
                                                </option>
                                            ))}
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={9}>
                                    <Form.Group>
                                        <Form.Label>Search</Form.Label>
                                        <Form.Control
                                            type="text"
                                            placeholder="Search tasks by name or description..."
                                            value={filter.search}
                                            onChange={(e) => handleFilterChange('search', e.target.value)}
                                        />
                                    </Form.Group>
                                </Col>
                                <Col md={3} className="d-flex align-items-end">
                                    <Button
                                        variant="outline-secondary"
                                        className="w-100"
                                        onClick={() => setFilter({
                                            project: 'all',
                                            status: 'all',
                                            priority: 'all',
                                            assignee: 'all',
                                            search: ''
                                        })}
                                    >
                                        Clear Filters
                                    </Button>
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>

                    <Card>
                        <Card.Header className="d-flex justify-content-between align-items-center">
                            <h5>Tasks</h5>
                            <Button
                                variant="primary"
                                onClick={handleAddTask}
                            >
                                + Add Task
                            </Button>
                        </Card.Header>
                        <Card.Body>
                            <Table hover responsive>
                                <thead>
                                    <tr>
                                        <th>Task</th>
                                        <th>Project</th>
                                        <th>Status</th>
                                        <th>Priority</th>
                                        <th>Assigned To</th>
                                        <th>Due Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredTasks.map(task => (
                                        <tr key={task.id}>
                                            <td>
                                                <div className="d-flex flex-column">
                                                    <strong>{task.name}</strong>
                                                    {task.description && (
                                                        <small className="text-muted">{task.description.substring(0, 50)}...</small>
                                                    )}
                                                </div>
                                            </td>
                                            <td>{getProjectName(task.project_id)}</td>
                                            <td>
                                                <Badge bg={STATUS_COLORS[task.status] || 'secondary'}>
                                                    {task.status}
                                                </Badge>
                                            </td>
                                            <td>
                                                <Badge bg={PRIORITY_COLORS[task.priority] || 'secondary'}>
                                                    {task.priority}
                                                </Badge>
                                            </td>
                                            <td>{task.assigned_to}</td>
                                            <td>{task.due_date}</td>
                                            <td>
                                                <div className="d-flex">
                                                    <Dropdown>
                                                        <Dropdown.Toggle variant="outline-primary" size="sm" id={`status-dropdown-${task.id}`}>
                                                            Status
                                                        </Dropdown.Toggle>
                                                        <Dropdown.Menu>
                                                            {Object.keys(STATUS_COLORS).map(status => (
                                                                <Dropdown.Item
                                                                    key={status}
                                                                    active={task.status === status}
                                                                    onClick={() => handleStatusChange(task.id, status)}
                                                                >
                                                                    {status}
                                                                </Dropdown.Item>
                                                            ))}
                                                        </Dropdown.Menu>
                                                    </Dropdown>
                                                    <Button
                                                        variant="outline-secondary"
                                                        size="sm"
                                                        className="ms-2"
                                                        onClick={() => handleEditTask(task)}
                                                    >
                                                        Edit
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>

                            {filteredTasks.length === 0 && (
                                <div className="text-center p-4">
                                    <p className="text-muted">No tasks found matching the current filters.</p>
                                </div>
                            )}
                        </Card.Body>
                    </Card>

                    {/* Task Modal */}
                    <Modal show={showTaskModal} onHide={handleCloseModal} size="lg">
                        <Modal.Header closeButton>
                            <Modal.Title>
                                {editingTask ? 'Edit Task' : 'Create New Task'}
                            </Modal.Title>
                        </Modal.Header>
                        <Modal.Body>
                            <Form onSubmit={handleSaveTask}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Task Name</Form.Label>
                                    <Form.Control
                                        type="text"
                                        required
                                        defaultValue={editingTask?.name || ''}
                                        placeholder="Enter task name"
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3">
                                    <Form.Label>Description</Form.Label>
                                    <Form.Control
                                        as="textarea"
                                        rows={3}
                                        defaultValue={editingTask?.description || ''}
                                        placeholder="Provide task details..."
                                    />
                                </Form.Group>

                                <Row>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Project</Form.Label>
                                            <Form.Select
                                                required
                                                defaultValue={editingTask?.project_id || ''}
                                            >
                                                <option value="">Select Project</option>
                                                {projects.map(project => (
                                                    <option key={project.id} value={project.id}>
                                                        {project.name}
                                                    </option>
                                                ))}
                                            </Form.Select>
                                        </Form.Group>
                                    </Col>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Due Date</Form.Label>
                                            <Form.Control
                                                type="date"
                                                defaultValue={editingTask?.due_date || ''}
                                            />
                                        </Form.Group>
                                    </Col>
                                </Row>

                                <Row>
                                    <Col md={4}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Status</Form.Label>
                                            <Form.Select
                                                required
                                                defaultValue={editingTask?.status || 'Pending'}
                                            >
                                                {Object.keys(STATUS_COLORS).map(status => (
                                                    <option key={status} value={status}>
                                                        {status}
                                                    </option>
                                                ))}
                                            </Form.Select>
                                        </Form.Group>
                                    </Col>
                                    <Col md={4}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Priority</Form.Label>
                                            <Form.Select
                                                required
                                                defaultValue={editingTask?.priority || 'Medium'}
                                            >
                                                {Object.keys(PRIORITY_COLORS).map(priority => (
                                                    <option key={priority} value={priority}>
                                                        {priority}
                                                    </option>
                                                ))}
                                            </Form.Select>
                                        </Form.Group>
                                    </Col>
                                    <Col md={4}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Assigned To</Form.Label>
                                            <Form.Select
                                                required
                                                defaultValue={editingTask?.assigned_to || ''}
                                            >
                                                <option value="">Select Assignee</option>
                                                {users.map(user => (
                                                    <option key={user.name} value={user.name}>
                                                        {user.name}
                                                    </option>
                                                ))}
                                            </Form.Select>
                                        </Form.Group>
                                    </Col>
                                </Row>
                            </Form>
                        </Modal.Body>
                        <Modal.Footer>
                            <Button variant="secondary" onClick={handleCloseModal}>
                                Cancel
                            </Button>
                            <Button variant="primary" onClick={handleSaveTask}>
                                {editingTask ? 'Update Task' : 'Create Task'}
                            </Button>
                        </Modal.Footer>
                    </Modal>
                </>
            )}
        </div>
    );
}

export default TaskManager; 