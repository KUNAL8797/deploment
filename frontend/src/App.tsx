import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import IdeaForm from './components/IdeaForm';
import IdeaList from './components/IdeaList';
import './App.css';

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
                <h1>AI Innovation Idea Incubator</h1>
                <nav className="nav-tabs">
                    <button 
                        className={activeTab === 'list' ? 'active' : ''}
                        onClick={() => setActiveTab('list')}
                    >
                        My Ideas
                    </button>
                    <button 
                        className={activeTab === 'create' ? 'active' : ''}
                        onClick={() => setActiveTab('create')}
                    >
                        Create Idea
                    </button>
                </nav>
                <button onClick={logout} className="logout-btn">Logout</button>
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
    const [showRegister, setShowRegister] = useState(false);

    const handleLoginSuccess = () => {
        console.log('Login successful');
    };

    const handleRegisterSuccess = () => {
        setShowRegister(false);
        console.log('Registration successful, please login');
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>AI Innovation Idea Incubator</h1>
            </header>
            
            <main className="main-content">
                {showRegister ? (
                    <div>
                        <Register onSuccess={handleRegisterSuccess} />
                        <p>
                            Already have an account?{' '}
                            <button onClick={() => setShowRegister(false)}>Login</button>
                        </p>
                    </div>
                ) : (
                    <div>
                        <Login onSuccess={handleLoginSuccess} />
                        <p>
                            Don't have an account?{' '}
                            <button onClick={() => setShowRegister(true)}>Register</button>
                        </p>
                    </div>
                )}
            </main>
        </div>
    );
}

function AppContent() {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? <AuthenticatedApp /> : <UnauthenticatedApp />;
}

function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}

export default App;
