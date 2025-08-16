import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import HomePage from './components/HomePage';
import Login from './components/Login';
import Register from './components/Register';
import IdeaForm from './components/IdeaForm';
import IdeaList from './components/IdeaList';
import './App.css';
import logo from "./assets/logo.png";  // adjust path if needed
// Theme Toggle Component
function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();
    
    return (
        <button
            onClick={toggleTheme}
            className="theme-toggle"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
            <div className="theme-toggle-inner">
                {theme === 'light' ? (
                    <span className="theme-icon">🌙</span>
                ) : (
                    <span className="theme-icon">☀️</span>
                )}
            </div>
        </button>
    );
}

function AuthenticatedApp() {
    const { logout } = useAuth();
    const [activeTab, setActiveTab] = useState('list');
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    const handleIdeaCreated = () => {
        setRefreshTrigger(prev => prev + 1);
        setActiveTab('list');
    };

    return (
        <div className="App">
            <header className="App-header">
                <div className="header-container">
                    <div className="header-brand">
                        <div className="brand-logo">
                            <img src={logo} alt="IdeaForge Logo" className="logo-icon" />
                            <h1>IdeaForge AI</h1>
                        </div>
                    </div>
                    
                    <nav className="nav-tabs">
                        <button 
                            className={`nav-tab ${activeTab === 'list' ? 'active' : ''}`}
                            onClick={() => setActiveTab('list')}
                        >
                            <span className="tab-icon">💡</span>
                            <span className="tab-text">My Ideas</span>
                        </button>
                        <button 
                            className={`nav-tab ${activeTab === 'create' ? 'active' : ''}`}
                            onClick={() => setActiveTab('create')}
                        >
                            <span className="tab-icon">✨</span>
                            <span className="tab-text">Create Idea</span>
                        </button>
                    </nav>
                    
                    <div className="header-actions">
                        <ThemeToggle />
                        <button onClick={logout} className="logout-btn">
                            <span>Sign Out</span>
                            <span className="logout-icon">👋</span>
                        </button>
                    </div>
                </div>
            </header>
            
            <main className="main-content">
                {activeTab === 'list' ? (
                    <IdeaList refreshTrigger={refreshTrigger} />
                ) : (
                    <IdeaForm onSuccess={handleIdeaCreated} />
                )}
            </main>
        </div>
    );
}

function UnauthenticatedApp() {
    const [currentView, setCurrentView] = useState<'home' | 'login' | 'register'>('home');

    const handleLoginSuccess = () => {
        console.log('Login successful');
    };

    const handleRegisterSuccess = () => {
        setCurrentView('login');
        console.log('Registration successful, please login');
    };

    const handleGetStarted = () => {
        setCurrentView('login');
    };

    if (currentView === 'home') {
        return (
            <div className="App">
                <nav className="home-navbar">
                    <div className="navbar-content">
                        <div className="navbar-brand">
                            <img src={logo} alt="IdeaForge Logo" className="logo-icon" />
                            <span className="brand-text">IdeaForge AI</span>
                        </div>
                        <div className="navbar-actions">
                            <ThemeToggle />
                            <button 
                                onClick={() => setCurrentView('login')}
                                className="nav-login-btn"
                            >
                                Sign In
                            </button>
                        </div>
                    </div>
                </nav>
                <HomePage onGetStarted={handleGetStarted} />
            </div>
        );
    }

    return (
        <div className="App">
            <div className="auth-layout">
                <header className="auth-header">
                    <div className="auth-brand">
                        <img src={logo} alt="IdeaForge Logo" className="logo-icon" />
                        <h1>IdeaForge AI</h1>
                    </div>
                    <div className="auth-header-actions">
                        <ThemeToggle />
                        <button 
                            onClick={() => setCurrentView('home')}
                            className="back-home-btn"
                        >
                            ← Back to Home
                        </button>
                    </div>
                </header>
                
                <main className="auth-main">
                    <div className="auth-container">
                        <div className="auth-card">
                            {currentView === 'register' ? (
                                <div className="auth-content">
                                    <div className="auth-header-text">
                                        <h2>Create Your Account</h2>
                                        <p>Start building your next breakthrough idea</p>
                                    </div>
                                    <Register onSuccess={handleRegisterSuccess} />
                                    <div className="auth-switch">
                                        <p>
                                            Already have an account?{' '}
                                            <button 
                                                onClick={() => setCurrentView('login')}
                                                className="switch-btn"
                                            >
                                                Sign In
                                            </button>
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <div className="auth-content">
                                    <div className="auth-header-text">
                                        <h2>Welcome Back</h2>
                                        <p>Continue your innovation journey</p>
                                    </div>
                                    <Login onSuccess={handleLoginSuccess} />
                                    <div className="auth-switch">
                                        <p>
                                            Don't have an account?{' '}
                                            <button 
                                                onClick={() => setCurrentView('register')}
                                                className="switch-btn"
                                            >
                                                Create Account
                                            </button>
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="auth-features">
                            <div className="feature-item">
                                <span className="feature-icon">🤖</span>
                                <span>AI-Powered Enhancement</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">📊</span>
                                <span>Smart Feasibility Analysis</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">🚀</span>
                                <span>Investor-Ready Pitches</span>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

function AppContent() {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? <AuthenticatedApp /> : <UnauthenticatedApp />;
}

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <AppContent />
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
