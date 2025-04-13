import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Form, Button, Card, Spinner, Badge, Dropdown } from 'react-bootstrap';
import ApiService from '../services/api';
import { useUserContext } from '../contexts/UserContext';
import { v4 as uuidv4 } from 'uuid';

function AIAssistant() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [conversationHistory, setConversationHistory] = useState([]);
    const [historyLoaded, setHistoryLoaded] = useState(false);
    const [availableRoles, setAvailableRoles] = useState([]);
    const [selectedRole, setSelectedRole] = useState('');
    const { user } = useUserContext();
    const messagesEndRef = useRef(null);

    // Get user ID
    const getUserId = () => {
        return user?.id || localStorage.getItem('user_id') || uuidv4();
    };

    // Load available roles
    useEffect(() => {
        async function loadRoles() {
            try {
                const roles = await ApiService.worker.getAvailableRoles();
                setAvailableRoles(roles);

                // Set default role based on user context or first available role
                const defaultRole = user?.role || roles[0] || 'worker';
                setSelectedRole(defaultRole);
            } catch (error) {
                console.error('Error loading roles:', error);
                // Set fallback roles
                setAvailableRoles(['ceo', 'project-manager', 'safety-officer', 'equipment-manager', 'worker']);
                setSelectedRole(user?.role || 'worker');
            }
        }

        loadRoles();
    }, [user]);

    // On load or role change, get conversation history
    useEffect(() => {
        async function loadHistory() {
            if (!selectedRole || historyLoaded) return;

            const userId = getUserId();
            if (!userId) return;

            try {
                const history = await ApiService.worker.getConversationHistory(userId, selectedRole);
                if (history && history.length > 0) {
                    // Convert history to message format
                    const historyMessages = history.map(item => [
                        { type: 'user', text: item.user_message, timestamp: item.timestamp },
                        { type: 'ai', text: item.ai_response, timestamp: item.timestamp }
                    ]).flat();

                    setMessages(historyMessages);
                    setConversationHistory(history);
                } else {
                    // Add welcome message if no history
                    setMessages([{
                        type: 'ai',
                        text: `Welcome to the ${selectedRole.toUpperCase()} Assistant! I can help you with tasks specific to your role. How can I assist you today?`,
                        timestamp: new Date().toISOString()
                    }]);
                }
                setHistoryLoaded(true);
            } catch (error) {
                console.error('Error loading conversation history:', error);
                // Fallback welcome message
                setMessages([{
                    type: 'ai',
                    text: `Welcome to the ${selectedRole.toUpperCase()} Assistant! I can help you with tasks specific to your role. How can I assist you today?`,
                    timestamp: new Date().toISOString()
                }]);
                setHistoryLoaded(true);
            }
        }

        loadHistory();
    }, [selectedRole, historyLoaded]);

    // Reset history loaded state when role changes
    useEffect(() => {
        setHistoryLoaded(false);
    }, [selectedRole]);

    // Scroll to the bottom of the messages
    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    // Handle role change
    const handleRoleChange = (role) => {
        setSelectedRole(role);
        setMessages([]);
        setConversationHistory([]);
        setHistoryLoaded(false);
    };

    // Send query to the AI
    const sendQuery = async (e) => {
        e.preventDefault();

        if (!query.trim() || !selectedRole) return;

        // Create/get user ID
        const userId = getUserId();
        if (!user?.id && !localStorage.getItem('user_id')) {
            localStorage.setItem('user_id', userId);
        }

        // Add user message to the chat
        const userMessage = {
            type: 'user',
            text: query,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setQuery('');
        setLoading(true);

        try {
            // Send the query to the Worker AI for the selected role
            const response = await ApiService.worker.sendMessage(
                userId,
                selectedRole,
                query,
                { source: 'ai_assistant' }
            );

            // Process the response
            const aiMessage = {
                type: 'ai',
                text: response.message || "I'm sorry, I couldn't process your request.",
                timestamp: new Date().toISOString(),
                data: response.data || null,
                visualization: response.visualization || null,
                recommendations: response.recommendations || null
            };

            setMessages(prev => [...prev, aiMessage]);

        } catch (error) {
            console.error('Error sending query to AI:', error);
            // Add error message
            setMessages(prev => [...prev, {
                type: 'ai',
                text: "Sorry, I encountered an error processing your request. Please try again later.",
                timestamp: new Date().toISOString(),
                error: true
            }]);
        } finally {
            setLoading(false);
        }
    };

    // Format a message for display
    const formatMessage = (message, index) => {
        if (message.type === 'user') {
            return (
                <div className="chat-message user-message" key={`${message.timestamp}-${index}`}>
                    <div className="message-content">
                        <strong>You:</strong> {message.text}
                    </div>
                    <div className="message-time">
                        {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            );
        } else {
            // AI message with possible extra components
            return (
                <div className={`chat-message ai-message ${message.error ? 'error' : ''}`} key={`${message.timestamp}-${index}`}>
                    <div className="message-content">
                        <strong>{selectedRole.toUpperCase()} AI Assistant:</strong> {message.text}

                        {/* Display data if available */}
                        {message.data && message.data.length > 0 && (
                            <div className="data-preview">
                                <h6>Data Preview:</h6>
                                <div className="data-table-container">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                {Object.keys(message.data[0]).map(key => (
                                                    <th key={key}>{key}</th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {message.data.slice(0, 5).map((item, idx) => (
                                                <tr key={idx}>
                                                    {Object.values(item).map((val, i) => (
                                                        <td key={i}>{String(val)}</td>
                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {/* Display visualization recommendation if available */}
                        {message.visualization && (
                            <div className="visualization-recommendation">
                                <h6>Visualization Recommendation:</h6>
                                <p>
                                    Recommended: <strong>{message.visualization.recommended}</strong>
                                </p>
                                <p>
                                    Alternatives: {message.visualization.alternatives.join(', ')}
                                </p>
                            </div>
                        )}

                        {/* Display recommendations if available */}
                        {message.recommendations && message.recommendations.length > 0 && (
                            <div className="recommendations">
                                <h6>Recommendations:</h6>
                                <ul>
                                    {message.recommendations.map((rec, idx) => (
                                        <li key={idx}>{rec}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                    <div className="message-time">
                        {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            );
        }
    };

    return (
        <Container fluid className="p-4">
            <Row>
                <Col lg={12}>
                    <Card className="mb-4">
                        <Card.Header className="d-flex justify-content-between align-items-center">
                            <div>
                                <h3>AI Assistant</h3>
                                <p className="text-muted mb-0">
                                    Talk with a role-specific AI assistant for personalized help
                                </p>
                            </div>
                            <div>
                                <Dropdown>
                                    <Dropdown.Toggle variant="outline-primary" id="dropdown-role">
                                        {selectedRole ? `${selectedRole.toUpperCase()} Assistant` : "Select Role"}
                                    </Dropdown.Toggle>
                                    <Dropdown.Menu>
                                        {availableRoles.map(role => (
                                            <Dropdown.Item
                                                key={role}
                                                active={selectedRole === role}
                                                onClick={() => handleRoleChange(role)}
                                            >
                                                {role.toUpperCase()} Assistant
                                            </Dropdown.Item>
                                        ))}
                                    </Dropdown.Menu>
                                </Dropdown>
                            </div>
                        </Card.Header>
                        <Card.Body className="chat-container">
                            <div className="messages">
                                {messages.map((message, index) => formatMessage(message, index))}
                                <div ref={messagesEndRef} />

                                {loading && (
                                    <div className="chat-message ai-message loading">
                                        <div className="message-content">
                                            <strong>{selectedRole.toUpperCase()} AI Assistant:</strong> <Spinner animation="border" size="sm" /> Thinking...
                                        </div>
                                    </div>
                                )}
                            </div>
                        </Card.Body>
                        <Card.Footer>
                            <Form onSubmit={sendQuery}>
                                <Form.Group className="d-flex">
                                    <Form.Control
                                        type="text"
                                        placeholder={`Ask the ${selectedRole ? selectedRole.toUpperCase() : "AI"} Assistant anything...`}
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        disabled={loading || !selectedRole}
                                    />
                                    <Button
                                        variant="primary"
                                        className="ms-2"
                                        type="submit"
                                        disabled={loading || !query.trim() || !selectedRole}
                                    >
                                        {loading ? <Spinner animation="border" size="sm" /> : 'Send'}
                                    </Button>
                                </Form.Group>
                            </Form>
                        </Card.Footer>
                    </Card>
                </Col>
            </Row>

            <style>{`
                .chat-container {
                    height: calc(100vh - 300px);
                    overflow-y: auto;
                    padding: 1rem;
                }
                
                .messages {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .chat-message {
                    padding: 1rem;
                    border-radius: 0.5rem;
                    max-width: 80%;
                }
                
                .user-message {
                    background-color: #f0f0f0;
                    align-self: flex-end;
                    margin-left: auto;
                }
                
                .ai-message {
                    background-color: #e3f2fd;
                    align-self: flex-start;
                    margin-right: auto;
                }
                
                .ai-message.error {
                    background-color: #ffebee;
                }
                
                .ai-message.loading {
                    background-color: #e8eaf6;
                    opacity: 0.8;
                }
                
                .message-time {
                    font-size: 0.8rem;
                    color: #757575;
                    text-align: right;
                    margin-top: 0.5rem;
                }
                
                .data-preview {
                    margin-top: 1rem;
                    background-color: rgba(255, 255, 255, 0.7);
                    padding: 0.5rem;
                    border-radius: 0.25rem;
                }
                
                .data-table-container {
                    overflow-x: auto;
                }
                
                .data-table {
                    width: 100%;
                    font-size: 0.8rem;
                    border-collapse: collapse;
                }
                
                .data-table th, .data-table td {
                    padding: 0.25rem 0.5rem;
                    border: 1px solid #ddd;
                }
                
                .data-table th {
                    background-color: #f5f5f5;
                }
                
                .visualization-recommendation, .recommendations {
                    margin-top: 1rem;
                    background-color: rgba(255, 255, 255, 0.7);
                    padding: 0.5rem;
                    border-radius: 0.25rem;
                }
            `}</style>
        </Container>
    );
}

export default AIAssistant; 