// DataService.js
// Service to load and provide construction data for the React application

import { useState, useEffect } from 'react';

// Utility function to fetch JSON data
const fetchData = async (dataFile) => {
    try {
        // Use relative path that points to the correct server port
        const response = await fetch(`http://localhost:5003/data/${dataFile}`);
        if (!response.ok) {
            throw new Error(`Error fetching ${dataFile}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to load ${dataFile}:`, error);
        return [];
    }
};

// Hook to load data from JSON files
export const useConstructionData = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState({
        projects: [],
        tasks: [],
        materials: [],
        safetyReports: [],
        users: [],
        equipment: [],
        maintenanceLogs: []
    });

    useEffect(() => {
        const loadAllData = async () => {
            setLoading(true);
            try {
                console.log("Attempting to load data from JSON files...");
                const [projects, tasks, materials, safetyReports, users, equipment, maintenanceLogs] = await Promise.all([
                    fetchData('projects.json'),
                    fetchData('tasks.json'),
                    fetchData('materials.json'),
                    fetchData('safety_reports.json'),
                    fetchData('users.json'),
                    fetchData('equipment.json'),
                    fetchData('maintenance_logs.json')
                ]);

                console.log("Data loaded:", {
                    projects: projects.length,
                    tasks: tasks.length,
                    materials: materials.length,
                    safetyReports: safetyReports.length,
                    users: users.length,
                    equipment: equipment.length,
                    maintenanceLogs: maintenanceLogs.length
                });

                setData({
                    projects,
                    tasks,
                    materials,
                    safetyReports,
                    users,
                    equipment,
                    maintenanceLogs
                });
                setError(null);
            } catch (err) {
                console.error('Data loading error:', err);
                setError('Failed to load construction data: ' + err.message);
            } finally {
                setLoading(false);
            }
        };

        loadAllData();
    }, []);

    return { ...data, loading, error };
};

// Helper functions to filter and process data
export const getProjectById = (projects, id) => {
    return projects.find(project => project.id === id) || null;
};

export const getTasksByProjectId = (tasks, projectId) => {
    return tasks.filter(task => task.project_id === projectId);
};

export const getMaterialsByProjectId = (materials, projectId) => {
    return materials.filter(material => material.project_id === projectId);
};

export const getSafetyReportsByProjectId = (reports, projectId) => {
    return reports.filter(report => report.project_id === projectId);
};

export const getUserById = (users, id) => {
    return users.find(user => user.id === id) || null;
};

// Equipment related helper functions
export const getEquipmentById = (equipment, id) => {
    return equipment.find(item => item.id === id) || null;
};

export const getEquipmentByProjectId = (equipment, projectId) => {
    return equipment.filter(item => item.assigned_project === projectId);
};

export const getEquipmentByUserId = (equipment, userId) => {
    return equipment.filter(item => item.assigned_to === userId);
};

export const getMaintenanceLogsByEquipmentId = (logs, equipmentId) => {
    return logs.filter(log => log.equipment_id === equipmentId);
};

export const calculateEquipmentCost = (equipment, projectId = null) => {
    const filteredEquipment = projectId
        ? getEquipmentByProjectId(equipment, projectId)
        : equipment;

    return filteredEquipment.reduce((total, item) => {
        return total + (item.daily_cost || 0);
    }, 0);
};

export const calculateTotalMaintenanceCost = (logs, period = null) => {
    let filteredLogs = logs;

    if (period) {
        const now = new Date();
        const periodStart = new Date();

        // Set period start date based on parameter
        if (period === 'month') {
            periodStart.setMonth(now.getMonth() - 1);
        } else if (period === 'quarter') {
            periodStart.setMonth(now.getMonth() - 3);
        } else if (period === 'year') {
            periodStart.setFullYear(now.getFullYear() - 1);
        }

        // Filter logs by date
        filteredLogs = logs.filter(log => {
            const logDate = new Date(log.maintenance_date);
            return logDate >= periodStart && logDate <= now;
        });
    }

    return filteredLogs.reduce((total, log) => {
        return total + (log.cost || 0);
    }, 0);
};

export const calculateProjectCompletion = (tasks, projectId) => {
    const projectTasks = getTasksByProjectId(tasks, projectId);
    if (projectTasks.length === 0) return 0;

    const completedTasks = projectTasks.filter(task => task.status === 'Completed').length;
    return Math.round((completedTasks / projectTasks.length) * 100);
};

export const calculateMaterialCost = (materials, projectId = null) => {
    const filteredMaterials = projectId
        ? getMaterialsByProjectId(materials, projectId)
        : materials;

    return filteredMaterials.reduce((total, material) => {
        return total + (material.quantity * material.unit_price);
    }, 0);
};

// Format date for display
export const formatDate = (dateString) => {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;

    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
};

// Format currency for display
export const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
};

// Create a named export object
const DataService = {
    useConstructionData,
    getProjectById,
    getTasksByProjectId,
    getMaterialsByProjectId,
    getSafetyReportsByProjectId,
    getUserById,
    getEquipmentById,
    getEquipmentByProjectId,
    getEquipmentByUserId,
    getMaintenanceLogsByEquipmentId,
    calculateEquipmentCost,
    calculateTotalMaintenanceCost,
    calculateProjectCompletion,
    calculateMaterialCost,
    formatDate,
    formatCurrency
};

export default DataService; 