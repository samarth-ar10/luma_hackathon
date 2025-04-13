import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Form, InputGroup, Spinner, Alert, Row, Col, Container, Tab, Tabs } from 'react-bootstrap';
import ApiService from '../services/api';
import workerAI from '../services/WorkerAI';
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

function AIVisualizer({ role }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState([]);
    const [visualizationType, setVisualizationType] = useState('bar');
    const [dataType, setDataType] = useState('time_series');
    const [userRequest, setUserRequest] = useState('');
    const [aiResponse, setAIResponse] = useState(null);
    const [implementationCode, setImplementationCode] = useState('');
    const [connected, setConnected] = useState(false);
    const [visualizationOptions, setVisualizationOptions] = useState([]);
    const chartContainerRef = useRef(null);

    // Sample datasets for demonstration
    const datasets = {
        time_series: [
            { date: '2023-01', value: 240 },
            { date: '2023-02', value: 300 },
            { date: '2023-03', value: 280 },
            { date: '2023-04', value: 350 },
            { date: '2023-05', value: 410 },
            { date: '2023-06', value: 390 },
            { date: '2023-07', value: 450 },
            { date: '2023-08', value: 480 },
            { date: '2023-09', value: 420 },
            { date: '2023-10', value: 510 },
            { date: '2023-11', value: 530 },
            { date: '2023-12', value: 580 }
        ],
        categorical: [
            { category: 'Equipment', value: 35 },
            { category: 'Materials', value: 45 },
            { category: 'Labor', value: 55 },
            { category: 'Permits', value: 15 },
            { category: 'Other', value: 10 }
        ],
        multi_series: [
            { date: '2023-01', actual: 240, planned: 250 },
            { date: '2023-02', actual: 300, planned: 290 },
            { date: '2023-03', actual: 280, planned: 320 },
            { date: '2023-04', actual: 350, planned: 340 },
            { date: '2023-05', actual: 410, planned: 390 },
            { date: '2023-06', actual: 390, planned: 400 }
        ]
    };

    // Connect to the Queen AI when the component mounts
    useEffect(() => {
        const initializeWorker = async () => {
            try {
                setLoading(true);
                const result = await workerAI.initialize(role);

                if (result.success) {
                    setConnected(true);
                    setError(null);
                    console.log("Worker AI successfully connected with role:", role);

                    // Listen for visualization change recommendations from the Queen
                    workerAI.onMessage('visualization_recommendation', handleVisualizationRecommendation);
                } else {
                    setError("Failed to connect Worker AI to Queen AI");
                }
            } catch (err) {
                console.error("Error initializing Worker AI:", err);
                setError("Error connecting to the AI system");
            } finally {
                setLoading(false);
            }
        };

        initializeWorker();

        // Clean up when component unmounts
        return () => {
            workerAI.disconnect();
        };
    }, [role]);

    // Load initial data based on selected data type
    useEffect(() => {
        setData(datasets[dataType] || []);
    }, [dataType]);

    // Handle visualization recommendation messages
    const handleVisualizationRecommendation = (message) => {
        if (message && message.recommendations) {
            setVisualizationOptions(message.recommendations);

            // Auto-apply the top recommendation if specified
            if (message.auto_apply && message.recommendations.length > 0) {
                setVisualizationType(message.recommendations[0].type);
            }
        }
    };

    // Handle visualization request
    const handleVisualizationRequest = async () => {
        if (!userRequest) return;

        try {
            setLoading(true);
            setError(null);

            // Get visualization options from the Worker AI
            const result = await workerAI.changeVisualization(
                dataType,
                visualizationType,
                data,
                userRequest // Pass the user's text prompt to the AI
            );

            if (result.status === 'error') {
                setError(result.message);
                return;
            }

            // Update visualization options
            if (result.options) {
                setVisualizationOptions(result.options);
            }

            // Set recommended visualization type if available
            if (result.recommended && result.recommended.type) {
                setVisualizationType(result.recommended.type);
            }

            // Store implementation details and AI response
            if (result.implementation) {
                setImplementationCode(result.implementation);

                // Extract code block from implementation if it exists
                const codeBlockMatch = result.implementation.match(/```.*?\n([\s\S]*?)```/);
                if (codeBlockMatch && codeBlockMatch[1]) {
                    setImplementationCode(codeBlockMatch[1]);
                }
            }

            // Store the complete AI response
            setAIResponse({
                ...result,
                message: result.message
            });

            // Clear the user request input after processing
            setUserRequest('');
        } catch (err) {
            console.error("Error processing visualization request:", err);
            setError("Error processing your request. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // Change dataset type
    const handleDataTypeChange = (e) => {
        const newDataType = e.target.value;
        setDataType(newDataType);
        setData(datasets[newDataType] || []);

        // Reset visualization type based on data type
        switch (newDataType) {
            case 'time_series':
                setVisualizationType('line');
                break;
            case 'categorical':
                setVisualizationType('pie');
                break;
            case 'multi_series':
                setVisualizationType('bar');
                break;
            default:
                setVisualizationType('bar');
        }
    };

    // Render the appropriate chart based on visualization type
    const renderChart = () => {
        if (!data || data.length === 0) {
            return <div className="text-center p-5">No data available</div>;
        }

        switch (visualizationType) {
            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={dataType === 'time_series' ? 'date' : 'category'} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {dataType === 'multi_series' ? (
                                <>
                                    <Line type="monotone" dataKey="actual" stroke="#8884d8" />
                                    <Line type="monotone" dataKey="planned" stroke="#82ca9d" />
                                </>
                            ) : (
                                <Line type="monotone" dataKey="value" stroke="#8884d8" />
                            )}
                        </LineChart>
                    </ResponsiveContainer>
                );

            case 'bar':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={dataType === 'time_series' ? 'date' : 'category'} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {dataType === 'multi_series' ? (
                                <>
                                    <Bar dataKey="actual" fill="#8884d8" />
                                    <Bar dataKey="planned" fill="#82ca9d" />
                                </>
                            ) : (
                                <Bar dataKey="value" fill="#8884d8" />
                            )}
                        </BarChart>
                    </ResponsiveContainer>
                );

            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <PieChart>
                            <Pie
                                data={data}
                                dataKey="value"
                                nameKey={dataType === 'time_series' ? 'date' : 'category'}
                                cx="50%"
                                cy="50%"
                                outerRadius={150}
                                fill="#8884d8"
                                label
                            />
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );

            case 'area':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={dataType === 'time_series' ? 'date' : 'category'} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {dataType === 'multi_series' ? (
                                <>
                                    <Area type="monotone" dataKey="actual" stackId="1" stroke="#8884d8" fill="#8884d8" />
                                    <Area type="monotone" dataKey="planned" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
                                </>
                            ) : (
                                <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" />
                            )}
                        </AreaChart>
                    </ResponsiveContainer>
                );

            default:
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={dataType === 'time_series' ? 'date' : 'category'} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="value" fill="#8884d8" />
                        </BarChart>
                    </ResponsiveContainer>
                );
        }
    };

    return (
        <div className="ai-visualizer">
            <h1 className="mb-4">AI-Powered Data Visualization</h1>

            {loading && (
                <div className="text-center my-4">
                    <Spinner animation="border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </Spinner>
                    <p className="mt-2">Processing your request...</p>
                </div>
            )}

            {error && (
                <Alert variant="danger" className="my-3">
                    {error}
                </Alert>
            )}

            {connected && (
                <Alert variant="success" className="my-3">
                    Connected to Queen AI with role: {role}
                </Alert>
            )}

            <Row className="mb-4">
                <Col md={8}>
                    <Card>
                        <Card.Header>
                            <h5>Data Visualization</h5>
                        </Card.Header>
                        <Card.Body>
                            <div ref={chartContainerRef} className="chart-container mb-3">
                                {renderChart()}
                            </div>

                            <Row className="mt-4 mb-3">
                                <Col md={4}>
                                    <Form.Group>
                                        <Form.Label>Data Type</Form.Label>
                                        <Form.Select
                                            value={dataType}
                                            onChange={handleDataTypeChange}
                                        >
                                            <option value="time_series">Time Series</option>
                                            <option value="categorical">Categorical</option>
                                            <option value="multi_series">Multi-Series Time Data</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Form.Group>
                                        <Form.Label>Visualization Type</Form.Label>
                                        <Form.Select
                                            value={visualizationType}
                                            onChange={(e) => setVisualizationType(e.target.value)}
                                        >
                                            <option value="bar">Bar Chart</option>
                                            <option value="line">Line Chart</option>
                                            <option value="pie">Pie Chart</option>
                                            <option value="area">Area Chart</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                                <Col md={4} className="d-flex align-items-end">
                                    <Button
                                        variant="primary"
                                        className="w-100"
                                        onClick={() => {
                                            const nextType = visualizationType === 'bar' ? 'line' :
                                                visualizationType === 'line' ? 'pie' :
                                                    visualizationType === 'pie' ? 'area' : 'bar';
                                            setVisualizationType(nextType);
                                        }}
                                    >
                                        Cycle Visualization Type
                                    </Button>
                                </Col>
                            </Row>

                            <div className="mt-3">
                                <Form.Label>Ask the AI to change the visualization</Form.Label>
                                <InputGroup className="mb-3">
                                    <Form.Control
                                        placeholder="e.g., 'Show me this data as a line chart' or 'What's the best way to visualize this trend?'"
                                        value={userRequest}
                                        onChange={(e) => setUserRequest(e.target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter') {
                                                handleVisualizationRequest();
                                            }
                                        }}
                                    />
                                    <Button
                                        variant="primary"
                                        onClick={handleVisualizationRequest}
                                        disabled={loading || !userRequest}
                                    >
                                        Submit
                                    </Button>
                                </InputGroup>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={4}>
                    <Card className="mb-4">
                        <Card.Header>
                            <h5>AI Response</h5>
                        </Card.Header>
                        <Card.Body>
                            {aiResponse ? (
                                <div>
                                    {aiResponse.message && (
                                        <div className="mb-3">
                                            <h6>AI Suggestion:</h6>
                                            <p>{aiResponse.message}</p>
                                        </div>
                                    )}

                                    {aiResponse.recommended && (
                                        <div className="mb-3">
                                            <h6>Recommended Visualization:</h6>
                                            <Badge bg="primary" className="me-2">{aiResponse.recommended.type}</Badge>
                                            <p className="mt-2">{aiResponse.recommended.reason}</p>
                                        </div>
                                    )}

                                    {aiResponse.options && aiResponse.options.length > 0 && (
                                        <div className="mb-3">
                                            <h6>Available Visualization Types:</h6>
                                            <div className="d-flex flex-wrap gap-2">
                                                {aiResponse.options.map((option, index) => (
                                                    <Button
                                                        key={index}
                                                        variant={visualizationType === option.type ? "primary" : "outline-primary"}
                                                        size="sm"
                                                        onClick={() => setVisualizationType(option.type)}
                                                    >
                                                        {option.type}
                                                    </Button>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p className="text-muted">
                                    Ask the AI to help you visualize your data differently.
                                    Try questions like "What's the best way to show this data?" or
                                    "Show me this as a pie chart instead."
                                </p>
                            )}
                        </Card.Body>
                    </Card>

                    {implementationCode && (
                        <Card>
                            <Card.Header>
                                <h5>Implementation Code</h5>
                            </Card.Header>
                            <Card.Body>
                                <div className="code-block">
                                    <pre className="bg-light p-3 rounded">
                                        <code>{implementationCode}</code>
                                    </pre>
                                </div>
                            </Card.Body>
                        </Card>
                    )}
                </Col>
            </Row>
        </div>
    );
}

// Missing Badge import
const Badge = ({ bg, className, children }) => (
    <span className={`badge bg-${bg} ${className || ''}`}>{children}</span>
);

export default AIVisualizer; 