import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL;

export const ideaService = {
    async createIdea(idea) {
        const response = await axios.post(`${API_BASE_URL}/ideas/`, idea);
        return response.data;
    },

    async getIdeas(params = {}) {
        const response = await axios.get(`${API_BASE_URL}/ideas/`, { params });
        return response.data;
    },

    async getIdea(id) {
        const response = await axios.get(`${API_BASE_URL}/ideas/${id}`);
        return response.data;
    },

    async updateIdea(id, idea) {
        const response = await axios.put(`${API_BASE_URL}/ideas/${id}`, idea);
        return response.data;
    },

    async deleteIdea(id) {
        await axios.delete(`${API_BASE_URL}/ideas/${id}`);
    },

    async enhanceIdea(id) {
        try {
            const response = await axios.post(`${API_BASE_URL}/ideas/${id}/enhance`);
            return response.data;
        } catch (error) {
            console.error('Failed to enhance idea:', error);
            throw error;
        }
    },
    async deleteIdea(id) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/ideas/${id}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting idea:', error);
            throw error;
        }
    },
    async getIdeaInsights(id) {
        try {
            const response = await axios.get(`${API_BASE_URL}/ideas/${id}/insights`);
            return response.data;
        } catch (error) {
            console.error('Failed to get idea insights:', error);
            throw error;
        }
    },
        async getIdeaInsights(id) {
        const response = await axios.get(`${API_BASE_URL}/ideas/${id}/insights`);
        return response.data;
    },
    async getIdeaInsights(id, forceRegenerate = false) {
        const params = forceRegenerate ? '?force_regenerate=true' : '';
        const response = await axios.get(`${API_BASE_URL}/ideas/${id}/insights${params}`);
        return response.data;
    },

    async getInsightsHistory(id) {
        const response = await axios.get(`${API_BASE_URL}/ideas/${id}/insights/history`);
        return response.data;
    },

    async deleteInsights(id) {
        const response = await axios.delete(`${API_BASE_URL}/ideas/${id}/insights`);
        return response.data;
    }
    
};
