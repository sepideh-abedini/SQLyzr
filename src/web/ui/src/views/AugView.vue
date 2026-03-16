<template>
  <div class="aug-view p-4">
    <Toast />
    <div class="grid m-0">
      <!-- Left Panel -->
      <div class="col-12 md:col-6 p-4">
        <div class="flex flex-column">
          <div class="flex flex-column gap-2">
            <label class="field-label">Dataset Size</label>
            <InputNumber v-model="datasetSize" disabled class="w-full mt-2" />
          </div>

          <div class="flex flex-column gap-2">
            <label class="field-label">Number of Synthetic Examples Per SubCategory:</label>
            <InputText v-model="config.aug_per_sub_cat" class="w-3 mr-2" />
            <Slider
              v-model="config.aug_per_sub_cat"
              :min="1"
              :max="100"
              :step="1"
              class="w-5 mt-4"
            />
          </div>

          <div class="flex flex-column gap-2">
            <label class="field-label">Error Threshold:</label>
            <InputText v-model="config.error_threshold" class="w-3 mr-2" />
            <Slider
              v-model="config.error_threshold"
              :min="0"
              :max="1"
              :step="0.01"
              class="w-5 mt-4"
            />
          </div>

          <div class="mt-auto flex justify-content-between pt-4 align-items-center">
            <div class="flex gap-3 align-items-center">
              <Button label="Run" icon="pi pi-play" @click="onRun" :disabled="isRunning" />
            </div>
            <Button
              label="Cleanup"
              icon="pi pi-trash"
              @click="onClear"
              severity="danger"
              :disabled="isRunning"
            />
            <Button label="Augment" icon="pi pi-plus" @click="onAugment" :disabled="isRunning" />
            <Button
              label="Reset"
              icon="pi pi-replay"
              @click="onReset"
              severity="warn"
              :disabled="isRunning"
            />
            <Button label="Save" icon="pi pi-save"  @click="saveConfig" />
          </div>

          <div v-if="status != 'idle'" class="mt-4">
            <Message v-if="status === 'running'" severity="info">Process is running...</Message>
            <Message v-else-if="status === 'completed'" severity="success">
              Process completed successfully.
            </Message>
            <Message v-else-if="status === 'no_process_found'" severity="secondary">
              No active process found.
            </Message>
            <Message v-else-if="status === 'error'" severity="error">
              Error checking process status.
            </Message>
          </div>
        </div>
        <div class="mt-auto flex justify-content-between pt-4 align-items-center">
          <ProgressSpinner
            v-if="isRunning"
            style="width: 30px; height: 30px"
            strokeWidth="8"
            animationDuration=".5s"
          />
        </div>
      </div>

      <!-- Right Panel -->
      <div class="col-12 md:col-6 p-4">
        <div class="w-full mb-4 flex gap-2">
          <h3>Available Charts</h3>
          <PSelect
            v-model="selectedPlot"
            :options="avail_charts"
            placeholder="Select a chart"
            default-value="EA"
            class="w-full md:w-56"
          />
        </div>
        <div class="h-full rounded-lg p-4">
          <img :src="getPlotUrl()" alt="Plot" class="plot" />
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

const charts = {
  EA: 'mean__relaxed__execution__accuracy_per__sub_category',
  'SubCategory Dist': 'sub_cat_count',
}

export default {
  name: 'AugView',
  mixins: [apiMixin],
  data() {
    return {
      datasetSize: 0,
      isRunning: false,
      status: 'idle',
      statusInterval: null as number | null,
      selectedPlot: 'EA',
      config: {
        error_threshold: 0.9,
        aug_per_sub_cat: 10,
      },
      plotTimestamp: Date.now(),
      onDoneCallback: null as (() => void) | null,
    }
  },
  computed: {
    avail_charts() {
      const keys = Object.keys(charts)
      console.log(keys)
      return Object.keys(charts)
    },
  },
  methods: {
    refreshPlot() {
      this.plotTimestamp = Date.now()
    },
    getPlotUrl() {
      const chart_name = charts[this.selectedPlot]
      return `${API_BASE_URL}/api/aug/plot/${chart_name}?ts=${this.plotTimestamp}`
    },

    async checkStatus() {
      try {
        const res = await this.call_api('api/aug/status')
        if (res && res.status === 'running') {
          this.isRunning = true
          this.status = 'running'
          if (!this.statusInterval) {
            this.startPolling()
          }
        } else {
          if (this.isRunning) {
            this.status = 'completed'
          }
          this.refreshPlot()
          this.isRunning = false
          this.stopPolling()
        }
      } catch (error) {
        console.error('Error checking status:', error)
        this.status = 'error'
        this.isRunning = false
        this.stopPolling()
      }
    },

    async onRun() {
      const res = await this.call_api('api/aug/start/sqlyzr', { method: 'POST' })
      this.onDoneCallback = () => {
        this.selectedPlot = 'SubCategory Dist'
      }
      await this.checkStatus()
    },

    async onClear() {
      const res = await this.call_api('api/aug/clear', { method: 'POST' })
      console.log(res)
      await this.fetchConfig()
      this.$toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Data cleared successfully.',
        life: 3000,
      })
    },

    async onAugment() {
      const res = await this.call_api('api/aug/start/aug', { method: 'POST' })
      this.onDoneCallback = () => {
        this.selectedPlot = 'SubCategory Dist'
      }
      await this.checkStatus()
    },

    async onReset() {
      const res = await this.call_api('api/aug/start/reset', { method: 'POST' })
      await this.checkStatus()
      this.onDoneCallback = () => {
        this.selectedPlot = 'SubCategory Dist'
      }
    },
    startPolling() {
      if (this.statusInterval) return
      this.statusInterval = window.setInterval(() => {
        this.checkStatus()
      }, 2000)
    },
    stopPolling() {
      if (this.statusInterval) {
        clearInterval(this.statusInterval)
        this.statusInterval = null
        if (this.onDoneCallback) {
          this.onDoneCallback()
          this.onDoneCallback = null
        }
      }
    },

    async fetchConfig() {
      const stats = await this.call_api('api/aug/stats')
      this.datasetSize = stats.dataset_size
      const data = await this.call_api('api/aug/config')
      this.config = data
      console.log(this.config.error_threshold)
      this.refreshPlot()
    },

    async saveConfig() {
      await this.call_api(
        'api/aug/save',
        {
          method: 'POST',
          body: JSON.stringify(this.config),
        },
        true,
      )
    },
  },
  watch: {
    selectedPlot(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.refreshPlot()
      }
    },
  },
  mounted() {
    this.fetchConfig()
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
    PSelect: Select,
    Button,
    Message,
  },
}
</script>

<style scoped>
.plot {
  width: 100%;
}
</style>
