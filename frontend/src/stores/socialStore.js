import { defineStore } from 'pinia';
import api from '../services/api';

export const useSocialStore = defineStore('social', {
    state: () => ({ nodes: {}, edges: {}, analyticsData: [], isLoading: false }),
    actions: {
        async fetchAllData() {
            this.isLoading = true;
            try {
                const gRes = await api.getGraphData();
                const nodesObj = {};
                // Prepara dados para o v-network-graph
                gRes.data.nodes.forEach(n => nodesObj[n.id] = { name: n.name });
                const edgesObj = {};
                gRes.data.links.forEach((l, i) => edgesObj[`edge${i}`] = { source: l.source, target: l.target });
                
                this.nodes = nodesObj;
                this.edges = edgesObj;
                console.log('fetchAllData: nodes', this.nodes);
                console.log('fetchAllData: edges', this.edges);
                
                const aRes = await api.getAnalytics();
                this.analyticsData = aRes.data;
                console.log('fetchAllData: analytics', this.analyticsData);
            } catch (e) { console.error(e); } 
            finally { this.isLoading = false; }
        },
        async resetAndSeed() {
            this.isLoading = true;
            await api.seedDatabase(); // Dispara comando para a nuvem
            await this.fetchAllData();
        }
    }
});