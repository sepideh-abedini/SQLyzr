<template>
  <div class="config">
    <Toast />
    <Card>
      <template #title>
        <div class="text-center">
          <h1>Configuration</h1>
        </div>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 p-2 config-section">
            <div class="grid">
              <FormField class="md:col-6">
                <label class="field-label">Dataset:</label>
                <Select
                  v-model="config.dataset"
                  :options="dataset_options"
                  placeholder="Select Dataset"
                  class="w-full"
                />
              </FormField>
              <FormField class="md:col-6">
                <label class="field-label">Dataset Size:</label>
                <Select
                  v-model="config.dataset_size"
                  :options="size_options"
                  placeholder="Select Size"
                  class="w-full"
                />
              </FormField>
            </div>
            <FormField class="md:col-12">
              <label class="field-label">Models:</label>
              <div class="flex flex-wrap gap-3 mt-2">
                <MultiSelect
                  v-model="config.models"
                  display="chip"
                  :options="modelOptions"
                  filter
                  placeholder="Select Models"
                  class="w-full"
                />
              </div>
            </FormField>
            <div class="grid">
              <FormField class="md:col-3">
                <label class="field-label">Num Iterations:</label>
                <InputNumber v-model="config.itrs" :min="1" :max="5" fluid> </InputNumber>
              </FormField>
              <FormField class="md:col-6">
                <label class="field-label">Temperature:</label>
                <AutoComplete
                  :typeahead="false"
                  multiple
                  :suggestions="suggested_temps"
                  v-model="config.temps"
                  @complete="addTemp"
                  fluid
                />
              </FormField>
              <FormField class="md:col-3">
                <label class="field-label">Batch Mode:</label>
                <div class="flex align-items-center">
                  <ToggleSwitch v-model="config.batch" />
                  <span class="ml-2">{{ config.batch ? 'On' : 'Off' }}</span>
                </div>
              </FormField>
            </div>
            <FormField class="md:col-12">
              <label class="field-label">Charts:</label>
              <MultiSelect
                v-model="config.charts"
                display="chip"
                :options="chartOptions"
                filter
                placeholder="Select Charts"
                class="w-full"
              />
            </FormField>
          </div>
          <div class="col-12 md:col-6 p-2">

          </div>
        </div>
      </template>
      <template #footer>
        <div class="grid">
          <div class="col-12">
            <div class="flex justify-content-center gap-3 mt-3">
              <Button
                label="Save Configuration"
                icon="pi pi-save"
                @click="saveConfig"
                class="p-button-primary"
              />
              <Button
                label="Reset Config"
                icon="pi pi-refresh"
                @click="resetConfig"
                severity="secondary"
                outlined
              />
              <Button label="Run SQLyzr" icon="pi pi-play" @click="runSqlyzr" severity="primary" />
              <Button
                label="Kill SQLyzr"
                icon="pi pi-times"
                @click="killSqlyzr"
                severity="danger"
              />
            </div>
          </div>
          <div class="col-12">
            <div class="status-info mb-3">
              <div v-if="running" class="status-badge running">
                <i class="pi pi-spin pi-spinner mr-2"></i>
                <span>Running: {{ current_step }}</span>
              </div>
              <div v-else-if="success" class="status-badge completed">
                <i class="pi pi-check-circle mr-2"></i>
                <span>Completed</span>
              </div>
              <div v-else-if="fail" class="status-badge completed">
                <i class="pi pi-times-circle mr-2"></i>
                <span>Failed</span>
              </div>
              <div v-else class="status-badge idle">
                <i class="pi pi-pause mr-2"></i>
                <span>Not Running</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import Card from 'primevue/card'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import FormField from '@primevue/forms/formfield'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import Knob from 'primevue/knob'
import Toast from 'primevue/toast'
import { ToggleButton, AutoComplete } from 'primevue'

export default {
  components: {
    Card,
    Button,
    Checkbox,
    InputText,
    InputNumber,
    Toast,
    FormField,
    Select,
    MultiSelect,
    Slider,
    ToggleSwitch,
    Knob,
    ToggleButton,
    AutoComplete,
  },
  data() {
    return {
      p: 95,
      k: 10,
      running: false,
      loading: false,
      memory_percent: 0,
      memory_gb: 0,
      cpu_percent: 0,
      elapsed_time: 0,
      max_cpu: 0,
      success: false,
      fail: false,
      calculating: false,
      dataset_options: ['sqlyzr', 'spider', 'bird', 'beaver'],
      size_options: ['small'],
      config: {
        models: [],
        dataset: '',
        dataset_size: '',
        itrs: 1,
        temps: [0.2],
        batch: false,
        force: false,
        aug_per_sub_cat: 5,
        error_threshold: 90,
        etcr: 1.0,
        pipeline_config: {
          verify: false,
          predict: false,
          eval: false,
          transformers: false,
          augment: false,
          charts: false,
        },
        pipeline_status: {
          verify: false,
          predict: false,
          eval: false,
          charts: false,
          transformers: false,
          augment: false,
        },
        charts: [],
      },
      modelOptions: ['din', 'dail', 'simple'],
      suggested_temps: [0.0, 0.2, 0.5, 0.7, 1.0],
      chartOptions: [
        'Execution Accuracy',
        'Relaxed Execution Accuracy',
        'Exact Match',
        'Execution Time',
        'Token Usage',
        'Execution Time Consistency',
        'Execution Time Inconsistency',
        'Complexity Consistency',
        'Complexity Inconsistency',
        'Category Distribution',
        'Overall',
      ],
    }
  },
  computed: {
    sorted_pipeline_steps() {
      return ['verify', 'predict', 'eval', 'charts', 'transformers', 'augment']
    },

    finished() {
      for (let step of this.sorted_pipeline_steps) {
        if (this.pipeline_config[step]) {
          if (!this.pipeline_status[step]) {
            return false
          }
        }
      }
      return true
    },
    current_step() {
      let max_i = -1
      for (let i = 0; i < this.sorted_pipeline_steps.length; i++) {
        let step = this.sorted_pipeline_steps[i]
        if (this.pipeline_status[step]) max_i = i > max_i ? i : max_i
      }
      for (let i = max_i + 1; i < this.sorted_pipeline_steps.length; i++) {
        let step = this.sorted_pipeline_steps[i]
        if (this.pipeline_config[step]) {
          return step
        }
      }
      return null
    },
  },
  methods: {
    clear() {
      this.running = false
      this.success = false
      this.fail = false
    },

    async fetchStatus() {
      const data = await this.call_api('api/process/status', {}, false)
      const old_running = this.running
      this.running = data.running
      if (data.running) {
        this.memory_gb = data.memory_gb || 0
        this.cpu_percent = data.cpu_percent || 0
        this.elapsed_time = data.elapsed_time || 0
        this.memory_percent = data.memory_percent || 0
        this.max_cpu = data.cpu_percent_max || 0
      }
      if (old_running !== this.running) {
        if (data.return_code === 0) {
          this.success = true
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'SQLyzr completed successfully',
            life: 3000,
          })
        }
        if (data.return_code > 0) {
          this.fail = true
          this.$toast.add({
            severity: 'error',
            summary: 'Failure',
            detail: 'SQLyzr failed!',
            life: 3000,
          })
        }
      }

      if (this.success || this.fail) {
        this.finished = true
        this.clearInterval()
      }
    },
    setInterval() {
      this.fetchData()
      this.refreshInterval = setInterval(() => {
        this.fetchData()
      }, 1000)
    },
    async fetchPipelineStatus() {
      this.pipeline_status = await this.call_api('api/pipeline/status', {}, false)
      console.log(this.pipeline_status)
    },
    async fetchPipelineConfig() {
      const data = await this.call_api('api/config', {}, false)
      this.pipeline_config = data.pipeline
    },
    async fetchData() {
      await this.fetchPipelineConfig()
      await this.fetchStatus()
      await this.fetchPipelineStatus()
    },
    async runSqlyzr() {
      await this.call_api(`/api/process/run`, { method: 'POST' })
      this.clear()
      this.setInterval()
    },
    async killSqlyzr() {
      await this.call_api(`/api/process/kill`, { method: 'POST' })
      this.setInterval()
    },
    addTemp(event) {
      let newTemp = event.query
      this.config.temps.push(newTemp)
    },
    async fetchConfig() {
      this.loading = true
      this.error = null
      const data = await this.call_api('api/config')
      this.config = data

      if (this.config.temps && Array.isArray(this.config.temps)) {
        this.config.temps = this.config.temps.map((temp) => parseFloat(temp))
      } else {
        this.config.temps = []
      }

      if (!this.config.pipeline) {
        this.config.pipeline = {
          verify: false,
          predict: false,
          eval: false,
          transformers: false,
          augment: false,
          charts: false,
        }
      }
      if (!Array.isArray(this.config.charts)) {
        this.config.charts = []
      }
    },

    async saveConfig() {
      this.loading = true
      await this.call_api(
        'api/config',
        {
          method: 'POST',
          body: JSON.stringify(this.config),
        },
        true,
      )
      this.loading = false
    },
    async resetConfig() {
      const response = await this.call_api('api/error', { method: 'POST' })
      console.log(response)
    },

    async calculate() {
      this.calculating = true
      this.error = null

      try {
        const response = await this.call_api('api/utils/calcr', {
          method: 'POST',
          body: JSON.stringify({
            p: this.p,
            k: this.k,
          }),
        })

        if (response) {
          this.config.etcr = response.result

          this.$toast.add({
            severity: 'success',
            summary: 'Calculation Complete',
            detail: `R calculation is done`,
            life: 3000,
          })
        }
      } catch (error) {
        console.error('Error calculating:', error)
        this.error = error.message || 'An error occurred during calculation'

        this.$toast.add({
          severity: 'error',
          summary: 'Calculation Error',
          detail: this.error,
          life: 5000,
        })
      } finally {
        this.calculating = false
      }
    },
  },
  mounted() {
    this.fetchConfig()
    this.fetchData()
  },

  beforeUnmount() {
    console.log('Unmount')
    this.clearInterval()
  },
}
</script>
<style>
.config {
  padding: 2rem;
}

.config-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  height: 100%;
}

.field-label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #495057;
}

.pipeline-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
}

.pipeline-step {
  display: flex;
  align-items: center;
}

.pipeline-arrow {
  margin: 0 0.5rem;
  color: #6c757d;
}

.text-capitalize {
  text-transform: capitalize;
}

.p-togglebutton.p-button.p-highlight,
.p-togglebutton.p-button:not(.p-disabled):hover {
  background: #007bff; /* blue */
  border-color: #007bff; /* blue */
  color: #fff; /* white text */
}

@media (max-width: 768px) {
  .config {
    padding: 1rem;
  }

  .config-section {
    padding: 1rem;
  }
}
</style>
