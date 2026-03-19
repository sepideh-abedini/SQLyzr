<template>
  <div class="p-2">
    <div class="flex gap-4 mt-1">
      <!--      <div class="w-full mb-4 flex gap-2">-->
      <!--        <Button label="Refresh Charts" icon="pi pi-refresh" @click="fetchCharts" />-->
      <!--      </div>-->

      <div class="grid md:col-6">
        <FormField class="md:col-6">
          <label class="field-label">Plot:</label>
          <Select
            v-model="selectedPlot"
            :options="avail_charts"
            placeholder="Select a plot"
            default-value="EA"
            class="w-full"
          />
        </FormField>
        <FormField class="md:col-6">
          <label class="field-label">Grouping</label>
          <Select
            v-model="selectedHue"
            :options="avail_hues"
            placeholder="Select a grouping"
            default-value="Model"
            class="w-full"
            :disabled="avail_hues.length === 0"
          />
        </FormField>
      </div>
      <div class="w-full mb-4 flex gap-2">
        <FloatLabel class="w-full" variant="in">
          <Select
            v-model="selectedChart"
            :options="avail_charts"
            filter
            option-label="label"
            option-value="value"
            placeholder="Select a chart"
            class="w-full"
            size="small"
          />
        </FloatLabel>
      </div>
    </div>
    <div v-if="selectedChart" class="chart-display">
      <h3>{{ selectedChart }}</h3>
      <div v-if="chartLoading" class="flex justify-content-center">
        <ProgressSpinner />
      </div>
      <div v-else-if="chartError" class="p-3">
        <Message severity="error">{{ chartError }}</Message>
      </div>
      <div v-else-if="avail_charts.length > 0" class="chart-image">
        <img :src="chartUrl" :alt="selectedChart" class="w-full" />
      </div>
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
import FloatLabel from 'primevue/floatlabel'

// const CHARTS = {
//   Overall: 'Model/overall__scores',
// }

export default {
  data() {
    return {
      loading: false,
      error: null,
      avail_charts: [],
      selectedChart: null,
      availableCharts: [],
      chartLoading: false,
      chartError: null,
      chartUrl: null,
    }
  },
  computed: {},
  methods: {
    async fetchCharts() {
      this.loading = true
      this.error = null

      try {
        const data = await this.call_api('api/charts')
        const chart_paths = data.avail_charts
        if (chart_paths.length > 0) {
          this.avail_charts = chart_paths.map((p) => {
            const label = p
              .split('/')
              .pop()
              .replace(/\.png$/, '')
              .replace(/__/g, ' ')
              .replace(/\b\w/g, (c) => c.toUpperCase())

            return { value: p, label }
          })
          this.selectedChart = this.avail_charts[1].value
        }
        console.log(this.avail_charts)
      } catch (error) {
        this.error = `Error loading charts: ${error.message}`
        console.error('Error loading charts:', error)
      } finally {
        this.loading = false
      }
    },

    async refreshChart() {
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
  watch: {
    selectedChart: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.refreshChart()
        }
      },
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
    Card,
    FloatLabel,
  },
}
</script>

<style>
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
