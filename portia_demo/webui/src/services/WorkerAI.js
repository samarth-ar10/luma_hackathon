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
        this.apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5003';
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
     * Send a message to change visualization type using AI
     * @param {string} dataType - Type of data being visualized
     * @param {string} currentVisualization - Current visualization type
     * @param {Array} data - Data being visualized
     * @param {string} userPrompt - User's request for visualization change
     * @returns {Promise<Object>} - Visualization recommendations
     */
    async changeVisualization(dataType, currentVisualization, data, userPrompt = '') {
        if (!this.initialized) {
            return { status: 'error', message: 'Worker AI not initialized' };
        }

        try {
            // Use the actual API if there's a user prompt, otherwise use local recommendations
            if (userPrompt) {
                // Make an actual API call to the backend
                const response = await fetch(`${this.apiUrl}/api/worker/message`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: 'visualization_user',  // Could be replaced with actual user ID
                        role: this.activeRole,
                        message: userPrompt,
                        context: {
                            current_visualization: currentVisualization,
                            data_type: dataType,
                            data_sample: data.slice(0, 5), // Send sample of data to keep payload small
                            visualization_request: true
                        }
                    }),
                });

                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }

                const result = await response.json();

                // Process the AI response
                if (result.error) {
                    return {
                        status: 'error',
                        message: result.message || 'Error processing visualization request'
                    };
                }

                // Parse the visualization recommendations from the AI response
                const visualizationData = this._extractVisualizationRecommendation(result.message, result.visualization);

                // Combine with some default options if AI didn't provide enough
                let options = visualizationData.options;
                if (!options || options.length < 2) {
                    const defaultOptions = this._getVisualizationRecommendations(dataType, data);
                    options = [...(options || []), ...defaultOptions.filter(o =>
                        !options || !options.some(rec => rec.type === o.type)
                    )];
                }

                return {
                    status: 'success',
                    dataType,
                    message: visualizationData.message || result.message,
                    recommended: visualizationData.recommended || options[0],
                    options: options,
                    implementation: visualizationData.code || this._generateImplementationCode(
                        visualizationData.recommended?.type || options[0].type,
                        dataType
                    )
                };
            } else {
                // Use local recommendations if no user prompt provided
                const recommendations = this._getVisualizationRecommendations(dataType, data);

                return {
                    status: 'success',
                    dataType,
                    recommended: recommendations.find(r => r.type !== currentVisualization) || recommendations[0],
                    options: recommendations,
                    implementation: this._generateImplementationCode(recommendations[0].type, dataType)
                };
            }
        } catch (error) {
            console.error('Error changing visualization:', error);
            return {
                status: 'error',
                message: error.message || 'Error getting visualization recommendations'
            };
        }
    }

    /**
     * Extract visualization recommendations from AI response
     * @param {string} message - The AI message response
     * @param {string} visualizationCode - Code block extracted from the response
     * @returns {Object} - Parsed visualization recommendations
     * @private
     */
    _extractVisualizationRecommendation(message, visualizationCode) {
        const result = {
            message: message,
            code: visualizationCode,
            options: []
        };

        // Try to identify the recommended visualization types from the message
        const vizTypes = ['bar', 'line', 'pie', 'area', 'scatter'];

        // Extract visualization options and recommendations
        vizTypes.forEach(type => {
            // Look for phrases indicating recommendations for each chart type
            const typeRegexes = [
                // Direct recommendation
                new RegExp(`\\b${type}\\s+(chart|graph|visualization)\\s+is\\s+(best|recommended|ideal|suitable)\\b`, 'i'),
                // Phrase mentioning benefits
                new RegExp(`\\b${type}\\s+(chart|graph|visualization)\\s+(would|could|can|will)\\s+(work|be good|be best|show)\\b`, 'i'),
                // Any mention of the chart type
                new RegExp(`\\b${type}\\s+(chart|graph|visualization)\\b`, 'i'),
            ];

            // Check all regex patterns
            for (const regex of typeRegexes) {
                if (regex.test(message)) {
                    // Extract a reason if available (look for sentence containing the chart type)
                    const sentenceRegex = new RegExp(`[^.!?]*\\b${type}\\s+(chart|graph|visualization)\\b[^.!?]*[.!?]`, 'i');
                    const sentenceMatch = message.match(sentenceRegex);
                    const reason = sentenceMatch ? sentenceMatch[0].trim() : `${type.charAt(0).toUpperCase() + type.slice(1)} chart recommended by AI`;

                    result.options.push({
                        type: type,
                        reason: reason
                    });

                    // Use the first match as the recommended option
                    if (!result.recommended) {
                        result.recommended = {
                            type: type,
                            reason: reason
                        };
                    }

                    break; // Once we've found a match with this type, move to the next type
                }
            }
        });

        // If we can extract a chart type from the code
        if (visualizationCode) {
            vizTypes.forEach(type => {
                const chartClassRegex = new RegExp(`<\\s*${type.charAt(0).toUpperCase() + type.slice(1)}Chart`, 'i');
                if (chartClassRegex.test(visualizationCode) && !result.options.some(opt => opt.type === type)) {
                    result.options.push({
                        type: type,
                        reason: `${type.charAt(0).toUpperCase() + type.slice(1)} chart from implementation code`
                    });

                    // If no recommendation found in text, use the one from code
                    if (!result.recommended) {
                        result.recommended = {
                            type: type,
                            reason: `${type.charAt(0).toUpperCase() + type.slice(1)} chart from implementation code`
                        };
                    }
                }
            });
        }

        return result;
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