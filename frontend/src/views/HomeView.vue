<script setup>
import { onMounted } from 'vue'
import { useSocialStore } from '../stores/socialStore'
import GraphNetwork from '../components/GraphNetwork.vue'
import DashboardChart from '../components/DashboardChart.vue'
const store = useSocialStore()
onMounted(() => { store.fetchAllData() })
</script>

<template>
  <div class="container">
    <header>
      <h1>Cloud Graph Dashboard</h1>
      <button @click="store.resetAndSeed" :disabled="store.isLoading" class="btn">
        {{ store.isLoading ? 'Sincronizando com a Nuvem...' : 'Resetar Dados na Nuvem' }}
      </button>
    </header>
    <div class="grid">
      <div class="card">
        <h2>Visualização de Grafo</h2>
        <GraphNetwork />
      </div>
      <div class="card">
        <h2>Analytics (Centralidade)</h2>
        <DashboardChart />
      </div>
    </div>
  </div>
</template>
<style scoped>
.container { padding: 2rem; max-width: 1400px; margin: 0 auto; font-family: 'Segoe UI', sans-serif; background: #f3f4f6; min-height: 100vh; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
h1 { color: #1f2937; }
.grid { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
.card { background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
h2 { color: #4b5563; margin-bottom: 1rem; font-size: 1.2rem; }
.btn { padding: 0.75rem 1.5rem; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
.btn:hover { background: #1d4ed8; }
.btn:disabled { background: #9ca3af; cursor: not-allowed; }
@media (max-width: 1024px) { .grid { grid-template-columns: 1fr; } }
</style>