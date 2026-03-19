<template xmlns="http://www.w3.org/1999/html">
  <div class="aug-view p-4">
    <Toast />
    <div class="grid">
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
        <div v-if="selectedPlot" class="h-full rounded-lg p-4">
          <img :src="plot_url" class="plot" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Toast from 'primevue/toast'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Slider from 'primevue/slider'
import Select from 'primevue/select'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import apiMixin from '@/api_mixin'
import { API_BASE_URL } from '@/config'
import FormField from '@primevue/forms/formfield'
import MultiSelect from 'primevue/multiselect'
import DataTable from 'primevue/datatable'
import FloatLabel from 'primevue/floatlabel'
import Column from 'primevue/column'
import AugConfigView from '@/views/AugConfigView.vue'

const charts = {
  REA: {
    file: 'mean__relaxed__execution__accuracy_per__sub_category',
    vars: ['Model', 'dst_ver'],
  },
  Overall: {
    file: 'overall__scores',
    vars: ['Model', 'dst_ver'],
  },
  'Gold Exec Time': { file: 'mean__gold__execution__time_per_scale', vars: ['Model', 'dst_ver'] },
  'SubCategory Dist': {
    file: 'sub_cat_count',
    vars: [],
  },
}

export default {
  name: 'AugView',
  mixins: [apiMixin],
  data() {
    return {
      db_stats: [{ db_id: 'foo', scale: 2 }],
      datasetSize: 0,
      isRunning: false,
      status: 'idle',
      statusInterval: null as number | null,
      selectedHue: null,
      selectedPlot: null,
      config: {
        error_threshold: 0.9,
        aug_per_sub_cat: 10,
        models: ['simple'],
        dataset: 'aug',
        scales: [1],
        dataset_versions: ['v0'],
      },
      plotTimestamp: Date.now(),
      onDoneCallback: null as (() => void) | null,
      modified: false,
      avail_hues: [],
    }
  },
  computed: {
    avail_charts() {
      const keys = Object.keys(charts)
      return Object.keys(charts)
    },
    plot_url() {
      const chart_name = charts[this.selectedPlot]?.file
      if (this.selectedHue)
        return `${API_BASE_URL}/api/aug/plot/${this.selectedHue}/${chart_name}?ts=${this.plotTimestamp}`
      else
        return `${API_BASE_URL}/api/aug/plot/${chart_name}?ts=${this.plotTimestamp}`
    },
    disabled() {
      return this.isRunning || this.modified
    },
  },
  methods: {
    async fetchCharts() {
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
      } catch (error) {
      } finally {
        this.loading = false
      }
    },
    refreshPlot() {
      this.plotTimestamp = Date.now()
    },
    async checkStatus() {
      try {
        const res = await this.call_api('api/aug/status', {}, false)
        if (res && res.status === 'running') {
          this.isRunning = true
          this.status = 'running'
          if (!this.statusInterval) {
            await this.startPolling()
          }
        } else {
          if (this.isRunning) {
            this.status = 'completed'
          }
          this.refreshPlot()
          this.isRunning = false
          await this.stopPolling()
        }
      } catch (error) {
        console.error('Error checking status:', error)
        this.status = 'error'
        this.isRunning = false
        await this.stopPolling()
      }
    },

    async startPolling() {
      if (this.statusInterval) return
      this.statusInterval = window.setInterval(() => {
        this.checkStatus()
      }, 2000)
    },
    async stopPolling() {
      if (this.statusInterval) {
        clearInterval(this.statusInterval)
        this.statusInterval = null
        if (this.onDoneCallback) {
          this.onDoneCallback()
          this.onDoneCallback = null
        }
      }
      await this.refreshPlot()
    },
  },
  watch: {
    selectedPlot(newVal, oldVal) {
      if (newVal !== null) {
        this.avail_hues = charts[newVal].vars
        if (this.avail_hues.length === 0) {
          this.selectedHue = null
        } else {
          this.selectedHue = this.avail_hues[0]
        }
      }
      this.refreshPlot()
    },
  },
  mounted() {
    this.fetchCharts()
    this.checkStatus()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  components: {
    Toast,
    InputNumber,
    Slider,
    ProgressSpinner,
    InputText,
    Select,
    Button,
    Message,
    FormField,
    MultiSelect,
    DataTable,
    FloatLabel,
    Column,
    AugConfigView,
  },
}
</script>

<style scoped>
.plot {
  width: 100%;
}
</style>
