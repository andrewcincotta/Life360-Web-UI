// Auth.tsx - Authentication component

import React, { useState } from 'react';
import toast from 'react-hot-toast';
import Life360Api from '../api';
import './Auth.css';

interface AuthProps {
  onAuthenticated: (token: string) => void;
}

const Auth: React.FC<AuthProps> = ({ onAuthenticated }) => {
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!token.trim()) {
      toast.error('Please enter a token');
      return;
    }

    setLoading(true);
    const api = new Life360Api();
    
    try {
      const isValid = await api.validateToken(token);
      
      if (isValid) {
        localStorage.setItem('life360_token', token);
        toast.success('Authentication successful!');
        onAuthenticated(token);
      } else {
        toast.error('Invalid token');
      }
    } catch (error) {
      toast.error('Failed to validate token');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Life360 Map Tracker</h1>
        <p className="auth-subtitle">
          Enter your Life360 Bearer token to view member locations
        </p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="token" className="form-label">
              Bearer Token
            </label>
            <input
              id="token"
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Enter your Life360 token"
              className="form-input"
              disabled={loading}
            />
            <p className="form-hint">
              Your token should start with "Bearer " followed by the actual token
            </p>
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading ? 'Validating...' : 'Connect'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p className="auth-note">
            <strong>Note:</strong> Your token is stored locally and never sent to any server except Life360.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Auth;