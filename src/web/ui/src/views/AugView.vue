<template xmlns="http://www.w3.org/1999/html">
  <div class="aug-view p-4">
    <Toast />
    <div class="grid">
      <div class="grid md:col-6">
        <FormField class="md:col-6">
          <label class="field-label">Plot Type</label>
          <Select
            v-model="selectedHue"
            :options="avail_hues"
            placeholder="Select a type"
            class="w-full"
          />
        </FormField>
        <FormField v-if="selectedHue" class="md:col-6">
          <label class="field-label">Plot:</label>
          <Select
            v-model="selectedPlot"
            :options="avail_plots"
            placeholder="Select a plot"
            class="w-full"
            :disabled="avail_plots.length === 0"
          >
            <template #option="slotProps">
              {{ formatPlotName(slotProps.option) }}
            </template>
            <template #value="slotProps">
              {{ formatPlotName(slotProps.value) }}
            </template>
          </Select>
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

export default {
  name: 'AugView',
  mixins: [apiMixin],
  data() {
    return {
      db_stats: [{ db_id: 'foo', scale: 2 }],
      plot_dict: {},
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
    plot_url() {
      return `${API_BASE_URL}/api/aug/plot/${this.selectedHue}/${this.selectedPlot}?ts=${this.plotTimestamp}`
    },
    disabled() {
      return this.isRunning || this.modified
    },
    avail_hues() {
      return Object.keys(this.plot_dict)
    },
    avail_plots() {
      console.log(this.selectedHue)
      if (this.selectedHue) return this.plot_dict[this.selectedHue]
      else return []
    },
  },
  methods: {
    formatPlotName(str: string) {
      return str
        .replace(/\.[^/.]+$/, '')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (l) => l.toUpperCase())
    },
    async fetchCharts() {
      try {
        const data = await this.call_api('api/charts')
        const avail_charts = data.avail_charts
        this.plot_dict = avail_charts
        console.log(avail_charts)
        if (Object.keys(avail_charts).length) {
          this.selectedHue = Object.keys(avail_charts)[0]
          if (this.plot_dict[this.selectedHue].length > 0)
            this.selectedPlot = this.plot_dict[this.selectedHue][0]
        }
      } catch (error) {
        console.error('Error fetching charts:', error)
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
    selectedHue(newVal, oldVal) {
      if (this.plot_dict[this.selectedHue].length > 0)
        this.selectedPlot = this.plot_dict[this.selectedHue][0]
      else this.selectedPlot = null
    },
    selectedPlot(newVal, oldVal) {
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
