import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import './App.css';

function AuthenticatedApp() {
    const { logout, isAuthenticated } = useAuth();

    return (
        <div className="App">
            <header className="App-header">
                <h1>AI Innovation Idea Incubator</h1>
                <div>
                    <span>Welcome! </span>
                    <button onClick={logout}>Logout</button>
                </div>
            </header>
            
            <main>
                <p>You are logged in! Ready for Step 3...</p>
            </main>
        </div>
    );
}

function UnauthenticatedApp() {
    const [showRegister, setShowRegister] = useState(false);

    const handleLoginSuccess = () => {
        // Login success is handled by the AuthContext
        // The component will automatically re-render when authentication state changes
        console.log('Login successful');
    };

    const handleRegisterSuccess = () => {
        // After successful registration, switch back to login view
        setShowRegister(false);
        console.log('Registration successful, please login');
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>AI Innovation Idea Incubator</h1>
            </header>
            
            <main>
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
