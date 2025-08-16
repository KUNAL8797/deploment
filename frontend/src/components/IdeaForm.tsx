import React, { useState } from 'react';
import { ideaService } from '../services/ideaService';

interface IdeaFormProps {
    onSuccess: () => void;
}

interface IdeaFormData {
    title: string;
    description: string;
    development_stage: string;
}

const developmentStages = [
    { value: 'concept', label: '💭 Concept - Just an idea', description: 'Early brainstorming phase' },
    { value: 'research', label: '🔍 Research - Gathering information', description: 'Validating market and technical feasibility' },
    { value: 'prototype', label: '🛠️ Prototype - Building first version', description: 'Creating initial working model' },
    { value: 'testing', label: '🧪 Testing - Validating with users', description: 'Getting feedback and iterating' },
    { value: 'launch', label: '🚀 Launch - Ready for market', description: 'Preparing for commercial release' }
];

const IdeaForm: React.FC<IdeaFormProps> = ({ onSuccess }) => {
    const [formData, setFormData] = useState<IdeaFormData>({
        title: '',
        description: '',
        development_stage: ''
    });
    
    const [creating, setCreating] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        
        // Clear error when user starts typing
        if (error) {
            setError('');
        }
    };

    const validateForm = (): boolean => {
        if (!formData.title.trim()) {
            setError('Please provide a title for your idea');
            return false;
        }
        
        if (formData.title.length < 3) {
            setError('Idea title should be at least 3 characters long');
            return false;
        }
        
        if (!formData.description.trim()) {
            setError('Please describe your innovation idea');
            return false;
        }
        
        if (formData.description.length < 20) {
            setError('Please provide more details about your idea (at least 20 characters)');
            return false;
        }
        
        if (!formData.development_stage) {
            setError('Please select the development stage of your idea');
            return false;
        }
        
        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        setCreating(true);
        setError('');
        
        try {
            console.log('Creating idea:', formData);
            const response = await ideaService.createIdea(formData);
            
            console.log('✅ Idea created successfully:', response);
            
            // Show success state
            setSuccess(true);
            
            // Reset form
            setFormData({
                title: '',
                description: '',
                development_stage: ''
            });
            
            // Call success callback after a brief delay to show success animation
            setTimeout(() => {
                onSuccess();
            }, 1500);
            
        } catch (error: any) {
            console.error('❌ Failed to create idea:', error);
            
            // Handle specific error messages
            if (error.response?.data?.detail) {
                setError(error.response.data.detail);
            } else if (error.response?.status === 422) {
                setError('Please check your input and try again');
            } else if (error.response?.status === 401) {
                setError('Your session has expired. Please login again');
            } else {
                setError('Failed to create idea. Please try again.');
            }
        } finally {
            setCreating(false);
            // Reset success state after showing it
            setTimeout(() => {
                setSuccess(false);
            }, 3000);
        }
    };

    const getTitleCharacterClass = () => {
        if (formData.title.length > 95) return 'error';
        if (formData.title.length > 80) return 'warning';
        return '';
    };

    const getDescriptionCharacterClass = () => {
        if (formData.description.length > 1900) return 'error';
        if (formData.description.length > 1600) return 'warning';
        return '';
    };

    const getSelectedStageInfo = () => {
        return developmentStages.find(stage => stage.value === formData.development_stage);
    };

    if (success) {
        return (
            <div className="idea-form form-success">
                <div className="idea-form-header">
                    <span className="idea-form-icon">🎉</span>
                    <h2>Innovation Created!</h2>
                    <p className="idea-form-subtitle">
                        Your idea has been successfully created and is ready for AI enhancement
                    </p>
                    <div className="idea-form-inspiration">
                        <span>✨</span>
                        <span>Redirecting to your ideas dashboard...</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="idea-form">
            <div className="idea-form-header">
                <span className="idea-form-icon">💡</span>
                <h2>Create Your Innovation</h2>
                <p className="idea-form-subtitle">
                    Transform your breakthrough concept into an AI-enhanced business opportunity
                </p>
                <div className="idea-form-inspiration">
                    <span>🚀</span>
                    <span>Every great innovation starts with a simple idea</span>
                </div>
            </div>

            {error && (
                <div className="error-banner">
                    <span>⚠️ {error}</span>
                    <button onClick={() => setError('')} className="error-close">✕</button>
                </div>
            )}

            <form onSubmit={handleSubmit} className="innovation-form">
                <div className="form-group">
                    <label htmlFor="title">
                        <span className="label-icon">✨</span>
                        Idea Title
                    </label>
                    <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        placeholder="e.g., Smart Home Energy Optimizer, AI-Powered Learning Assistant, Eco-Friendly Food Packaging..."
                        required
                        maxLength={100}
                        className={formData.title.length > 95 ? 'error' : ''}
                    />
                    <div className={`char-counter ${getTitleCharacterClass()}`}>
                        {formData.title.length}/100
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="description">
                        <span className="label-icon">📝</span>
                        Describe Your Innovation
                    </label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        placeholder="Describe your innovative idea in detail. What problem does it solve? How does it work? What makes it unique? Who is your target audience? What inspired this idea? The more details you provide, the better our AI can enhance your concept..."
                        required
                        maxLength={2000}
                        className={formData.description.length > 1900 ? 'error' : ''}
                    />
                    <div className={`char-counter ${getDescriptionCharacterClass()}`}>
                        {formData.description.length}/2000
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="development_stage">
                        <span className="label-icon">🎯</span>
                        Development Stage
                    </label>
                    <select
                        id="development_stage"
                        name="development_stage"
                        value={formData.development_stage}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Select your current stage...</option>
                        {developmentStages.map(stage => (
                            <option key={stage.value} value={stage.value}>
                                {stage.label}
                            </option>
                        ))}
                    </select>
                    {getSelectedStageInfo() && (
                        <small className="stage-description">
                            <span>💬</span>
                            {getSelectedStageInfo()!.description}
                        </small>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={creating || !formData.title.trim() || !formData.description.trim() || !formData.development_stage}
                    className={`idea-submit-btn ${creating ? 'btn-loading' : ''}`}
                >
                    {creating ? (
                        <>
                            <span className="loading-spinner">⏳</span>
                            <span>Creating Your Innovation...</span>
                        </>
                    ) : (
                        <>
                            <span>🚀</span>
                            <span>Launch My Idea</span>
                            <span>→</span>
                        </>
                    )}
                </button>

                {creating && (
                    <div className="creation-progress">
                        <div className="progress-text">
                            <span>✨ Processing your innovation...</span>
                        </div>
                        <div className="progress-steps">
                            <div className="progress-step active">📝 Analyzing content</div>
                            <div className="progress-step active">💾 Saving to database</div>
                            <div className="progress-step">🤖 Preparing for AI enhancement</div>
                        </div>
                    </div>
                )}
            </form>

            <div className="form-tips">
                <h4>
                    <span>💡</span>
                    Pro Tips for Better Ideas
                </h4>
                <ul>
                    <li>Be specific about the problem you're solving and why it matters</li>
                    <li>Explain your unique approach, technology, or methodology</li>
                    <li>Mention your target audience, market size, or user personas</li>
                    <li>Include any inspiration, research, or validation behind your idea</li>
                    <li>Don't worry about perfection - our AI will enhance and refine it!</li>
                    <li>Think about scalability, monetization, and long-term vision</li>
                </ul>
            </div>

            <div className="form-examples">
                <h4>
                    <span>🌟</span>
                    Need Inspiration? Here are some example ideas:
                </h4>
                <div className="example-cards">
                    <div className="example-card" onClick={() => setFormData({
                        title: 'AI-Powered Personal Finance Coach',
                        description: 'A mobile app that uses machine learning to analyze spending patterns, predict financial risks, and provide personalized budgeting advice. Users can connect their bank accounts, set financial goals, and receive real-time alerts about unusual spending. The AI learns from user behavior to offer increasingly accurate recommendations for saving, investing, and debt management.',
                        development_stage: 'concept'
                    })}>
                        <div className="example-icon">💰</div>
                        <div className="example-title">AI Finance Coach</div>
                        <div className="example-desc">Personal financial guidance powered by machine learning</div>
                    </div>

                    <div className="example-card" onClick={() => setFormData({
                        title: 'Smart Urban Farming System',
                        description: 'An IoT-enabled vertical farming solution for urban apartments and offices. The system uses sensors to monitor soil moisture, light levels, and nutrient content, automatically adjusting conditions for optimal plant growth. Users can control and monitor their gardens remotely through a mobile app, receive harvest predictions, and get notifications about plant health. Perfect for growing fresh vegetables and herbs in limited urban spaces.',
                        development_stage: 'research'
                    })}>
                        <div className="example-icon">🌱</div>
                        <div className="example-title">Smart Urban Farm</div>
                        <div className="example-desc">IoT-powered vertical farming for city dwellers</div>
                    </div>

                    <div className="example-card" onClick={() => setFormData({
                        title: 'Virtual Reality Therapy Platform',
                        description: 'A VR-based mental health platform that provides immersive therapy sessions for anxiety, phobias, and PTSD. The platform offers guided meditation environments, exposure therapy simulations, and cognitive behavioral therapy exercises. Licensed therapists can monitor progress and customize treatment plans. The system creates safe, controlled virtual environments that help patients confront and overcome their challenges at their own pace.',
                        development_stage: 'prototype'
                    })}>
                        <div className="example-icon">🥽</div>
                        <div className="example-title">VR Therapy Platform</div>
                        <div className="example-desc">Immersive virtual reality for mental health treatment</div>
                    </div>
                </div>
                <small className="examples-note">
                    <span>💡</span>
                    Click any example to auto-fill the form and see how detailed ideas look!
                </small>
            </div>
        </div>
    );
};

export default IdeaForm;
