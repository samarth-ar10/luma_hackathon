import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

// Create context
const UserContext = createContext();

// Custom hook to use the context
export const useUserContext = () => useContext(UserContext);

// Provider component
export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Load user from localStorage or create a new one
        const loadUser = () => {
            try {
                const savedUser = localStorage.getItem('user');

                if (savedUser) {
                    setUser(JSON.parse(savedUser));
                } else {
                    // Create a new user with UUID
                    const newUser = {
                        id: uuidv4(),
                        role: 'worker', // Default role
                        preferences: {
                            theme: 'light',
                            dashboardLayout: 'grid',
                        },
                        created: new Date().toISOString()
                    };

                    localStorage.setItem('user', JSON.stringify(newUser));
                    setUser(newUser);
                }
            } catch (error) {
                console.error('Error loading user:', error);
                // Create a fallback user if there's an error
                const fallbackUser = { id: uuidv4(), role: 'worker' };
                setUser(fallbackUser);
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, []);

    // Update user information and save to localStorage
    const updateUser = (updates) => {
        const updatedUser = { ...user, ...updates };
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
    };

    // Change user role
    const changeRole = (role) => {
        updateUser({ role });
    };

    // Logout user
    const logout = () => {
        localStorage.removeItem('user');
        setUser(null);
    };

    // Context value
    const value = {
        user,
        loading,
        updateUser,
        changeRole,
        logout
    };

    return (
        <UserContext.Provider value={value}>
            {children}
        </UserContext.Provider>
    );
};

export default UserContext; 