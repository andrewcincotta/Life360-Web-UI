// App.tsx - Main application component

import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import Auth from './components/Auth';
import MapView from './components/MapView';
import './App.css';

function App() {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('life360_token');
    if (storedToken) {
      setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  const handleAuthenticated = (newToken: string) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('life360_token');
    setToken(null);
  };

  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="App">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      {!token ? (
        <Auth onAuthenticated={handleAuthenticated} />
      ) : (
        <MapView token={token} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;