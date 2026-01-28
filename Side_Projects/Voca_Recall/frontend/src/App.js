import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import Databases from './pages/Databases';
import Services from './pages/Services';
import Settings from './pages/Settings';
import ManageTokens from './pages/ManageTokens';
import ManageUsers from './pages/ManageUsers';
import EmailLogs from './pages/EmailLogs';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 relative">
      {isAuthenticated && <Navbar />}
      <main className={isAuthenticated ? 'pt-16 relative' : 'relative'}>
        <Routes>
          <Route 
            path="/login" 
            element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} 
          />
          <Route 
            path="/register" 
            element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />} 
          />
          <Route 
            path="/forgot-password" 
            element={isAuthenticated ? <Navigate to="/dashboard" /> : <ForgotPassword />} 
          />
          <Route 
            path="/reset-password" 
            element={isAuthenticated ? <Navigate to="/dashboard" /> : <ResetPassword />} 
          />
          <Route 
            path="/dashboard" 
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/databases" 
            element={isAuthenticated ? <Databases /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/services" 
            element={isAuthenticated ? <Services /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/settings" 
            element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/settings/tokens" 
            element={isAuthenticated ? <ManageTokens /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/manage-users" 
            element={isAuthenticated ? <ManageUsers /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/email-logs" 
            element={isAuthenticated ? <EmailLogs /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/" 
            element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} 
          />
        </Routes>
      </main>
    </div>
  );
}

export default App; 