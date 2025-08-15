import React, { useState } from 'react';

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
    onEnhance?: (id: number) => void;
}

const IdeaCard: React.FC<IdeaCardProps> = ({ idea, onEnhance }) => {
    const [showFullRefinement, setShowFullRefinement] = useState(false);
    const [enhancing, setEnhancing] = useState(false);

    const handleEnhance = async () => {
        setEnhancing(true);
        if (onEnhance) {
            await onEnhance(idea.id);
        }
        setEnhancing(false);
    };

    const getScoreColor = (score: number) => {
        if (score >= 8) return '#4caf50';
        if (score >= 6) return '#ff9800';
        return '#f44336';
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

    return (
        <div className="idea-card">
            {/* Header Section */}
            <div className="idea-header">
                <div className="title-section">
                    <h3>{idea.title}</h3>
                    <div className="badges">
                        <span 
                            className="stage-badge"
                            style={{ backgroundColor: getStageColor(idea.development_stage) }}
                        >
                            {idea.development_stage.toUpperCase()}
                        </span>
                        
                        {idea.ai_validated ? (
                            <span className="ai-validated-badge">
                                🤖 AI Enhanced
                            </span>
                        ) : (
                            <span className="ai-pending-badge">
                                ⏳ Enhancement Pending
                            </span>
                        )}
                    </div>
                </div>
                
                <div className="feasibility-display">
                    <div 
                        className="feasibility-circle"
                        style={{ borderColor: getScoreColor(idea.feasibility_score) }}
                    >
                        <span style={{ color: getScoreColor(idea.feasibility_score) }}>
                            {idea.feasibility_score.toFixed(1)}
                        </span>
                        <small>Score</small>
                    </div>
                </div>
            </div>

            {/* Original Idea Section */}
            <div className="original-idea-section">
                <h4>📝 Original Concept</h4>
                <p className="original-description">{idea.description}</p>
            </div>

            {/* AI Enhanced Content */}
            {idea.ai_validated && idea.ai_refined_pitch ? (
                <div className="ai-enhanced-section">
                    <div className="ai-section-header">
                        <h4>🤖 AI-Enhanced Business Pitch</h4>
                        <button 
                            className="toggle-refinement-btn"
                            onClick={() => setShowFullRefinement(!showFullRefinement)}
                        >
                            {showFullRefinement ? '🔼 Show Less' : '🔽 Show Full Analysis'}
                        </button>
                    </div>
                    
                    <div className="ai-refined-pitch">
                        <div className="refined-content">
                            {showFullRefinement ? (
                                <div className="full-refinement">
                                    <div dangerouslySetInnerHTML={{
                                        __html: idea.ai_refined_pitch.replace(/\n/g, '<br/>')
                                    }} />
                                </div>
                            ) : (
                                <p>
                                    {idea.ai_refined_pitch.length > 200 
                                        ? `${idea.ai_refined_pitch.substring(0, 200)}...`
                                        : idea.ai_refined_pitch
                                    }
                                </p>
                            )}
                        </div>
                    </div>

                    {/* AI Scoring Dashboard */}
                    <div className="ai-scoring-dashboard">
                        <h5>📊 AI Feasibility Analysis</h5>
                        <div className="scoring-grid">
                            <div className="score-item">
                                <div className="score-header">
                                    <span className="score-icon">📈</span>
                                    <span className="score-label">Market Potential</span>
                                </div>
                                <div className="score-bar">
                                    <div 
                                        className="score-fill market"
                                        style={{ width: `${(idea.market_potential || 0) * 10}%` }}
                                    ></div>
                                </div>
                                <span className="score-value">
                                    {idea.market_potential?.toFixed(1)}/10
                                </span>
                                <p className="score-description">
                                    Market size, demand, and growth opportunities
                                </p>
                            </div>

                            <div className="score-item">
                                <div className="score-header">
                                    <span className="score-icon">⚙️</span>
                                    <span className="score-label">Technical Simplicity</span>
                                </div>
                                <div className="score-bar">
                                    <div 
                                        className="score-fill technical"
                                        style={{ width: `${((11 - (idea.technical_complexity || 5)) * 10)}%` }}
                                    ></div>
                                </div>
                                <span className="score-value">
                                    {(11 - (idea.technical_complexity || 5)).toFixed(1)}/10
                                </span>
                                <p className="score-description">
                                    Ease of development and implementation
                                </p>
                            </div>

                            <div className="score-item">
                                <div className="score-header">
                                    <span className="score-icon">💰</span>
                                    <span className="score-label">Resource Efficiency</span>
                                </div>
                                <div className="score-bar">
                                    <div 
                                        className="score-fill resources"
                                        style={{ width: `${((11 - (idea.resource_requirements || 5)) * 10)}%` }}
                                    ></div>
                                </div>
                                <span className="score-value">
                                    {(11 - (idea.resource_requirements || 5)).toFixed(1)}/10
                                </span>
                                <p className="score-description">
                                    Capital needs and operational requirements
                                </p>
                            </div>
                        </div>

                        {/* Overall Feasibility Summary */}
                        <div className="feasibility-summary">
                            <div className="summary-header">
                                <h6>🎯 Overall Feasibility Assessment</h6>
                                <div 
                                    className="overall-score"
                                    style={{ color: getScoreColor(idea.feasibility_score) }}
                                >
                                    {idea.feasibility_score.toFixed(1)}/10
                                </div>
                            </div>
                            <div className="feasibility-breakdown">
                                <span>
                                    Calculated from: Market Potential ({idea.market_potential?.toFixed(1)}) + 
                                    Technical Simplicity ({(11 - (idea.technical_complexity || 5)).toFixed(1)}) + 
                                    Resource Efficiency ({(11 - (idea.resource_requirements || 5)).toFixed(1)}) ÷ 3
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="no-ai-enhancement">
                    <div className="enhancement-prompt">
                        <h4>🚀 Ready for AI Enhancement?</h4>
                        <p>Get a professional business pitch and feasibility analysis powered by Gemini 2.5 Pro</p>
                        <button 
                            className="enhance-btn"
                            onClick={handleEnhance}
                            disabled={enhancing}
                        >
                            {enhancing ? (
                                <>⏳ Enhancing with AI...</>
                            ) : (
                                <>🤖 Enhance with AI</>
                            )}
                        </button>
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="idea-footer">
                <div className="creation-date">
                    Created {new Date(idea.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                    })}
                </div>
                
                {idea.ai_validated && (
                    <button 
                        className="re-enhance-btn"
                        onClick={handleEnhance}
                        disabled={enhancing}
                    >
                        🔄 Re-enhance
                    </button>
                )}
            </div>
        </div>
    );
};


export default IdeaCard;
