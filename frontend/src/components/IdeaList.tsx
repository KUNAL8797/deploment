import React, { useState, useEffect } from 'react';
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
    created_by: number;
    created_at: string;
    updated_at: string;
}

interface IdeaListResponse {
    items: Idea[];
    total: number;
    skip: number;
    limit: number;
    has_next: boolean;
}

interface IdeaListProps {
    refreshTrigger: number;
}

interface InsightsData {
    idea_id: number;
    idea_title: string;
    market_insights: string;
    risk_assessment: string;
    implementation_roadmap: string;
    is_ai_generated: boolean;
    generation_version: number;
    generated_at: string;
    last_updated: string;
}

interface InsightsStatus {
    idea_id: number;
    has_insights: boolean;
    insights_count: number;
    current_version?: number;
    first_generated?: string;
    last_updated?: string;
    is_ai_generated?: boolean;
}

const developmentStages = [
    { value: '', label: 'All Stages' },
    { value: 'concept', label: 'Concept' },
    { value: 'research', label: 'Research' },
    { value: 'prototype', label: 'Prototype' },
    { value: 'testing', label: 'Testing' },
    { value: 'launch', label: 'Launch' }
];

const IdeaList: React.FC<IdeaListProps> = ({ refreshTrigger }) => {
    const [ideas, setIdeas] = useState<Idea[]>([]);
    const [loading, setLoading] = useState(false);
    const [enhancing, setEnhancing] = useState<number | null>(null);
    const [error, setError] = useState('');
    const [expandedIdeas, setExpandedIdeas] = useState<Set<number>>(new Set());
    
    // Delete functionality states
    const [deletingIdea, setDeletingIdea] = useState<number | null>(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);
    
    // Insights Status Tracking
    const [insightsStatus, setInsightsStatus] = useState<{[key: number]: InsightsStatus}>({});
    const [checkingInsights, setCheckingInsights] = useState<Set<number>>(new Set());
    
    // Insights Modal State
    const [insightsModal, setInsightsModal] = useState<{
        show: boolean;
        data: InsightsData | null;
        loading: boolean;
        ideaId?: number;
    }>({
        show: false,
        data: null,
        loading: false
    });
    
    const [pagination, setPagination] = useState({
        skip: 0,
        limit: 10,
        total: 0,
        has_next: false
    });

    const [filters, setFilters] = useState({
        stage: '',
        search: '',
        ai_validated: '',
        sort_by: 'created_at',
        sort_order: 'desc'
    });

    // Enhanced AI Content Formatting Function
    const formatAIContent = (content: string) => {
        if (!content) return null;
        
        const sections = content.split('\n\n').filter(section => section.trim());
        
        return (
            <div className="formatted-ai-content">
                {sections.map((section, index) => {
                    const trimmedSection = section.trim();
                    
                    // Handle standalone headers (lines that are entirely bold)
                    if (trimmedSection.match(/^\*\*([^*]+)\*\*$/)) {
                        const headerText = trimmedSection.replace(/^\*\*(.+)\*\*$/, '$1');
                        return (
                            <div key={index} className="ai-section">
                                <h5 className="ai-section-title">{headerText}</h5>
                            </div>
                        );
                    }
                    
                    // Handle sections with mixed content (paragraphs with bold text)
                    if (trimmedSection.includes('**')) {
                        const formattedText = trimmedSection
                            .split(/(\*\*[^*]+\*\*)/)
                            .map((part, partIndex) => {
                                if (part.startsWith('**') && part.endsWith('**')) {
                                    const boldText = part.replace(/\*\*/g, '');
                                    return <strong key={partIndex} className="ai-bold">{boldText}</strong>;
                                }
                                return <span key={partIndex}>{part}</span>;
                            });
                        
                        return (
                            <div key={index} className="ai-paragraph">
                                <p>{formattedText}</p>
                            </div>
                        );
                    }
                    
                    // Handle numbered lists
                    if (trimmedSection.match(/^\d+\./)) {
                        const listItems = trimmedSection.split('\n').filter(item => item.trim());
                        return (
                            <div key={index} className="ai-list-section">
                                <ol className="ai-numbered-list">
                                    {listItems.map((item, itemIndex) => {
                                        const cleanItem = item.replace(/^\d+\.\s*/, '').trim();
                                        const formattedItem = cleanItem.includes('**') 
                                            ? cleanItem.split(/(\*\*[^*]+\*\*)/).map((part, partIndex) => {
                                                if (part.startsWith('**') && part.endsWith('**')) {
                                                    return <strong key={partIndex}>{part.replace(/\*\*/g, '')}</strong>;
                                                }
                                                return <span key={partIndex}>{part}</span>;
                                            })
                                            : cleanItem;
                                        
                                        return (
                                            <li key={itemIndex} className="ai-list-item">
                                                {formattedItem}
                                            </li>
                                        );
                                    })}
                                </ol>
                            </div>
                        );
                    }
                    
                    // Handle bullet points
                    if (trimmedSection.includes('- ') || trimmedSection.includes('• ')) {
                        const listItems = trimmedSection.split('\n').filter(item => item.trim());
                        return (
                            <div key={index} className="ai-list-section">
                                <ul className="ai-bullet-list">
                                    {listItems.map((item, itemIndex) => {
                                        const cleanItem = item.replace(/^[-•]\s*/, '').trim();
                                        const formattedItem = cleanItem.includes('**') 
                                            ? cleanItem.split(/(\*\*[^*]+\*\*)/).map((part, partIndex) => {
                                                if (part.startsWith('**') && part.endsWith('**')) {
                                                    return <strong key={partIndex}>{part.replace(/\*\*/g, '')}</strong>;
                                                }
                                                return <span key={partIndex}>{part}</span>;
                                            })
                                            : cleanItem;
                                        
                                        return (
                                            <li key={itemIndex} className="ai-list-item">
                                                {formattedItem}
                                            </li>
                                        );
                                    })}
                                </ul>
                            </div>
                        );
                    }
                    
                    // Regular paragraph with potential bold text
                    if (trimmedSection.trim()) {
                        const formattedText = trimmedSection.includes('**') 
                            ? trimmedSection.split(/(\*\*[^*]+\*\*)/).map((part, partIndex) => {
                                if (part.startsWith('**') && part.endsWith('**')) {
                                    return <strong key={partIndex} className="ai-bold">{part.replace(/\*\*/g, '')}</strong>;
                                }
                                return <span key={partIndex}>{part}</span>;
                            })
                            : trimmedSection;
                        
                        return (
                            <div key={index} className="ai-paragraph">
                                <p>{formattedText}</p>
                            </div>
                        );
                    }
                    
                    return null;
                })}
            </div>
        );
    };

    // Delete idea function
    const handleDeleteIdea = async (ideaId: number, ideaTitle: string) => {
        setDeletingIdea(ideaId);
        
        try {
            console.log(`Deleting idea ${ideaId}: ${ideaTitle}`);
            await ideaService.deleteIdea(ideaId);
            
            // Remove from local state
            setIdeas(prev => prev.filter(idea => idea.id !== ideaId));
            
            // Update pagination
            setPagination(prev => ({
                ...prev,
                total: prev.total - 1
            }));
            
            // Clear any related state
            setExpandedIdeas(prev => {
                const newSet = new Set(prev);
                newSet.delete(ideaId);
                return newSet;
            });
            
            setInsightsStatus(prev => {
                const newStatus = { ...prev };
                delete newStatus[ideaId];
                return newStatus;
            });
            
            console.log(`✅ Successfully deleted idea ${ideaId}: ${ideaTitle}`);
            
        } catch (error: any) {
            console.error(`❌ Failed to delete idea ${ideaId}:`, error);
            setError(`Failed to delete "${ideaTitle}". Please try again.`);
        } finally {
            setDeletingIdea(null);
            setShowDeleteConfirm(null);
        }
    };

    // Confirm delete with dialog
    const confirmDeleteIdea = (ideaId: number, ideaTitle: string) => {
        if (window.confirm(`Are you sure you want to delete "${ideaTitle}"?\n\nThis action cannot be undone and will remove:\n• The idea and all its content\n• AI-generated enhancements\n• Market insights and analysis\n• All associated data`)) {
            handleDeleteIdea(ideaId, ideaTitle);
        }
    };

    // Check insights status for an idea
    const checkInsightsStatus = async (ideaId: number) => {
        if (checkingInsights.has(ideaId)) return;
        
        setCheckingInsights(prev => new Set(prev).add(ideaId));
        
        try {
            const response = await ideaService.getInsightsHistory(ideaId);
            setInsightsStatus(prev => ({ ...prev, [ideaId]: response }));
        } catch (error) {
            console.error(`Failed to check insights status for idea ${ideaId}:`, error);
        } finally {
            setCheckingInsights(prev => {
                const newSet = new Set(prev);
                newSet.delete(ideaId);
                return newSet;
            });
        }
    };

    // Load ideas function
    const loadIdeas = async () => {
        setLoading(true);
        setError('');
        
        try {
            const params: any = {
                skip: pagination.skip,
                limit: pagination.limit,
                sort_by: filters.sort_by,
                sort_order: filters.sort_order
            };

            if (filters.stage) params.stage = filters.stage;
            if (filters.search) params.search = filters.search;
            if (filters.ai_validated) params.ai_validated = filters.ai_validated === 'true';

            console.log('Loading ideas with params:', params);
            const response: IdeaListResponse = await ideaService.getIdeas(params);
            
            setIdeas(response.items);
            setPagination({
                skip: response.skip,
                limit: response.limit,
                total: response.total,
                has_next: response.has_next
            });
            
            console.log(`Loaded ${response.items.length} ideas, total: ${response.total}`);
            
            // Check insights status for AI-validated ideas
            response.items.forEach(idea => {
                if (idea.ai_validated) {
                    checkInsightsStatus(idea.id);
                }
            });
            
        } catch (error: any) {
            console.error('Failed to load ideas:', error);
            setError('Failed to load ideas. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Enhancement function
    const handleEnhanceIdea = async (ideaId: number) => {
        setEnhancing(ideaId);
        
        try {
            console.log(`Starting AI enhancement for idea ${ideaId}`);
            await ideaService.enhanceIdea(ideaId);
            
            // Refresh ideas after enhancement
            await loadIdeas();
            
            console.log(`✅ Successfully enhanced idea ${ideaId}`);
            
        } catch (error: any) {
            console.error(`❌ Failed to enhance idea ${ideaId}:`, error);
            setError('Failed to enhance idea with AI. Please try again.');
        } finally {
            setEnhancing(null);
        }
    };

    // Toggle idea expansion
    const toggleIdeaExpansion = (ideaId: number) => {
        setExpandedIdeas(prev => {
            const newSet = new Set(prev);
            if (newSet.has(ideaId)) {
                newSet.delete(ideaId);
            } else {
                newSet.add(ideaId);
            }
            return newSet;
        });
    };

    // Enhanced insights loading with database integration
    const loadAdditionalInsights = async (ideaId: number, forceRegenerate: boolean = false) => {
        setInsightsModal({ show: true, data: null, loading: true, ideaId });
        
        try {
            console.log(`Loading AI insights for idea ${ideaId} (force regenerate: ${forceRegenerate})`);
            const insights = await ideaService.getIdeaInsights(ideaId, forceRegenerate);
            setInsightsModal({ show: true, data: insights, loading: false, ideaId });
            
            // Update insights status after loading
            await checkInsightsStatus(ideaId);
            
            console.log(`✅ Successfully loaded insights for idea ${ideaId}`);
        } catch (error: any) {
            console.error('Failed to load insights:', error);
            setError('Failed to load additional insights. Please try again.');
            setInsightsModal({ show: false, data: null, loading: false });
        }
    };

    // Force regenerate insights
    const regenerateInsights = async () => {
        if (!insightsModal.ideaId) return;
        
        setInsightsModal(prev => ({ ...prev, loading: true, data: null }));
        
        try {
            console.log(`Regenerating insights for idea ${insightsModal.ideaId}`);
            const insights = await ideaService.getIdeaInsights(insightsModal.ideaId, true);
            setInsightsModal(prev => ({ ...prev, data: insights, loading: false }));
            
            // Update insights status after regeneration
            await checkInsightsStatus(insightsModal.ideaId);
            
            console.log(`✅ Successfully regenerated insights for idea ${insightsModal.ideaId}`);
        } catch (error: any) {
            console.error('Failed to regenerate insights:', error);
            setError('Failed to regenerate insights. Please try again.');
            setInsightsModal(prev => ({ ...prev, loading: false }));
        }
    };

    const closeInsightsModal = () => {
        setInsightsModal({ show: false, data: null, loading: false });
    };

    // Filter handlers
    const handleFilterChange = (field: string, value: string) => {
        setFilters(prev => ({ ...prev, [field]: value }));
        setPagination(prev => ({ ...prev, skip: 0 }));
    };

    // Pagination handlers
    const handlePageChange = (newSkip: number) => {
        setPagination(prev => ({ ...prev, skip: newSkip }));
    };

    const goToNextPage = () => {
        if (pagination.has_next) {
            handlePageChange(pagination.skip + pagination.limit);
        }
    };

    const goToPreviousPage = () => {
        if (pagination.skip > 0) {
            handlePageChange(Math.max(0, pagination.skip - pagination.limit));
        }
    };

    // Utility functions
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const formatDateTime = (dateString: string) => {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
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

    const getInsightsButtonText = (ideaId: number) => {
        const status = insightsStatus[ideaId];
        if (checkingInsights.has(ideaId)) {
            return '🔍 Checking insights...';
        }
        if (status?.has_insights) {
            return '🔄 View/Update Market Insights';
        }
        return '💡 Generate Market Insights';
    };

    const getInsightsButtonClass = (ideaId: number) => {
        const status = insightsStatus[ideaId];
        if (status?.has_insights) {
            return 'insights-btn cached';
        }
        return 'insights-btn';
    };

    // Effects
    useEffect(() => {
        loadIdeas();
    }, [pagination.skip, filters, refreshTrigger]);

    useEffect(() => {
        if (error) {
            const timer = setTimeout(() => setError(''), 5000);
            return () => clearTimeout(timer);
        }
    }, [error]);

    // Calculate stats
    const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;
    const totalPages = Math.ceil(pagination.total / pagination.limit);
    const aiValidatedCount = ideas.filter(idea => idea.ai_validated).length;
    const aiPendingCount = ideas.length - aiValidatedCount;
    const insightsGeneratedCount = Object.values(insightsStatus).filter(status => status.has_insights).length;

    return (
        <div className="idea-list">
            {/* Header */}
            <div className="list-header">
                <div className="header-info">
                    <h2>Your Innovation Ideas ({pagination.total})</h2>
                    <div className="ideas-stats">
                        <span className="stat-item">
                            <strong>{pagination.total}</strong> Total Ideas
                        </span>
                        <span className="stat-item ai-validated">
                            <strong>{aiValidatedCount}</strong> 🤖 AI Enhanced
                        </span>
                        <span className="stat-item insights-generated">
                            <strong>{insightsGeneratedCount}</strong> 📊 Insights Generated
                        </span>
                        {aiPendingCount > 0 && (
                            <span className="stat-item ai-pending">
                                <strong>{aiPendingCount}</strong> ⏳ Pending Enhancement
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Filters and Controls */}
            <div className="filters-section">
                <div className="filters">
                    <select
                        value={filters.stage}
                        onChange={(e) => handleFilterChange('stage', e.target.value)}
                        className="filter-select"
                    >
                        {developmentStages.map(stage => (
                            <option key={stage.value} value={stage.value}>
                                {stage.label}
                            </option>
                        ))}
                    </select>

                    <select
                        value={filters.ai_validated}
                        onChange={(e) => handleFilterChange('ai_validated', e.target.value)}
                        className="filter-select"
                    >
                        <option value="">All Ideas</option>
                        <option value="true">🤖 AI Enhanced</option>
                        <option value="false">⏳ Pending Enhancement</option>
                    </select>

                    <input
                        type="text"
                        placeholder="Search ideas..."
                        value={filters.search}
                        onChange={(e) => handleFilterChange('search', e.target.value)}
                        className="search-input"
                    />
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-banner">
                    <span>⚠️ {error}</span>
                    <button onClick={() => setError('')} className="error-close">✕</button>
                </div>
            )}

            {/* Loading State */}
            {loading ? (
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading your ideas...</p>
                </div>
            ) : ideas.length === 0 ? (
                /* Empty State */
                <div className="empty-state">
                    <div className="empty-illustration">💡</div>
                    <h3>No Ideas Found</h3>
                    <p>
                        {filters.search || filters.stage || filters.ai_validated
                            ? 'No ideas match your current filters. Try adjusting your search criteria.'
                            : 'Start your innovation journey by creating your first idea!'}
                    </p>
                    {(filters.search || filters.stage || filters.ai_validated) && (
                        <button 
                            className="clear-filters-btn"
                            onClick={() => {
                                setFilters({
                                    stage: '',
                                    search: '',
                                    ai_validated: '',
                                    sort_by: 'created_at',
                                    sort_order: 'desc'
                                });
                            }}
                        >
                            Clear All Filters
                        </button>
                    )}
                </div>
            ) : (
                /* Ideas Grid */
                <>
                    <div className="ideas-grid">
                        {ideas.map(idea => (
                            <div key={idea.id} className="idea-card">
                                {/* Idea Header */}
                                <div className="idea-header">
                                    <div className="idea-title-section">
                                        <h3>{idea.title}</h3>
                                        <div className="idea-badges">
                                            <span 
                                                className="stage-badge"
                                                style={{ backgroundColor: getStageColor(idea.development_stage) }}
                                            >
                                                {idea.development_stage.toUpperCase()}
                                            </span>
                                            {idea.ai_validated ? (
                                                <span className="ai-validated-badge">🤖 AI Enhanced</span>
                                            ) : (
                                                <span className="ai-pending-badge">⏳ Pending</span>
                                            )}
                                            {insightsStatus[idea.id]?.has_insights && (
                                                <span className="insights-cached-badge">📊 Insights Cached</span>
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
                                        <small>Score</small>
                                    </div>
                                </div>
                                
                                {/* Original Description */}
                                <div className="original-description">
                                    <h4>📝 Original Concept:</h4>
                                    <p>
                                        {idea.description.length > 150 
                                            ? `${idea.description.substring(0, 150)}...` 
                                            : idea.description}
                                    </p>
                                </div>
                                
                                {/* AI Enhanced Content */}
                                {idea.ai_validated && idea.ai_refined_pitch ? (
                                    <div className="ai-enhanced-section">
                                        <div className="ai-section-header">
                                            <h4>🤖 AI-Enhanced Professional Pitch</h4>
                                            <button 
                                                className="toggle-content-btn"
                                                onClick={() => toggleIdeaExpansion(idea.id)}
                                            >
                                                <span>{expandedIdeas.has(idea.id) ? '🔼' : '🔽'}</span>
        <span>{expandedIdeas.has(idea.id) ? 'Collapse Analysis' : 'Expand Full Analysis'}</span>
                                            </button>
                                        </div>
                                        <button 
    className="expand-btn"
    onClick={() => toggleIdeaExpansion(idea.id)}
>
    <span>📖</span>
    <span>Read Complete AI Analysis</span>
    <span>→</span>
</button>
<button 
    className={getInsightsButtonClass(idea.id)}
    onClick={() => loadAdditionalInsights(idea.id)}
    disabled={insightsModal.loading || checkingInsights.has(idea.id)}
>
    {insightsModal.loading && insightsModal.ideaId === idea.id ? (
        <>
            <span>⏳</span>
            <span>Loading Insights...</span>
        </>
    ) : (
        <>
            <span>{insightsStatus[idea.id]?.has_insights ? '🔄' : '💡'}</span>
            <span>
                {insightsStatus[idea.id]?.has_insights 
                    ? 'View/Update Market Insights' 
                    : 'Generate Market Insights'
                }
            </span>
            <span>→</span>
        </>
    )}
</button>
                                        <div className="ai-refined-display">
                                            {expandedIdeas.has(idea.id) ? (
                                                <div className="full-ai-analysis">
                                                    {formatAIContent(idea.ai_refined_pitch)}
                                                    
                                                    <div className="ai-actions">
                                                        <button 
                                                            className={getInsightsButtonClass(idea.id)}
                                                            onClick={() => loadAdditionalInsights(idea.id)}
                                                            disabled={insightsModal.loading || checkingInsights.has(idea.id)}
                                                        >
                                                            {insightsModal.loading && insightsModal.ideaId === idea.id ? (
                                                                <>⏳ Loading Insights...</>
                                                            ) : (
                                                                getInsightsButtonText(idea.id)
                                                            )}
                                                        </button>
                                                        {insightsStatus[idea.id]?.has_insights && (
                                                            <div className="insights-status">
                                                                <small>
                                                                    Last updated: {formatDateTime(insightsStatus[idea.id].last_updated!)}
                                                                    {insightsStatus[idea.id].is_ai_generated ? ' 🤖' : ' ⚠️'}
                                                                </small>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="preview-display">
                                                    <div className="preview-content">
                                                        {formatAIContent(idea.ai_refined_pitch.substring(0, 400) + '...')}
                                                    </div>
                                                    <div className="content-fade"></div>
                                                    <button 
                                                        className="expand-btn"
                                                        onClick={() => toggleIdeaExpansion(idea.id)}
                                                    >
                                                        📖 Read Complete AI Analysis
                                                    </button>
                                                </div>
                                            )}
                                        </div>

                                        {/* AI Metrics Dashboard */}
                                        <div className="ai-metrics-dashboard">
                                            <h5>📊 AI Feasibility Breakdown</h5>
                                            <div className="metrics-container">
                                                <div className="metric-card">
                                                    <div className="metric-header">
                                                        <span className="metric-icon">📈</span>
                                                        <span className="metric-title">Market Potential</span>
                                                        <span className="metric-score">{idea.market_potential?.toFixed(1)}/10</span>
                                                    </div>
                                                    <div className="metric-bar-container">
                                                        <div className="metric-bar">
                                                            <div 
                                                                className="metric-fill market-fill"
                                                                style={{ width: `${(idea.market_potential || 0) * 10}%` }}
                                                            ></div>
                                                        </div>
                                                    </div>
                                                    <p className="metric-description">
                                                        Market size, customer demand, and growth opportunities
                                                    </p>
                                                </div>

                                                <div className="metric-card">
                                                    <div className="metric-header">
                                                        <span className="metric-icon">⚙️</span>
                                                        <span className="metric-title">Technical Feasibility</span>
                                                        <span className="metric-score">
                                                            {(11 - (idea.technical_complexity || 5)).toFixed(1)}/10
                                                        </span>
                                                    </div>
                                                    <div className="metric-bar-container">
                                                        <div className="metric-bar">
                                                            <div 
                                                                className="metric-fill technical-fill"
                                                                style={{ width: `${((11 - (idea.technical_complexity || 5)) * 10)}%` }}
                                                            ></div>
                                                        </div>
                                                    </div>
                                                    <p className="metric-description">
                                                        Development complexity and implementation difficulty
                                                    </p>
                                                </div>

                                                <div className="metric-card">
                                                    <div className="metric-header">
                                                        <span className="metric-icon">💰</span>
                                                        <span className="metric-title">Resource Efficiency</span>
                                                        <span className="metric-score">
                                                            {(11 - (idea.resource_requirements || 5)).toFixed(1)}/10
                                                        </span>
                                                    </div>
                                                    <div className="metric-bar-container">
                                                        <div className="metric-bar">
                                                            <div 
                                                                className="metric-fill resources-fill"
                                                                style={{ width: `${((11 - (idea.resource_requirements || 5)) * 10)}%` }}
                                                            ></div>
                                                        </div>
                                                    </div>
                                                    <p className="metric-description">
                                                        Capital requirements and operational overhead
                                                    </p>
                                                </div>
                                            </div>
                                            
                                            {/* Overall Score Summary */}
                                            <div className="overall-feasibility">
                                                <div className="feasibility-header">
                                                    <h6>🎯 Overall Feasibility Score</h6>
                                                    <div 
                                                        className="feasibility-score-large"
                                                        style={{ color: getFeasibilityColor(idea.feasibility_score) }}
                                                    >
                                                        {idea.feasibility_score.toFixed(1)}/10
                                                    </div>
                                                </div>
                                                <div className="feasibility-bar">
                                                    <div 
                                                        className="feasibility-fill"
                                                        style={{ 
                                                            width: `${idea.feasibility_score * 10}%`,
                                                            background: getFeasibilityColor(idea.feasibility_score)
                                                        }}
                                                    ></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    /* No AI Enhancement */
                                    <div className="no-ai-enhancement">
                                        <div className="enhancement-card">
                                            <h4>🚀 Ready for AI Enhancement?</h4>
                                            <p>Transform your idea into a professional business pitch with:</p>
                                            <ul className="enhancement-features">
                                                <li>🎯 Professional pitch refinement</li>
                                                <li>📊 Market potential analysis</li>
                                                <li>⚙️ Technical feasibility assessment</li>
                                                <li>💰 Resource requirement evaluation</li>
                                            </ul>
                                            <button 
                                                onClick={() => handleEnhanceIdea(idea.id)}
                                                disabled={enhancing === idea.id}
                                                className="enhance-action-btn"
                                            >
                                                {enhancing === idea.id ? (
                                                    <>⏳ AI is analyzing your idea...</>
                                                ) : (
                                                    <>🤖 Enhance with Gemini 2.5 Pro</>
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                )}
                                
                                {/* Enhanced Footer with Delete */}
                                <div className="idea-footer">
                                    <div className="idea-meta">
                                        <div className="idea-date">
                                            Created {formatDate(idea.created_at)}
                                        </div>
                                        {idea.ai_validated && idea.updated_at !== idea.created_at && (
                                            <div className="idea-updated">
                                                Enhanced {formatDate(idea.updated_at)}
                                            </div>
                                        )}
                                    </div>
                                    
                                    <div className="idea-actions">
                                        {idea.ai_validated && (
                                            <button 
                                                onClick={() => handleEnhanceIdea(idea.id)}
                                                disabled={enhancing === idea.id}
                                                className="re-enhance-btn"
                                                title="Re-enhance with AI"
                                            >
                                                {enhancing === idea.id ? (
                                                    <>⏳ Re-enhancing...</>
                                                ) : (
                                                    <>🔄 Re-enhance</>
                                                )}
                                            </button>
                                        )}
                                        
                                        <div className="danger-actions">
                                            {showDeleteConfirm === idea.id ? (
                                                <div className="delete-confirm">
                                                    <span className="confirm-text">Delete "{idea.title.length > 20 ? idea.title.substring(0, 20) + '...' : idea.title}"?</span>
                                                    <div>
                                                        <button
                                                            onClick={() => handleDeleteIdea(idea.id, idea.title)}
                                                            disabled={deletingIdea === idea.id}
                                                            className="confirm-delete-btn"
                                                        >
                                                            {deletingIdea === idea.id ? '⏳' : '✓ Yes'}
                                                        </button>
                                                        <button
                                                            onClick={() => setShowDeleteConfirm(null)}
                                                            className="cancel-delete-btn"
                                                        >
                                                            ✕ No
                                                        </button>
                                                    </div>
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => setShowDeleteConfirm(idea.id)}
                                                    className="delete-btn"
                                                    title="Delete idea"
                                                    disabled={deletingIdea !== null}
                                                >
                                                    🗑️ Delete
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="pagination">
                            <div className="pagination-info">
                                <span>
                                    Showing {pagination.skip + 1} to{' '}
                                    {Math.min(pagination.skip + pagination.limit, pagination.total)} of{' '}
                                    {pagination.total} ideas
                                </span>
                            </div>
                            
                            <div className="pagination-controls">
                                <button 
                                    className="page-btn"
                                    disabled={pagination.skip === 0}
                                    onClick={goToPreviousPage}
                                >
                                    ← Previous
                                </button>
                                
                                <span className="page-info">
                                    Page {currentPage} of {totalPages}
                                </span>
                                
                                <button 
                                    className="page-btn"
                                    disabled={!pagination.has_next}
                                    onClick={goToNextPage}
                                >
                                    Next →
                                </button>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Bulk Actions Footer */}
            {ideas.length > 0 && (
                <div className="bulk-actions">
                    <div className="bulk-info">
                        <small>
                            💡 Tip: Expand ideas to see complete AI-generated business pitches. Click delete to permanently remove ideas and all associated data.
                        </small>
                    </div>
                </div>
            )}

            {/* Enhanced Insights Modal with Database Integration */}
            {insightsModal.show && (
                <div className="insights-modal-overlay" onClick={closeInsightsModal}>
                    <div className="insights-modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="insights-modal-header">
                            <h3>🔍 AI Market Insights & Implementation Roadmap</h3>
                            <button className="close-modal-btn" onClick={closeInsightsModal}>✕</button>
                        </div>
                        
                        {insightsModal.loading ? (
                            <div className="insights-loading">
                                <div className="loading-spinner"></div>
                                <p>Generating comprehensive AI insights...</p>
                                <small>Analyzing market trends, assessing risks, and creating implementation roadmap...</small>
                            </div>
                        ) : insightsModal.data ? (
                            <div className="insights-content">
                                <div className="insights-header-info">
                                    <h4>📋 {insightsModal.data.idea_title}</h4>
                                    <div className="insights-metadata">
                                        <div className="metadata-row">
                                            <span>Generated: {formatDateTime(insightsModal.data.generated_at)}</span>
                                            <span>Last Updated: {formatDateTime(insightsModal.data.last_updated)}</span>
                                        </div>
                                        <div className="metadata-row">
                                            <span>Version: {insightsModal.data.generation_version}</span>
                                            <span className={`generation-badge ${insightsModal.data.is_ai_generated ? 'ai-generated' : 'fallback'}`}>
                                                {insightsModal.data.is_ai_generated ? '🤖 AI Generated' : '⚠️ Fallback Content'}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="insights-actions">
                                    <button 
                                        className="refresh-insights-btn"
                                        onClick={regenerateInsights}
                                        disabled={insightsModal.loading}
                                    >
                                        {insightsModal.loading ? '⏳ Regenerating...' : '🔄 Regenerate Fresh Insights'}
                                    </button>
                                </div>

                                <div className="insight-section">
                                    <h4>📊 Market Analysis & Competitive Intelligence</h4>
                                    <div className="insight-text">
                                        {formatAIContent(insightsModal.data.market_insights)}
                                    </div>
                                </div>
                                
                                <div className="insight-section">
                                    <h4>⚠️ Risk Assessment & Mitigation Strategies</h4>
                                    <div className="insight-text">
                                        {formatAIContent(insightsModal.data.risk_assessment)}
                                    </div>
                                </div>
                                
                                <div className="insight-section">
                                    <h4>🗺️ 12-Month Implementation Roadmap</h4>
                                    <div className="insight-text">
                                        {formatAIContent(insightsModal.data.implementation_roadmap)}
                                    </div>
                                </div>

                                <div className="insights-footer">
                                    <button 
                                        className="close-insights-btn"
                                        onClick={closeInsightsModal}
                                    >
                                        Close Insights
                                    </button>
                                </div>
                            </div>
                        ) : null}
                    </div>
                </div>
            )}
        </div>
    );
};

export default IdeaList;
