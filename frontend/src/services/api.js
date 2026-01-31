import axios from 'axios';
// Usa proxy do Vite (see vite.config.js) para encaminhar /api -> http://localhost:8000
const api = axios.create({ baseURL: '/api' });
export default {
    seedDatabase() { return api.post('/seed'); },
    getGraphData() { return api.get('/graph-data'); },
    getAnalytics() { return api.get('/analytics'); }
};