import React, { useState } from 'react';
import { ideaService } from '../services/ideaService';

interface Idea {
    id: number;
    title: string;
    description: string;
    ai_refined_pitch?: string;
    development_stage: string;
    ai_validated: boolean;
    market_potential?: number;
    technical_complexity?: number;
    resource_requirements?: number;
    feasibility_score: number;
    created_at: string;
}

interface IdeaCardProps {
    idea: Idea;
    onUpdate?: () => void;
}

const IdeaCard: React.FC<IdeaCardProps> = ({ idea, onUpdate }) => {
    const [showFullPitch, setShowFullPitch] = useState(false);
    const [loadingInsights, setLoadingInsights] = useState(false);
    const [insights, setInsights] = useState<any>(null);
    const [enhancing, setEnhancing] = useState(false);

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const getStageColor = (stage: string) => {
        const colors: { [key: string]: string } = {
            concept: '#ff9800',
            research: '#2196f3',
            prototype: '#9c27b0',
            testing: '#ff5722',
            launch: '#4caf50'
        };
        return colors[stage] || '#666';
    };

    const getFeasibilityColor = (score: number) => {
        if (score >= 8) return '#4caf50';
        if (score >= 6) return '#ff9800';
        return '#f44336';
    };

    const loadInsights = async () => {
        setLoadingInsights(true);
        try {
            const response = await ideaService.getIdeaInsights(idea.id);
            setInsights(response);
        } catch (error) {
            console.error('Failed to load insights:', error);
        } finally {
            setLoadingInsights(false);
        }
    };

    const enhanceWithAI = async () => {
        setEnhancing(true);
        try {
            await ideaService.enhanceIdea(idea.id);
            onUpdate && onUpdate();
        } catch (error) {
            console.error('Failed to enhance idea:', error);
        } finally {
            setEnhancing(false);
        }
    };

    return (
        <div className="idea-card">
            <div className="idea-header">
                <div className="idea-title-section">
                    <h3>{idea.title}</h3>
                    <div className="idea-badges">
                        <span 
                            className="stage-badge"
                            style={{ backgroundColor: getStageColor(idea.development_stage) }}
                        >
                            {idea.development_stage.charAt(0).toUpperCase() + idea.development_stage.slice(1)}
                        </span>
                        {idea.ai_validated && (
                            <span className="ai-badge">🤖 AI Enhanced</span>
                        )}
                    </div>
                </div>
                
                <div className="feasibility-score">
                    <div 
                        className="score-circle"
                        style={{ borderColor: getFeasibilityColor(idea.feasibility_score) }}
                    >
                        <span style={{ color: getFeasibilityColor(idea.feasibility_score) }}>
                            {idea.feasibility_score.toFixed(1)}
                        </span>
                    </div>
                    <small>Feasibility</small>
                </div>
            </div>
            
            <div className="idea-content">
                <div className="original-description">
                    <h4>Original Idea:</h4>
                    <p>
                        {idea.description.length > 150 
                            ? `${idea.description.substring(0, 150)}...` 
                            : idea.description}
                    </p>
                </div>
                
                {idea.ai_refined_pitch && (
                    <div className="ai-refined-pitch">
                        <h4>🤖 AI-Refined Professional Pitch:</h4>
                        <div className="pitch-content">
                            <p>
                                {showFullPitch || idea.ai_refined_pitch.length <= 200
                                    ? idea.ai_refined_pitch
                                    : `${idea.ai_refined_pitch.substring(0, 200)}...`}
                            </p>
                            {idea.ai_refined_pitch.length > 200 && (
                                <button 
                                    className="toggle-pitch-btn"
                                    onClick={() => setShowFullPitch(!showFullPitch)}
                                >
                                    {showFullPitch ? 'Show Less' : 'Show Full Pitch'}
                                </button>
                            )}
                        </div>
                    </div>
                )}
                
                {idea.ai_validated && (
                    <div className="ai-metrics">
                        <h4>📊 AI Analysis:</h4>
                        <div className="metrics-grid">
                            <div className="metric">
                                <span className="metric-label">Market Potential</span>
                                <div className="metric-bar">
                                    <div 
                                        className="metric-fill market"
                                        style={{ width: `${(idea.market_potential || 0) * 10}%` }}
                                    ></div>
                                </div>
                                <span className="metric-value">{idea.market_potential?.toFixed(1)}/10</span>
                            </div>
                            
                            <div className="metric">
                                <span className="metric-label">Technical Simplicity</span>
                                <div className="metric-bar">
                                    <div 
                                        className="metric-fill technical"
                                        style={{ width: `${((11 - (idea.technical_complexity || 5)) * 10)}%` }}
                                    ></div>
                                </div>
                                <span className="metric-value">{(11 - (idea.technical_complexity || 5)).toFixed(1)}/10</span>
                            </div>
                            
                            <div className="metric">
                                <span className="metric-label">Resource Efficiency</span>
                                <div className="metric-bar">
                                    <div 
                                        className="metric-fill resources"
                                        style={{ width: `${((11 - (idea.resource_requirements || 5)) * 10)}%` }}
                                    ></div>
                                </div>
                                <span className="metric-value">{(11 - (idea.resource_requirements || 5)).toFixed(1)}/10</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
            
            <div className="idea-actions">
                <div className="action-buttons">
                    <button 
                        onClick={loadInsights}
                        disabled={loadingInsights}
                        className="insights-btn"
                    >
                        {loadingInsights ? 'Loading...' : '💡 AI Insights'}
                    </button>
                    
                    {!idea.ai_validated && (
                        <button 
                            onClick={enhanceWithAI}
                            disabled={enhancing}
                            className="enhance-btn"
                        >
                            {enhancing ? 'Enhancing...' : '🚀 Enhance with AI'}
                        </button>
                    )}
                </div>
                
                <div className="idea-date">
                    Created {formatDate(idea.created_at)}
                </div>
            </div>
            
            {insights && (
                <div className="insights-modal">
                    <div className="insights-content">
                        <h3>🔍 AI-Generated Insights for "{idea.title}"</h3>
                        
                        <div className="insight-section">
                            <h4>📈 Market Analysis</h4>
                            <p>{insights.market_insights}</p>
                        </div>
                        
                        <div className="insight-section">
                            <h4>⚠️ Risk Assessment</h4>
                            <p>{insights.risk_assessment}</p>
                        </div>
                        
                        <div className="insight-section">
                            <h4>🗺️ Implementation Roadmap</h4>
                            <p>{insights.implementation_roadmap}</p>
                        </div>
                        
                        <button 
                            onClick={() => setInsights(null)}
                            className="close-insights-btn"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default IdeaCard;
