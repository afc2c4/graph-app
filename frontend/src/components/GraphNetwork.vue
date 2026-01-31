<script setup>
import { VNetworkGraph } from "v-network-graph"
import "v-network-graph/lib/style.css"
import { useSocialStore } from '../stores/socialStore'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

const store = useSocialStore()
const { nodes, edges } = storeToRefs(store)
const hasNodes = computed(() => Object.keys(nodes.value || {}).length > 0)
const configs = {
  node: { 
    label: { visible: true, text: "name" }, 
    normal: { radius: 25, color: "#4f46e5" } // Azul Indigo
  },
  edge: { 
    marker: { target: { type: "arrow" } }, 
    normal: { color: "#94a3b8", width: 2 } 
  }
}
</script>
<template>
  <div class="graph">
    <div v-if="!hasNodes" class="empty">Sem dados para exibir</div>
    <v-network-graph v-else :nodes="nodes" :edges="edges" :configs="configs" />
  </div>
</template>
<style scoped>.graph { height: 400px; border: 1px solid #e5e7eb; background: #fff; border-radius: 8px; }
.empty { display:flex; align-items:center; justify-content:center; height:100%; color:#6b7280; font-weight:600; }</style>