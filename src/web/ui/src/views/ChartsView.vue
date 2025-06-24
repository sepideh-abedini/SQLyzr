<template>
  <div class="charts">
    <Toast />

    <Message v-if="error" severity="error">{{ error }}</Message>

    <ProgressSpinner v-if="loading" class="my-4" />

    <Card v-else>
      <template #title>
        <div class="text-center">
          <h1>Charts</h1>
        </div>
      </template>
      <div class="flex gap-4 mt-1">
        <div class="w-full mb-4 flex gap-2">
          <Button label="Refresh Charts" icon="pi pi-refresh" @click="fetchCharts" />
        </div>
        <div class="w-full mb-4 flex gap-2">
          <h3>Available Charts</h3>
          <Select
            v-model="selectedChart"
            :options="charts"
            filter
            placeholder="Select a chart"
            default-value="overall.png"
            @update:modelValue="selectChart"
            class="w-full md:w-56"
          />
        </div>
      </div>
    </Card>
    <div v-if="selectedChart" class="chart-display">
      <h3>{{ selectedChart }}</h3>
      <div v-if="chartLoading" class="flex justify-content-center">
        <ProgressSpinner />
      </div>
      <div v-else-if="chartError" class="p-3">
        <Message severity="error">{{ chartError }}</Message>
      </div>
      <div v-else class="chart-image">
        <img :src="chartUrl" :alt="selectedChart" class="w-full" />
      </div>
    </div>
    <div v-else class="flex justify-content-center align-items-center h-full">
      <Message severity="info">Select a chart from the list to view</Message>
    </div>
  </div>
</template>

<script>
import Button from 'primevue/button'
import Select from 'primevue/select'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import Card from 'primevue/card'
import { API_BASE_URL } from '../config'

export default {
  data() {
    return {
      loading: false,
      error: null,
      charts: [],
      selectedChart: null,
      chartLoading: false,
      chartError: null,
      chartUrl: null,
    }
  },
  methods: {
    async fetchCharts() {
      this.loading = true
      this.error = null

      try {
        const data = await this.call_api('api/charts')
        this.charts = data.charts || []
      } catch (error) {
        this.error = `Error loading charts: ${error.message}`
        console.error('Error loading charts:', error)
      } finally {
        this.loading = false
      }
    },

    async selectChart() {
      this.chartLoading = true
      this.chartError = null
      try {
        this.chartUrl = `${API_BASE_URL}/api/charts/${encodeURIComponent(this.selectedChart)}`

        const img = new Image()
        img.onload = () => {
          this.chartLoading = false
        }
        img.onerror = () => {
          this.chartError = `Failed to load chart: ${this.selectedChart}`
          this.chartLoading = false
        }
        img.src = this.chartUrl
      } catch (error) {
        this.chartError = `Error loading chart: ${error.message}`
        this.chartLoading = false
      }
    },
  },
  mounted() {
    this.fetchCharts()
  },
  components: {
    Button,
    Message,
    ProgressSpinner,
    Toast,
    Select,
    Card
  },
}
</script>

<style>
.charts {
  padding: 2rem;
}

.charts h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.charts h3 {
  margin-bottom: 1rem;
  font-weight: 600;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow:
    0 2px 1px -1px rgba(0, 0, 0, 0.2),
    0 1px 1px 0 rgba(0, 0, 0, 0.14),
    0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.chart-display {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  min-height: 400px;
}

.chart-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (max-width: 768px) {
  .charts {
    padding: 1rem;
  }

  .chart-display {
    margin-top: 1rem;
  }
}
</style>
