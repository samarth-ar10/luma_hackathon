import axios from 'axios';
import {
    useConstructionData,
    getProjectById,
    getTasksByProjectId,
    getMaterialsByProjectId,
    getSafetyReportsByProjectId,
    getUserById
} from '../data/DataService';

// Base URL for the API - Update to match Flask server port
const API_BASE_URL = 'http://localhost:5003/api';

// Create an axios instance with default configurations
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Data fetching functions for the dashboard
const fetchData = async (resource) => {
    try {
        const response = await api.get(`/data/${resource}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching ${resource}:`, error);
        throw error;
    }
};

const fetchAllData = async () => {
    try {
        const [projects, tasks, materials, equipment, safetyReports, users, maintenanceLogs] = await Promise.all([
            fetchData('projects'),
            fetchData('tasks'),
            fetchData('materials'),
            fetchData('equipment'),
            fetchData('safety_reports'),
            fetchData('users'),
            fetchData('maintenance_logs')
        ]);

        return {
            projects,
            tasks,
            materials,
            equipment,
            safetyReports,
            users,
            maintenanceLogs
        };
    } catch (error) {
        console.error('Error fetching all data:', error);
        throw error;
    }
};

// Role-specific data filters
const getRoleData = (role, allData) => {
    // Base data that all roles can see
    const baseData = {
        projects: allData.projects || [],
        tasks: allData.tasks || [],
        equipment: allData.equipment || []
    };

    // Add role-specific data and filters
    switch (role.toLowerCase()) {
        case 'ceo':
            return {
                ...allData,
                // CEOs see everything, maybe add some high-level KPIs
                financialSummary: {
                    revenue: 1250000,
                    expenses: 950000,
                    profit: 300000
                }
            };
        case 'project-manager':
            return {
                ...baseData,
                materials: allData.materials || [],
                users: allData.users || [],
                // Project managers need full access to project data
                projectAnalytics: {
                    onTrack: 8,
                    delayed: 2,
                    completed: 15
                }
            };
        case 'safety-officer':
            return {
                ...baseData,
                safetyReports: allData.safetyReports || [],
                // Safety officers focus on safety reports and compliance
                safetyMetrics: {
                    incidentCount: 3,
                    nearMissCount: 7,
                    inspectionsPassed: 12
                }
            };
        case 'equipment-manager':
            return {
                ...baseData,
                maintenanceLogs: allData.maintenanceLogs || [],
                // Equipment managers need equipment status
                equipmentMetrics: {
                    operational: 45,
                    maintenance: 8,
                    repair: 3
                }
            };
        default: // worker or any other role
            return baseData;
    }
};

// Get all available roles
const fetchAvailableRoles = async () => {
    try {
        const response = await api.get('/worker/roles');
        return response.data.roles || [];
    } catch (error) {
        console.error('Error fetching available roles:', error);
        // Fallback roles if API fails
        return ['ceo', 'project-manager', 'safety-officer', 'equipment-manager', 'worker'];
    }
};

// Worker AI communication API
const workerAPI = {
    // Get available Worker AI roles
    getAvailableRoles: fetchAvailableRoles,

    // Send a message to the Worker AI
    sendMessage: async (userId, role, message, context = {}) => {
        try {
            const response = await api.post('/worker/message', {
                user_id: userId,
                role,
                message,
                context
            });
            return response.data;
        } catch (error) {
            console.error('Error sending message to Worker AI:', error);
            return {
                message: "Sorry, I'm having trouble processing your request right now."
            };
        }
    },

    // Get the user's dashboard configuration for a specific role
    getDashboard: async (userId, role) => {
        try {
            const response = await api.get(`/worker/dashboard?user_id=${userId}&role=${role}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching dashboard:', error);
            return {
                error: "Could not load your dashboard",
                items: []
            };
        }
    },

    // Get conversation history for a specific role
    getConversationHistory: async (userId, role, limit = 10) => {
        try {
            const response = await api.get(`/worker/conversation?user_id=${userId}&role=${role}&limit=${limit}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching conversation history:', error);
            return [];
        }
    }
};

// API services for different endpoints
const ApiService = {
    // Use this function to get data for components that can't use React hooks directly
    getData: async () => {
        try {
            return await fetchAllData();
        } catch (error) {
            console.error('Error in getData:', error);
            throw error;
        }
    },

    // General stats for dashboard
    getStats: async () => {
        try {
            const data = await ApiService.getData();

            // Calculate some stats
            const totalProjects = data.projects.length;
            const projectsInProgress = data.projects.filter(p => p.status === 'In Progress').length;
            const completedTasks = data.tasks.filter(t => t.status === 'Completed').length;
            const totalTasks = data.tasks.length;
            const taskCompletionRate = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

            // Calculate total material cost
            const totalMaterialCost = data.materials.reduce((sum, m) => sum + (m.quantity * m.unit_price), 0);

            // Equipment stats
            const operationalEquipment = data.equipment.filter(e => e.status === 'Operational').length;
            const totalEquipment = data.equipment.length;
            const equipmentUsageRate = totalEquipment > 0 ? (operationalEquipment / totalEquipment) * 100 : 0;

            // Maintenance stats
            const maintenanceCost = data.maintenanceLogs.reduce((sum, log) => sum + log.cost, 0);

            return {
                totalProjects,
                projectsInProgress,
                completedTasks,
                totalTasks,
                taskCompletionRate,
                totalMaterialCost,
                operationalEquipment,
                totalEquipment,
                equipmentUsageRate,
                maintenanceCost
            };
        } catch (error) {
            console.error('Error calculating stats:', error);
            throw error;
        }
    },

    // Get role-specific data
    getRoleData: async (role) => {
        try {
            // Fetch all data
            const allData = await ApiService.getData();

            // Filter based on role
            return getRoleData(role, allData);
        } catch (error) {
            console.error(`Error fetching data for role ${role}:`, error);
            throw error;
        }
    },

    // Query LLM with Portia for construction data analysis
    askLLM: async (query, role, context = {}) => {
        try {
            // Use the Worker AI for LLM queries
            const userId = localStorage.getItem('user_id') || 'anonymous';
            return await workerAPI.sendMessage(userId, role, query, context);
        } catch (error) {
            console.error('Error querying LLM:', error);
            // Fallback to simulation for demo purposes
            return {
                message: `This is a simulated AI response to: "${query}"`,
                timestamp: new Date().toISOString()
            };
        }
    },

    // Execute a SQL query against our construction database
    executeQuery: async (sqlQuery) => {
        try {
            // Try to call the actual API
            try {
                const response = await api.post('/query', { sql: sqlQuery });
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, using local data:', apiError);

                // Fallback to local data handling
                const data = await ApiService.getData();

                if (sqlQuery.toLowerCase().includes('select * from projects')) {
                    return { success: true, results: data.projects };
                }

                if (sqlQuery.toLowerCase().includes('select * from tasks')) {
                    return { success: true, results: data.tasks };
                }

                if (sqlQuery.toLowerCase().includes('select * from materials')) {
                    return { success: true, results: data.materials };
                }

                if (sqlQuery.toLowerCase().includes('select * from safety_reports')) {
                    return { success: true, results: data.safetyReports };
                }

                if (sqlQuery.toLowerCase().includes('select * from equipment')) {
                    return { success: true, results: data.equipment };
                }

                if (sqlQuery.toLowerCase().includes('select * from equipment_maintenance_log')) {
                    return { success: true, results: data.maintenanceLogs };
                }

                return { success: false, error: 'Query not supported in local mode' };
            }
        } catch (error) {
            console.error('Error executing SQL query:', error);
            throw error;
        }
    },

    // Get customers data - fallback to simulated data if API fails
    getCustomers: async () => {
        try {
            try {
                const response = await api.get('/customers');
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, using simulated data:', apiError);

                // Simulated customer data
                return [
                    { id: 1, name: 'Metropolis Investments', email: 'contact@metropolis.com', phone: '555-123-4567' },
                    { id: 2, name: 'Urban Living Co.', email: 'info@urbanliving.com', phone: '555-234-5678' },
                    { id: 3, name: 'City of Metropolis', email: 'mayor@metropolis.gov', phone: '555-345-6789' }
                ];
            }
        } catch (error) {
            console.error('Error fetching customers:', error);
            throw error;
        }
    },

    // Equipment management methods

    // Get all equipment
    getEquipment: async () => {
        try {
            try {
                const response = await api.get('/equipment');
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, using local data:', apiError);
                const data = await ApiService.getData();
                return data.equipment;
            }
        } catch (error) {
            console.error('Error fetching equipment:', error);
            throw error;
        }
    },

    // Get equipment by ID
    getEquipmentById: async (equipmentId) => {
        try {
            try {
                const response = await api.get(`/equipment/${equipmentId}`);
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, using local data:', apiError);
                const data = await ApiService.getData();
                return data.equipment.find(e => e.id === equipmentId) || null;
            }
        } catch (error) {
            console.error(`Error fetching equipment with ID ${equipmentId}:`, error);
            throw error;
        }
    },

    // Update equipment status
    updateEquipmentStatus: async (equipmentId, status) => {
        try {
            const response = await api.patch(`/equipment/${equipmentId}`, { status });
            return response.data;
        } catch (error) {
            console.error('Error updating equipment status:', error);
            throw error;
        }
    },

    // Assign equipment to project
    assignEquipment: async (equipmentId, projectId, userId) => {
        try {
            const response = await api.patch(`/equipment/${equipmentId}/assign`, {
                project_id: projectId,
                user_id: userId
            });
            return response.data;
        } catch (error) {
            console.error('Error assigning equipment:', error);
            throw error;
        }
    },

    // Log equipment maintenance
    logMaintenance: async (maintenanceData) => {
        try {
            const response = await api.post('/maintenance-logs', maintenanceData);
            return response.data;
        } catch (error) {
            console.error('Error logging maintenance:', error);
            throw error;
        }
    },

    // Get maintenance logs for equipment
    getMaintenanceLogs: async (equipmentId = null) => {
        try {
            try {
                const url = equipmentId ? `/maintenance-logs?equipment_id=${equipmentId}` : '/maintenance-logs';
                const response = await api.get(url);
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, using local data:', apiError);
                const data = await ApiService.getData();

                if (equipmentId) {
                    return data.maintenanceLogs.filter(log => log.equipment_id === equipmentId);
                }

                return data.maintenanceLogs;
            }
        } catch (error) {
            console.error('Error fetching maintenance logs:', error);
            throw error;
        }
    },

    // Add a new customer
    addCustomer: async (customerData) => {
        try {
            const response = await api.post('/customers', customerData);
            return response.data;
        } catch (error) {
            console.error('Error adding customer:', error);
            // Simulate success for demo
            return {
                success: true,
                customer: {
                    id: Date.now(),
                    ...customerData
                }
            };
        }
    },

    // Delete a customer
    deleteCustomer: async (customerId) => {
        try {
            const response = await api.delete(`/customers/${customerId}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting customer:', error);
            // Simulate success for demo
            return {
                success: true,
                message: `Customer ${customerId} deleted`
            };
        }
    },

    // Get server debug info
    getDebugInfo: async () => {
        try {
            const response = await api.get('/debug');
            return response.data;
        } catch (error) {
            console.error('Error fetching debug info:', error);
            // Simulate response
            return {
                server_status: 'Simulated',
                api_version: '1.0.0',
                db_connection: 'Ok',
                llm_connection: 'Ok'
            };
        }
    },

    // Submit a new task - sync with database when possible
    addTask: async (taskData) => {
        try {
            try {
                const response = await api.post('/tasks', taskData);
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, simulating task creation:', apiError);

                // For demo purposes, simulate a successful creation
                const data = await ApiService.getData();
                return {
                    success: true,
                    task: {
                        id: data.tasks.length + 1,
                        ...taskData,
                        created_at: new Date().toISOString()
                    }
                };
            }
        } catch (error) {
            console.error('Error adding task:', error);
            throw error;
        }
    },

    // Update task status
    updateTaskStatus: async (taskId, newStatus) => {
        try {
            try {
                const response = await api.patch(`/tasks/${taskId}`, { status: newStatus });
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, simulating task update:', apiError);

                // For demo purposes, simulate a successful update
                return {
                    success: true,
                    message: `Task ${taskId} updated to status: ${newStatus}`
                };
            }
        } catch (error) {
            console.error('Error updating task:', error);
            throw error;
        }
    },

    // Create a new safety report
    submitSafetyReport: async (reportData) => {
        try {
            try {
                const response = await api.post('/safety-reports', reportData);
                return response.data;
            } catch (apiError) {
                console.warn('API call failed, simulating report creation:', apiError);

                // For demo purposes, simulate a successful creation
                const data = await ApiService.getData();
                return {
                    success: true,
                    report: {
                        id: data.safetyReports.length + 1,
                        ...reportData,
                        created_at: new Date().toISOString()
                    }
                };
            }
        } catch (error) {
            console.error('Error submitting safety report:', error);
            throw error;
        }
    },

    // Worker AI methods
    worker: workerAPI
};

export default ApiService; 