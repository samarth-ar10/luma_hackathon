import React, { useState, useEffect } from 'react';
import { Table, Button, Form, Modal, Alert, Badge } from 'react-bootstrap';
import ApiService from '../services/api';

function EmployeeList() {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [newEmployee, setNewEmployee] = useState({
        name: '',
        email: '',
        department: '',
        role: '',
        hire_date: ''
    });

    // Load employee data
    useEffect(() => {
        const fetchEmployees = async () => {
            try {
                setLoading(true);

                // Since we're repurposing the /roles/ceo endpoint that returns employee data
                const response = await ApiService.getRoleData('ceo');

                // We'll extract the employee data from the team field
                if (response && response.team && response.team.results) {
                    setEmployees(response.team.results);
                } else {
                    // Fallback to mock data if the endpoint doesn't return what we expect
                    setEmployees([
                        { id: 1, name: "John Smith", email: "john.smith@company.com", department: "Executive", role: "CEO", hire_date: "2020-01-01" },
                        { id: 2, name: "Sarah Johnson", email: "sarah.j@company.com", department: "Marketing", role: "Marketing Director", hire_date: "2020-02-15" },
                        { id: 3, name: "Michael Lee", email: "michael.l@company.com", department: "Sales", role: "Sales Director", hire_date: "2020-03-10" },
                        { id: 4, name: "Emily Brown", email: "emily.b@company.com", department: "Engineering", role: "CTO", hire_date: "2020-02-01" }
                    ]);
                }

                setLoading(false);
            } catch (error) {
                console.error('Error fetching employees:', error);
                setError('Failed to load employee data');
                setLoading(false);
            }
        };

        fetchEmployees();
    }, []);

    const handleCloseModal = () => {
        setShowAddModal(false);
        setNewEmployee({ name: '', email: '', department: '', role: '', hire_date: '' });
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewEmployee({
            ...newEmployee,
            [name]: value
        });
    };

    const handleAddEmployee = async () => {
        // Validation
        if (!newEmployee.name || !newEmployee.email || !newEmployee.department || !newEmployee.role || !newEmployee.hire_date) {
            setError('All fields are required');
            return;
        }

        try {
            // In a production app, this would be an API call
            // For now, we'll just add to the state directly
            const newId = employees.length > 0 ? Math.max(...employees.map(e => e.id)) + 1 : 1;
            const employeeToAdd = {
                id: newId,
                ...newEmployee
            };

            setEmployees([...employees, employeeToAdd]);
            handleCloseModal();
            setError(null);
        } catch (error) {
            console.error('Error adding employee:', error);
            setError('Failed to add employee');
        }
    };

    const handleDeleteEmployee = async (id) => {
        try {
            // In a production app, this would be an API call
            // For now, we'll just update the state directly
            setEmployees(employees.filter(employee => employee.id !== id));
        } catch (error) {
            console.error('Error deleting employee:', error);
            setError('Failed to delete employee');
        }
    };

    if (loading) {
        return <div className="text-center p-5">Loading employees...</div>;
    }

    return (
        <div className="employee-list">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Employee Directory</h1>
                <Button variant="primary" onClick={() => setShowAddModal(true)}>Add Employee</Button>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            <Table striped bordered hover responsive>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Department</th>
                        <th>Role</th>
                        <th>Hire Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {employees.map(employee => (
                        <tr key={employee.id}>
                            <td>{employee.id}</td>
                            <td>{employee.name}</td>
                            <td>{employee.email}</td>
                            <td>
                                <Badge bg={
                                    employee.department === 'Executive' ? 'dark' :
                                        employee.department === 'Engineering' ? 'info' :
                                            employee.department === 'Marketing' ? 'primary' :
                                                employee.department === 'Sales' ? 'success' :
                                                    employee.department === 'Construction' ? 'warning' : 'secondary'
                                }>
                                    {employee.department}
                                </Badge>
                            </td>
                            <td>{employee.role}</td>
                            <td>{employee.hire_date}</td>
                            <td>
                                <Button
                                    variant="outline-danger"
                                    size="sm"
                                    onClick={() => handleDeleteEmployee(employee.id)}
                                >
                                    Delete
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>

            {/* Add Employee Modal */}
            <Modal show={showAddModal} onHide={handleCloseModal}>
                <Modal.Header closeButton>
                    <Modal.Title>Add New Employee</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Name</Form.Label>
                            <Form.Control
                                type="text"
                                name="name"
                                value={newEmployee.name}
                                onChange={handleInputChange}
                                placeholder="Enter employee name"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Email</Form.Label>
                            <Form.Control
                                type="email"
                                name="email"
                                value={newEmployee.email}
                                onChange={handleInputChange}
                                placeholder="Enter email"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Department</Form.Label>
                            <Form.Select
                                name="department"
                                value={newEmployee.department}
                                onChange={handleInputChange}
                            >
                                <option value="">Select Department</option>
                                <option value="Executive">Executive</option>
                                <option value="Engineering">Engineering</option>
                                <option value="Marketing">Marketing</option>
                                <option value="Sales">Sales</option>
                                <option value="Construction">Construction</option>
                                <option value="HR">HR</option>
                            </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Role</Form.Label>
                            <Form.Control
                                type="text"
                                name="role"
                                value={newEmployee.role}
                                onChange={handleInputChange}
                                placeholder="Enter role"
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>Hire Date</Form.Label>
                            <Form.Control
                                type="date"
                                name="hire_date"
                                value={newEmployee.hire_date}
                                onChange={handleInputChange}
                            />
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleCloseModal}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleAddEmployee}>
                        Add Employee
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
}

export default EmployeeList; 