<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { useSocialStore } from '../stores/socialStore'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
const store = useSocialStore()
const chartData = computed(() => ({
  labels: store.analyticsData.map(d => d.name),
  datasets: [{ 
    label: 'Influência (Conexões)', 
    data: store.analyticsData.map(d => d.followers), 
    backgroundColor: '#10b981',
    borderRadius: 5
  }]
}))
const options = { responsive: true, maintainAspectRatio: false }
</script>
<template>
  <div class="chart"><Bar :data="chartData" :options="options" v-if="store.analyticsData.length" /></div>
</template>
<style scoped>.chart { height: 300px; padding: 15px; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; }</style>