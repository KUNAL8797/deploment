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
        const response = await axios.post(`${API_BASE_URL}/ideas/${id}/enhance`);
        return response.data;
    },

    async getIdeaInsights(id) {
        const response = await axios.get(`${API_BASE_URL}/ideas/${id}/insights`);
        return response.data;
    }
};
