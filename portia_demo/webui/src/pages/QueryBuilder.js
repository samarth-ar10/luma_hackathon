import React, { useState } from 'react';
import { Card, Button, Form, Table, Spinner, Alert } from 'react-bootstrap';
import ApiService from '../services/api';

function QueryBuilder() {
    const [sqlQuery, setSqlQuery] = useState("SELECT * FROM employees");
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [queryHistory, setQueryHistory] = useState([]);

    const handleQueryChange = (e) => {
        setSqlQuery(e.target.value);
    };

    const handleExecuteQuery = async (e) => {
        e.preventDefault();

        // Validate query
        if (!sqlQuery.trim()) {
            setError('Please enter a SQL query');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Execute the SQL query via our API service
            // Note: We'll need to implement this endpoint in our Flask server
            const response = await ApiService.executeQuery(sqlQuery.trim());

            if (response.success) {
                // Add to history
                const timestamp = new Date().toISOString();
                setQueryHistory([
                    {
                        query: sqlQuery.trim(),
                        timestamp,
                        rowCount: response.results ? response.results.length : 0
                    },
                    ...queryHistory.slice(0, 9) // Keep last 10 queries
                ]);

                setResults(response.results || []);
            } else {
                setError(response.error || 'Error executing query');
            }
        } catch (err) {
            console.error('Error executing query:', err);
            setError('Error executing query: ' + (err.message || 'Unknown error'));
        } finally {
            setLoading(false);
        }
    };

    const loadQueryFromHistory = (query) => {
        setSqlQuery(query);
    };

    // Helper function to render result table based on query results
    const renderResultsTable = () => {
        if (!results || results.length === 0) {
            return <Alert variant="info">No results found</Alert>;
        }

        const columns = Object.keys(results[0]);

        return (
            <Table striped bordered hover responsive className="mt-4">
                <thead>
                    <tr>
                        {columns.map(column => (
                            <th key={column}>{column}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {results.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {columns.map(column => (
                                <td key={`${rowIndex}-${column}`}>{row[column]}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </Table>
        );
    };

    return (
        <div className="query-builder">
            <h1 className="mb-4">Data Explorer</h1>

            <div className="row">
                <div className="col-md-8">
                    <Card className="mb-4">
                        <Card.Header>
                            <h5>Execute SQL Query</h5>
                        </Card.Header>
                        <Card.Body>
                            <Form onSubmit={handleExecuteQuery}>
                                <Form.Group className="mb-3">
                                    <Form.Control
                                        as="textarea"
                                        rows={5}
                                        value={sqlQuery}
                                        onChange={handleQueryChange}
                                        placeholder="Enter your SQL query here..."
                                    />
                                </Form.Group>

                                {error && <Alert variant="danger">{error}</Alert>}

                                <div className="d-grid">
                                    <Button
                                        variant="primary"
                                        type="submit"
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <Spinner
                                                    as="span"
                                                    animation="border"
                                                    size="sm"
                                                    className="me-2"
                                                />
                                                Executing...
                                            </>
                                        ) : 'Execute Query'}
                                    </Button>
                                </div>
                            </Form>
                        </Card.Body>
                    </Card>

                    {/* Query Results */}
                    {results && (
                        <Card>
                            <Card.Header>
                                <h5>Query Results ({results.length} rows)</h5>
                            </Card.Header>
                            <Card.Body>
                                {renderResultsTable()}
                            </Card.Body>
                        </Card>
                    )}
                </div>

                <div className="col-md-4">
                    <Card>
                        <Card.Header>
                            <h5>Query History</h5>
                        </Card.Header>
                        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            <ul className="list-group list-group-flush">
                                {queryHistory.length === 0 ? (
                                    <li className="list-group-item text-muted">No queries yet</li>
                                ) : (
                                    queryHistory.map((item, index) => (
                                        <li key={index} className="list-group-item">
                                            <div className="d-flex w-100 justify-content-between">
                                                <small className="text-muted">
                                                    {new Date(item.timestamp).toLocaleTimeString()}
                                                </small>
                                                <small>{item.rowCount} rows</small>
                                            </div>
                                            <p className="mb-1 text-truncate">{item.query}</p>
                                            <Button
                                                variant="link"
                                                size="sm"
                                                className="p-0"
                                                onClick={() => loadQueryFromHistory(item.query)}
                                            >
                                                Use Query
                                            </Button>
                                        </li>
                                    ))
                                )}
                            </ul>
                        </div>
                    </Card>

                    <Card className="mt-4">
                        <Card.Header>
                            <h5>Example Queries</h5>
                        </Card.Header>
                        <ul className="list-group list-group-flush">
                            <li className="list-group-item">
                                <Button
                                    variant="link"
                                    className="p-0"
                                    onClick={() => setSqlQuery("SELECT * FROM employees")}
                                >
                                    SELECT * FROM employees
                                </Button>
                            </li>
                            <li className="list-group-item">
                                <Button
                                    variant="link"
                                    className="p-0"
                                    onClick={() => setSqlQuery("SELECT * FROM projects WHERE status = 'active'")}
                                >
                                    SELECT * FROM projects WHERE status = 'active'
                                </Button>
                            </li>
                            <li className="list-group-item">
                                <Button
                                    variant="link"
                                    className="p-0"
                                    onClick={() => setSqlQuery("SELECT department, SUM(budget) as total_budget FROM projects GROUP BY department")}
                                >
                                    SELECT department, SUM(budget) as total_budget FROM projects GROUP BY department
                                </Button>
                            </li>
                        </ul>
                    </Card>
                </div>
            </div>
        </div>
    );
}

export default QueryBuilder; 