import React, { useState } from 'react';
import { ideaService } from '../services/ideaService';

interface IdeaFormProps {
    onSuccess: () => void;
}

const developmentStages = [
    { value: 'concept', label: 'Concept' },
    { value: 'research', label: 'Research' },
    { value: 'prototype', label: 'Prototype' },
    { value: 'testing', label: 'Testing' },
    { value: 'launch', label: 'Launch' }
];

const IdeaForm: React.FC<IdeaFormProps> = ({ onSuccess }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        development_stage: 'concept'
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [aiProcessing, setAiProcessing] = useState(false);
    const [processingStage, setProcessingStage] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setAiProcessing(true);

        try {
            // Update processing stage for user feedback
            setProcessingStage('Creating idea...');
            await new Promise(resolve => setTimeout(resolve, 500)); // UX delay
            
            setProcessingStage('🤖 AI analyzing your idea...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            setProcessingStage('🧠 Generating professional pitch...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            setProcessingStage('📊 Calculating feasibility scores...');
            
            const newIdea = await ideaService.createIdea(formData);
            
            setProcessingStage('✅ AI enhancement complete!');
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Reset form
            setFormData({ title: '', description: '', development_stage: 'concept' });
            onSuccess();
            
        } catch (error: any) {
            setError(error.response?.data?.detail || 'Failed to create idea');
        } finally {
            setLoading(false);
            setAiProcessing(false);
            setProcessingStage('');
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="idea-form">
            <h2>Create New Innovation Idea</h2>
            
            {aiProcessing && (
                <div className="ai-processing-indicator">
                    <div className="processing-animation">
                        <div className="spinner"></div>
                        <div className="processing-text">{processingStage}</div>
                    </div>
                    <div className="processing-description">
                        Our AI is analyzing your idea using Gemini 2.5 Pro to:
                        <ul>
                            <li>Refine your pitch for maximum impact</li>
                            <li>Assess market potential and opportunities</li>
                            <li>Evaluate technical complexity</li>
                            <li>Calculate resource requirements</li>
                        </ul>
                    </div>
                </div>
            )}
            
            <form onSubmit={handleSubmit} style={{ opacity: aiProcessing ? 0.7 : 1 }}>
                <div className="form-group">
                    <label htmlFor="title">Idea Title *</label>
                    <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        placeholder="Enter a compelling title for your innovation..."
                        required
                        maxLength={200}
                        disabled={loading}
                    />
                    <small>Be specific and descriptive - AI will optimize this for market appeal</small>
                </div>

                <div className="form-group">
                    <label htmlFor="description">Idea Description *</label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        placeholder="Describe your innovation idea in detail. Include the problem it solves, how it works, and what makes it unique..."
                        required
                        minLength={10}
                        maxLength={2000}
                        rows={6}
                        disabled={loading}
                    />
                    <small>The more detail you provide, the better AI can refine your pitch</small>
                </div>

                <div className="form-group">
                    <label htmlFor="development_stage">Current Development Stage *</label>
                    <select
                        id="development_stage"
                        name="development_stage"
                        value={formData.development_stage}
                        onChange={handleChange}
                        required
                        disabled={loading}
                    >
                        {developmentStages.map(stage => (
                            <option key={stage.value} value={stage.value}>
                                {stage.label}
                            </option>
                        ))}
                    </select>
                    <small>AI will tailor analysis based on your current development stage</small>
                </div>

                {error && <div className="error">{error}</div>}

                <button type="submit" disabled={loading} className="submit-btn">
                    {loading ? 'Creating & AI Processing...' : '🚀 Create Idea with AI Enhancement'}
                </button>
                
                <div className="ai-disclaimer">
                    <small>
                        ⚡ Powered by Gemini 2.5 Pro AI -  Your idea will be enhanced with professional pitch refinement 
                        and comprehensive feasibility analysis
                    </small>
                </div>
            </form>
        </div>
    );
};

export default IdeaForm;
