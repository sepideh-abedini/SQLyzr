<template xmlns="http://www.w3.org/1999/html">
  <div class="aug-view p-4">
    <Toast />
    <div class="grid">
      <div class="grid md:col-6">
        <AugConfigView ref="augRef" v-model="modified" />
        <div class="grid mt-5 w-full">
          <div class="md:col-3 flex flex-column gap-2">
            <Button
              label="Run"
              icon="pi pi-play"
              @click="onRun"
              v-tooltip="getTooltip('Run SQLyzr on the latest workload version.')"
              :disabled="disabled"
            />
            <Button
              label="Cleanup"
              icon="pi pi-trash"
              v-tooltip="'Delete all output files'"
              @click="onClear"
              severity="danger"
            />
          </div>
          <div class="md:col-3 flex flex-column gap-2">
            <Button
              label="Scale"
              v-tooltip="getTooltip('Scale all database by the selected factors.')"
              icon="pi pi-window-maximize"
              @click="onScale"
              :disabled="disabled"
            />
          </div>
          <div class="md:col-3 flex flex-column gap-2">
            <Button
              label="Augment"
              v-tooltip="getTooltip('')"
              icon="pi pi-forward"
              @click="onAugment"
              :disabled="disabled"
            />
            <Button
              label="Reset"
              icon="pi pi-backward"
              v-tooltip="getTooltip('Delete all workload versions and revert to v0.')"
              @click="onReset"
              severity="warn"
              :disabled="disabled"
            />
          </div>
        </div>
        <div class="md:col-6">
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
          <div class="mt-auto flex justify-content-between pt-4 align-items-center">
            <ProgressSpinner
              v-if="isRunning"
              style="width: 30px; height: 30px"
              strokeWidth="8"
              animationDuration=".5s"
            />
          </div>
        </div>
        <div v-if="0" class="col-12 mt-4 w-full">
          <DataTable
            :value="db_stats"
            class="p-datatable-sm"
            stripedRows
            :sortOrder="1"
            responsiveLayout="scroll"
          >
            <Column field="db_id" header="Table Name" sortable />
            <Column
              v-bind:key="scale"
              v-for="scale in config.scales"
              :field="`x${scale}`"
              :header="`x${scale}`"
              sortable
            />
          </DataTable>
        </div>
      </div>

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
      selectedPlot: null,
      selectedHue: null,
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
      console.log(keys)
      return Object.keys(charts)
    },
    avail_versions() {
      return [...Array(5).keys()].map((i) => `v${i}`)
    },
    avail_datasets() {
      return ['aug']
    },
    avail_models() {
      return ['simple', 'simple_v2']
    },
    avail_scales() {
      return [1, 2, 5, 10]
    },
    plot_url() {
      const chart_name = charts[this.selectedPlot]?.file
      if (this.selectedHue)
        return `${API_BASE_URL}/api/aug/plot/${this.selectedHue}/${chart_name}?ts=${this.plotTimestamp}`
      else return `${API_BASE_URL}/api/aug/plot/${chart_name}?ts=${this.plotTimestamp}`
    },
    disabled() {
      return this.isRunning || this.modified
    },
  },
  methods: {
    getTooltip(msg: string) {
      if (this.disabled) return 'Save configuration changes before running.'
      else return msg
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

    async onRun() {
      const res = await this.call_api('api/aug/start/sqlyzr', { method: 'POST' })
      this.onDoneCallback = () => {
        this.selectedPlot = 'Overall'
      }
      await this.checkStatus()
    },

    async onScale() {
      const res = await this.call_api('api/aug/start/scale', { method: 'POST' })
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
        this.fetchConfig()
      }
      await this.checkStatus()
    },

    async onReset() {
      const res = await this.call_api('api/aug/start/reset', { method: 'POST' })
      this.onDoneCallback = () => {
        this.selectedPlot = 'SubCategory Dist'
        this.fetchConfig()
      }
      await this.checkStatus()
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
      await this.fetchConfig()
    },

    async fetchConfig() {
      const stats = await this.call_api('api/aug/stats')
      this.db_stats = stats.db_stats
      this.$refs.augRef.fetchConfig()
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
