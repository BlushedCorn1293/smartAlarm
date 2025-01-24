import React, { createContext, useState, useContext } from 'react';

const ApiContext = createContext();

export const ApiProvider = ({ children }) => {
    const [apiUrl, setApiUrl] = useState('');

    return (
        <ApiContext.Provider value={{ apiUrl, setApiUrl }}>
            {children}
        </ApiContext.Provider>
    );
};

// Export ApiProvider as the default export
export default ApiProvider;

export const useApi = () => {
    const context = useContext(ApiContext);

    // Throw an error if useApi is called outside of ApiProvider
    if (!context) {
        throw new Error('useApi must be used within an ApiProvider');
    }

    return context;
};
