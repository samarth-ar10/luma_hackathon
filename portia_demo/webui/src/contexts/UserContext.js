import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

// Create the context
const UserContext = createContext();

// Custom hook to use the user context
export const useUserContext = () => useContext(UserContext);

// Worker AI context
export const WorkerAIContext = createContext();
export const useWorkerAI = () => useContext(WorkerAIContext);

// Provider component
export const UserProvider = ({ children }) => {
    // User state
    const [user, setUser] = useState(null);

    // Worker AI states
    const [aiResponse, setAiResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [availableRoles, setAvailableRoles] = useState([]);

    // Initialize user on component mount
    useEffect(() => {
        // Check for existing user ID in localStorage
        const storedUserId = localStorage.getItem('user_id');

        if (storedUserId) {
            setUser({
                id: storedUserId,
                // Other user details could be loaded here
            });
        } else {
            // Create a new user ID if none exists
            const newUserId = uuidv4();
            localStorage.setItem('user_id', newUserId);
            setUser({
                id: newUserId,
                // Set default properties
            });
        }

        // Fetch available worker AI roles
        fetchAvailableRoles();
    }, []);

    // Fetch available roles from API
    const fetchAvailableRoles = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5003'}/api/worker/roles`);
            if (response.ok) {
                const data = await response.json();
                setAvailableRoles(data.roles || []);
            } else {
                // Fallback roles if API fails
                setAvailableRoles(['ceo', 'project-manager', 'safety-officer', 'equipment-manager', 'worker']);
            }
        } catch (error) {
            console.error('Error fetching worker AI roles:', error);
            // Fallback roles if API fails
            setAvailableRoles(['ceo', 'project-manager', 'safety-officer', 'equipment-manager', 'worker']);
        }
    };

    // Send message to Worker AI
    const sendMessage = async (role, message, context = {}) => {
        if (!message.trim() || !role) return null;

        // Ensure we have a user ID
        const userId = user?.id || localStorage.getItem('user_id');
        if (!userId) return null;

        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5003'}/api/worker/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    role,
                    message,
                    context
                }),
            });

            const data = await response.json();
            setAiResponse(data.message || 'Sorry, I could not process your request.');
            return data;
        } catch (error) {
            console.error('Error sending message to Worker AI:', error);
            const errorMessage = 'Sorry, there was an error communicating with the AI assistant.';
            setAiResponse(errorMessage);
            return { message: errorMessage, error: true };
        } finally {
            setLoading(false);
        }
    };

    // Clear AI response
    const clearAiResponse = () => {
        setAiResponse(null);
    };

    // Update user role
    const updateUserRole = (role) => {
        setUser(currentUser => ({
            ...currentUser,
            role
        }));
    };

    // Combined context values
    const userContextValue = {
        user,
        setUser,
        updateUserRole
    };

    const workerAIContextValue = {
        aiResponse,
        loading,
        availableRoles,
        sendMessage,
        clearAiResponse
    };

    return (
        <UserContext.Provider value={userContextValue}>
            <WorkerAIContext.Provider value={workerAIContextValue}>
                {children}
            </WorkerAIContext.Provider>
        </UserContext.Provider>
    );
};

export default UserContext; 