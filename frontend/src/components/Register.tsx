import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface RegisterProps {
    onSuccess: () => void;
}

const Register: React.FC<RegisterProps> = ({ onSuccess }) => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [errors, setErrors] = useState<{[key: string]: string}>({});
    const { register, loading } = useAuth();

    const validateForm = () => {
        const newErrors: {[key: string]: string} = {};

        // Username validation
        if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters long';
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        // Password validation
        if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters long';
        }

        // Confirm password validation
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        setErrors({});

        try {
            const result = await register(formData.username, formData.email, formData.password);
            if (result.success) {
                onSuccess();
            } else {
                setErrors({ general: result.error || 'Registration failed' });
            }
        } catch (error) {
            setErrors({ general: 'An unexpected error occurred' });
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    return (
        <div className="register-form">
            <h2>Create Your Account</h2>
            <p className="register-subtitle">
                Join AI Innovation Idea Incubator to start enhancing your business ideas with AI
            </p>
            
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="username">Username *</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        placeholder="Choose a unique username"
                        required
                        disabled={loading}
                        className={errors.username ? 'error' : ''}
                    />
                    {errors.username && <small className="error-text">{errors.username}</small>}
                </div>

                <div className="form-group">
                    <label htmlFor="email">Email Address *</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="your.email@example.com"
                        required
                        disabled={loading}
                        className={errors.email ? 'error' : ''}
                    />
                    {errors.email && <small className="error-text">{errors.email}</small>}
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password *</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Create a secure password (min 6 characters)"
                        required
                        disabled={loading}
                        className={errors.password ? 'error' : ''}
                    />
                    {errors.password && <small className="error-text">{errors.password}</small>}
                </div>

                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password *</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="Confirm your password"
                        required
                        disabled={loading}
                        className={errors.confirmPassword ? 'error' : ''}
                    />
                    {errors.confirmPassword && <small className="error-text">{errors.confirmPassword}</small>}
                </div>

                {errors.general && <div className="error-banner">{errors.general}</div>}

                <button type="submit" disabled={loading} className="register-btn">
                    {loading ? 'Creating Account...' : 'Create Account'}
                </button>
            </form>

            <div className="register-footer">
                <small>
                    By registering, you agree to use this platform responsibly 
                    and acknowledge that AI-generated content is for guidance only.
                </small>
            </div>
        </div>
    );
};

export default Register;
