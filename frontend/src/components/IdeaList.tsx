
import React, { useState, useEffect } from 'react';
import { ideaService } from '../services/ideaService';

interface Idea {
    id: number;
    title: string;
    description: string;
    development_stage: string;
    ai_validated: boolean;
    feasibility_score: number;
    created_at: string;
}

interface IdeaListProps {
    refreshTrigger: number;
}

const IdeaList: React.FC<IdeaListProps> = ({ refreshTrigger }) => {
    const [ideas, setIdeas] = useState<Idea[]>([]);
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({
        skip: 0,
        limit: 10,
        total: 0,
        has_next: false
    });
    const [filters, setFilters] = useState({
        stage: '',
        search: '',
        ai_validated: ''
    });

    const loadIdeas = async () => {
        setLoading(true);
        try {
            const params: any = {
                skip: pagination.skip,
                limit: pagination.limit
            };

            if (filters.stage) params.stage = filters.stage;
            if (filters.search) params.search = filters.search;
            if (filters.ai_validated) params.ai_validated = filters.ai_validated === 'true';

            const response = await ideaService.getIdeas(params);
            setIdeas(response.items);
            setPagination({
                skip: response.skip,
                limit: response.limit,
                total: response.total,
                has_next: response.has_next
            });
        } catch (error) {
            console.error('Failed to load ideas:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadIdeas();
    }, [pagination.skip, filters, refreshTrigger]);

    const handleFilterChange = (field: string, value: string) => {
        setFilters(prev => ({ ...prev, [field]: value }));
        setPagination(prev => ({ ...prev, skip: 0 })); // Reset to first page
    };

    const handlePageChange = (newSkip: number) => {
        setPagination(prev => ({ ...prev, skip: newSkip }));
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString();
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
        <div className="idea-list">
            <div className="list-header">
                <h2>Innovation Ideas ({pagination.total})</h2>
                
                {/* Filters */}
                <div className="filters">
                    <select
                        value={filters.stage}
                        onChange={(e) => handleFilterChange('stage', e.target.value)}
                    >
                        <option value="">All Stages</option>
                        <option value="concept">Concept</option>
                        <option value="research">Research</option>
                        <option value="prototype">Prototype</option>
                        <option value="testing">Testing</option>
                        <option value="launch">Launch</option>
                    </select>

                    <input
                        type="text"
                        placeholder="Search ideas..."
                        value={filters.search}
                        onChange={(e) => handleFilterChange('search', e.target.value)}
                    />

                    <select
                        value={filters.ai_validated}
                        onChange={(e) => handleFilterChange('ai_validated', e.target.value)}
                    >
                        <option value="">All Ideas</option>
                        <option value="true">AI Validated</option>
                        <option value="false">Not AI Validated</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="loading">Loading ideas...</div>
            ) : (
                <>
                    <div className="ideas-grid">
                        {ideas.map(idea => (
                            <div key={idea.id} className="idea-card">
                                <div className="idea-header">
                                    <h3>{idea.title}</h3>
                                    <span 
                                        className="stage-badge"
                                        style={{ backgroundColor: getStageColor(idea.development_stage) }}
                                    >
                                        {idea.development_stage}
                                    </span>
                                </div>
                                
                                <p className="idea-description">
                                    {idea.description.length > 150 
                                        ? `${idea.description.substring(0, 150)}...` 
                                        : idea.description}
                                </p>
                                
                                <div className="idea-footer">
                                    <div className="idea-stats">
                                        <span>Score: {idea.feasibility_score.toFixed(1)}/10</span>
                                        {idea.ai_validated && <span className="ai-badge">🤖 AI Enhanced</span>}
                                    </div>
                                    <div className="idea-date">
                                        {formatDate(idea.created_at)}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    <div className="pagination">
                        <button 
                            disabled={pagination.skip === 0}
                            onClick={() => handlePageChange(Math.max(0, pagination.skip - pagination.limit))}
                        >
                            Previous
                        </button>
                        
                        <span>
                            Page {Math.floor(pagination.skip / pagination.limit) + 1} of{' '}
                            {Math.ceil(pagination.total / pagination.limit)}
                        </span>
                        
                        <button 
                            disabled={!pagination.has_next}
                            onClick={() => handlePageChange(pagination.skip + pagination.limit)}
                        >
                            Next
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};

export default IdeaList;
