/**
 * WorkerAI service - Interface with the Worker AI backend
 */
class WorkerAI {
    constructor() {
        this.initialized = false;
        this.activeRole = null;
        this.connectionStatus = 'disconnected';
        this.messageHandlers = new Map();
        this.capabilities = {
            nlp: false,
            recommendations: false,
            visualization: false,
            autonomous: false
        };
    }

    /**
     * Initialize the Worker AI with a specific role
     * @param {string} role - The role for the Worker AI (e.g., 'worker', 'manager')
     * @returns {Promise<Object>} - Initialization status
     */
    async initialize(role = 'worker') {
        try {
            this.activeRole = role;

            // Check capabilities of the Worker AI
            const status = await this._checkStatus();

            if (status && status.status === 'active') {
                this.initialized = true;
                this.connectionStatus = 'connected';

                // Set capabilities based on status response
                if (status.capabilities) {
                    this.capabilities = status.capabilities;
                }

                console.log(`Worker AI initialized with role: ${role}`);
                console.log('Worker AI capabilities:', this.capabilities);

                return {
                    success: true,
                    message: `Worker AI initialized with role: ${role}`,
                    capabilities: this.capabilities
                };
            } else {
                this.connectionStatus = 'error';
                return {
                    success: false,
                    message: 'Could not initialize Worker AI'
                };
            }
        } catch (error) {
            console.error('Error initializing Worker AI:', error);
            this.connectionStatus = 'error';
            return {
                success: false,
                error: error.message || 'Unknown error'
            };
        }
    }

    /**
     * Check Worker AI status
     * @returns {Promise<Object>} - Status information
     * @private
     */
    async _checkStatus() {
        try {
            // For now, simulate a successful connection since we don't have a direct status endpoint
            return {
                status: 'active',
                version: '1.0',
                capabilities: {
                    nlp: true,
                    recommendations: true,
                    visualization: true,
                    autonomous: false
                }
            };

            // In the future, implement an actual endpoint call to the Worker AI status API
        } catch (error) {
            console.error('Error checking Worker AI status:', error);
            return null;
        }
    }

    /**
     * Disconnect from the Worker AI
     */
    disconnect() {
        this.initialized = false;
        this.connectionStatus = 'disconnected';
        this.messageHandlers.clear();
        console.log('Worker AI disconnected');
    }

    /**
     * Register a handler for specific message types from the Worker AI
     * @param {string} messageType - Type of message to listen for
     * @param {Function} handler - Callback function for handling the message
     */
    onMessage(messageType, handler) {
        if (typeof handler === 'function') {
            this.messageHandlers.set(messageType, handler);
        }
    }

    /**
     * Send a message to change visualization type
     * @param {string} dataType - Type of data being visualized
     * @param {string} currentVisualization - Current visualization type
     * @param {Array} data - Data being visualized
     * @returns {Promise<Object>} - Visualization recommendations
     */
    async changeVisualization(dataType, currentVisualization, data) {
        if (!this.initialized) {
            return { status: 'error', message: 'Worker AI not initialized' };
        }

        try {
            // In a real implementation, we would call the backend API
            // For now, simulate a response with visualization recommendations

            const recommendations = this._getVisualizationRecommendations(dataType, data);

            // Simulate a processing delay
            await new Promise(resolve => setTimeout(resolve, 800));

            return {
                status: 'success',
                dataType,
                recommended: recommendations.find(r => r.type !== currentVisualization) || recommendations[0],
                options: recommendations,
                implementation: this._generateImplementationCode(recommendations[0].type, dataType)
            };
        } catch (error) {
            console.error('Error changing visualization:', error);
            return {
                status: 'error',
                message: error.message || 'Error getting visualization recommendations'
            };
        }
    }

    /**
     * Generate visualization recommendations based on data type
     * @param {string} dataType - Type of data
     * @param {Array} data - The data being visualized
     * @returns {Array} - Recommendations
     * @private
     */
    _getVisualizationRecommendations(dataType, data) {
        switch (dataType) {
            case 'time_series':
                return [
                    { type: 'line', reason: 'Best for showing trends over time' },
                    { type: 'area', reason: 'Good for emphasizing magnitude of changes over time' },
                    { type: 'bar', reason: 'Useful for comparing discrete time periods' }
                ];

            case 'categorical':
                return [
                    { type: 'bar', reason: 'Best for comparing categories' },
                    { type: 'pie', reason: 'Good for showing proportion of the whole' },
                    { type: 'line', reason: 'Can show trends across categories if they have an order' }
                ];

            case 'multi_series':
                return [
                    { type: 'line', reason: 'Best for comparing multiple trends over time' },
                    { type: 'bar', reason: 'Good for comparing values across categories and series' },
                    { type: 'area', reason: 'Useful for showing cumulative values' }
                ];

            default:
                return [
                    { type: 'bar', reason: 'General purpose visualization' },
                    { type: 'line', reason: 'Alternative visualization' }
                ];
        }
    }

    /**
     * Generate sample implementation code for a visualization
     * @param {string} vizType - Visualization type
     * @param {string} dataType - Data type
     * @returns {string} - Sample implementation code
     * @private
     */
    _generateImplementationCode(vizType, dataType) {
        const dataKeyMapping = {
            time_series: "date",
            categorical: "category",
            multi_series: "date"
        };

        const xAxisKey = dataKeyMapping[dataType] || "category";

        const code = `
// React component for ${vizType} chart with ${dataType} data
import React from 'react';
import { ${vizType.charAt(0).toUpperCase() + vizType.slice(1)}Chart, ${vizType === 'pie' ? 'Pie' : vizType.charAt(0).toUpperCase() + vizType.slice(1)}, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function DataVisualization({ data }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <${vizType.charAt(0).toUpperCase() + vizType.slice(1)}Chart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        ${vizType !== 'pie' ? '<CartesianGrid strokeDasharray="3 3" />' : ''}
        ${vizType !== 'pie' ? `<XAxis dataKey="${xAxisKey}" />` : ''}
        ${vizType !== 'pie' ? '<YAxis />' : ''}
        <Tooltip />
        <Legend />
        ${vizType === 'pie' ?
                `<Pie data={data} dataKey="value" nameKey="${xAxisKey}" cx="50%" cy="50%" outerRadius={150} fill="#8884d8" label />` :
                dataType === 'multi_series' ?
                    '<Line type="monotone" dataKey="actual" stroke="#8884d8" />\n        <Line type="monotone" dataKey="planned" stroke="#82ca9d" />' :
                    `<${vizType.charAt(0).toUpperCase() + vizType.slice(1)} type="monotone" dataKey="value" stroke="#8884d8" ${vizType === 'area' ? 'fill="#8884d8"' : 'fill="#8884d8"'} />`
            }
      </${vizType.charAt(0).toUpperCase() + vizType.slice(1)}Chart>
    </ResponsiveContainer>
  );
}

export default DataVisualization;`;

        return code;
    }
}

// Export as singleton
const workerAI = new WorkerAI();
export default workerAI; 