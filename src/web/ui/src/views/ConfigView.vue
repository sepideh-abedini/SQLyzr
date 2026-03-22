<template>
  <div class="config">
    <Toast position="bottom-right" />
    <Card>
      <template #content>
        <div class="grid">
          <div class="md:col-6 p-2">
            <div class="config-section">
              <div class="grid">
                <FormField class="md:col-6">
                  <FloatLabel variant="in">
                    <label class="field-label">Workload:</label>
                    <Select
                      v-model="config.dataset"
                      :options="dataset_options"
                      placeholder="Select Workload"
                      class="w-full"
                      :disabled="dataset_lock_mode"
                    />
                  </FloatLabel>
                </FormField>
                <FormField class="md:col-6">
                  <FloatLabel variant="in">
                    <label class="field-label">Workload Size:</label>
                    <Select
                      v-model="config.dataset_size"
                      :options="size_options"
                      placeholder="Select Size"
                      class="w-full"
                      :disabled="dataset_lock_mode"
                    />
                  </FloatLabel>
                </FormField>
              </div>
              <div class="grid">
                <FormField class="md:col-6">
                  <label class="field-label">Text2SQL System:</label>
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
                <FormField class="md:col-6">
                  <FloatLabel variant="in">
                    <label class="field-label">Batch Mode:</label>
                    <div class="flex align-items-center">
                      <ToggleSwitch v-model="config.batch" />
                      <span class="ml-2">{{ config.batch ? 'On' : 'Off' }}</span>
                    </div>
                  </FloatLabel>
                </FormField>
              </div>
              <div class="grid">
                <FormField class="md:col-3">
                  <label class="field-label">Num Iterations:</label>
                  <InputNumber v-model="config.itrs" :min="1" :max="5" fluid> </InputNumber>
                </FormField>
                <FormField class="md:col-9">
                  <FloatLabel variant="in" class="w-full">
                    <label class="field-label">Temperature:</label>
                    <MultiSelect
                      v-model="config.temps"
                      display="chip"
                      :options="suggested_temps"
                      filter
                      placeholder="Select Temperatures"
                      class="w-full"
                      fluid
                    />
                  </FloatLabel>
                </FormField>
              </div>
              <div class="grid w-full">
                <FormField class="md:col-7">
                  <FloatLabel variant="in">
                    <label>Scaling Factors:</label>
                    <MultiSelect
                      class="w-full"
                      display="chip"
                      filter
                      placeholder="Select scales"
                      v-model="config.scales"
                      :options="avail_scales"
                    >
                    </MultiSelect>
                  </FloatLabel>
                </FormField>
                <FormField class="md:col-5">
                  <FloatLabel variant="in">
                    <label>Augmentation per Subcategory</label>
                    <InputText size="large" fluid v-model="config.aug_per_sub_cat" />
                  </FloatLabel>
                </FormField>
              </div>
              <div class="grid w-full">
                <FormField class="md:col-5">
                  <label class="field-label">Workload Versions [DEBUG]:</label>
                  <Select
                    display="chip"
                    filter
                    placeholder="Select version"
                    v-model="selected_version"
                    :options="config.dataset_versions"
                  />
                </FormField>
                <FormField class="md:col-6">
                  <FloatLabel variant="in">
                    <label class="field-label">Force Evaluation [DEBUG]:</label>
                    <div class="flex align-items-center">
                      <ToggleSwitch v-model="config.eval_force" />
                      <span class="ml-2">{{ config.eval_force ? 'On' : 'Off' }}</span>
                    </div>
                  </FloatLabel>
                </FormField>
                <!--                <RCalc />-->
              </div>
            </div>
          </div>
          <div class="md:col-6 p-2 config-section">
            <div class="config-section">
              <FormField class="mb-3">
                <label class="field-label">Error Threshold (Min Acceptable EA):</label>
                <div class="flex justify-content-center mt-2">
                  <Knob
                    value-color="red"
                    valueTemplate="{value}%"
                    :size="100"
                    :min="0"
                    :max="100"
                    v-model="errorThresholdPercent"
                  />
                </div>
              </FormField>
              <FormField v-if="config.pipeline" class="mb-3">
                <label class="field-label">Pipeline Steps:</label>
                <div class="pipeline-container mt-2">
                  <div
                    v-for="(step, index) in sorted_pipeline_steps"
                    :key="step"
                    class="pipeline-step"
                  >
                    <ToggleButton
                      v-model="config.pipeline[step]"
                      :on-label="step"
                      :off-label="step"
                      class="text-capitalize"
                      :disabled="step === 'scale' && !valid_scales"
                    />
                    <i
                      v-if="index < sorted_pipeline_steps.length - 1"
                      class="pi pi-arrow-right pipeline-arrow"
                    ></i>
                  </div>
                </div>
              </FormField>
              <FormField class="col-12 flex justify-content-center">
                <FloatLabel variant="in">
                  <label class="field-label">Pipeline Mode:</label>
                  <SelectButton
                    severity="success"
                    name="selection"
                    v-model="selected_pipeline_mode"
                    :options="['Evaluation', 'Augmentation', 'Scaling']"
                  />
                </FloatLabel>
              </FormField>
              <FormField class="mb-3">
                <label class="field-label">Plots:</label>
                <MultiSelect
                  v-model="config.charts"
                  display="chip"
                  :options="chartOptions"
                  filter
                  placeholder="Select Plots"
                  class="w-full"
                />
              </FormField>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="grid">
          <div class="col-12">
            <div class="flex justify-content-center gap-3 mt-3">
              <!--              <Button-->
              <!--                label="Save Configuration"-->
              <!--                icon="pi pi-save"-->
              <!--                @click="saveConfig"-->
              <!--                class="p-button-primary"-->
              <!--                :disabled="running"-->
              <!--              />-->
              <Button
                label="Cleanup"
                icon="pi pi-trash"
                v-tooltip="'Delete all output files'"
                @click="cleanup"
                severity="danger"
                :disabled="run_disabled"
              />
              <Button
                label="Default Config"
                icon="pi pi-refresh"
                @click="resetConfig"
                severity="secondary"
                v-tooltip="'Reset to default configuration'"
                :disabled="run_disabled"
              />
              <Button
                label="Clear Config"
                icon="pi pi-eraser"
                @click="clearConfig"
                severity="secondary"
                v-tooltip="'Clear config'"
                :disabled="run_disabled"
              />
              <Button
                label="Run SQLyzr"
                icon="pi pi-play"
                @click="runSqlyzr"
                severity="primary"
                :disabled="run_disabled"
              />
              <Button
                label="Stop Sqlyzr"
                icon="pi pi-times"
                @click="killSqlyzr"
                severity="danger"
                :disabled="!running"
              />
            </div>
          </div>
          <div class="col-12">
            <div class="status-info mb-3">
              <div v-if="running" class="status-badge running">
                <i class="pi pi-spin pi-spinner mr-2"></i>
                <span>Running </span>
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
import { ToggleButton, AutoComplete, SelectButton } from 'primevue'
import LogsView from '@/views/LogsView.vue'
import ChartsView from '@/views/ChartsView.vue'
import RCalc from '@/views/RCalc.vue'
import { toRaw } from 'vue'
import { saveAs } from '@primevue/core'
import isEqual from 'lodash/isEqual'

export default {
  components: {
    RCalc,
    LogsView,
    ChartsView,
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
    SelectButton,
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
      selected_pipeline_mode: 'Evaluation',
      dataset_options: ['aggregate', 'spider', 'bird', 'beaver'],
      size_options: ['small', 'full'],
      selected_version: null,
      initialized: false,
      verified_scales: [],
      valid_scales: false,
      config: {
        models: [],
        dataset: '',
        dataset_size: '',
        dataset_versions: [],
        scales: [],
        itrs: 1,
        temps: [0.2],
        batch: false,
        force: false,
        aug_per_sub_cat: 5,
        error_threshold: 90,
        etcr: 1.0,
        eval_force: false,
        pipeline: {
          predict: false,
          eval: false,
          augment: false,
          charts: false,
          transformers: false,
          scale: false,
        },
        pipeline_status: {
          predict: false,
          eval: false,
          charts: false,
          transformers: false,
          augment: false,
          scale: false,
        },
        charts: [],
      },
      modelOptions: ['din', 'dail', 'direct'],
      suggested_temps: [0.2, 0.5, 0.7, 1.0],
      chartOptions: [
        'Overall',
        'Execution Accuracy',
        // 'Relaxed Execution Accuracy',
        'Exact Match',
        'Execution Time',
        'Token Usage',
        'Execution Time Consistency',
        'Complexity Consistency',
        'Category Distribution',
        'Gold Execution Time',
      ],
    }
  },
  computed: {
    run_disabled() {
      return this.running || this.loading
    },
    dataset_lock_mode() {
      return this.config.pipeline.augment || this.config.pipeline.scale
    },
    errorThresholdPercent: {
      get() {
        return Math.round((this.config.error_threshold ?? 0) * 100)
      },
      set(val) {
        this.config.error_threshold = val / 100
      },
    },
    visible_scales() {
      return this.avail_scales.filter((v) => v !== 1)
    },
    avail_versions() {
      return [...Array(5).keys()].map((i) => `v${i}`)
    },
    avail_scales() {
      return [2, 3, 4, 5, 10, 20, 30, 40, 50, 100, 1000]
    },
    sorted_pipeline_steps() {
      return ['scale', 'predict', 'eval', 'charts', 'transformers', 'augment']
    },

    // finished() {
    //   for (let step of this.sorted_pipeline_steps) {
    //     if (this.config.pipeline?.[step]) {
    //       if (!this.pipeline_status?.[step]) {
    //         return false
    //       }
    //     }
    //   }
    //   return true
    // },
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
    clearConfig() {
      this.config = {
        models: [],
        dataset: '',
        dataset_size: '',
        dataset_versions: [],
        scales: [],
        itrs: 1,
        temps: [],
        batch: false,
        force: false,
        aug_per_sub_cat: 0,
        error_threshold: 50,
        etcr: 1.0,
        pipeline: {
          predict: false,
          eval: false,
          augment: false,
          charts: false,
          scale: false,
        },
      }
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
        console.log(data)
        const msg = data.msg ?? ''
        if (data.return_code === 0) {
          this.success = true
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: msg,
            sticky: true,
            // life: 3000,
          })
        }
        if (data.return_code > 0) {
          this.fail = true
          this.$toast.add({
            severity: 'error',
            summary: 'Failure',
            detail: msg,
            // life: 3000,
          })
        }
      }

      if (!this.running) {
        this.finished = true
        this.clearInterval()
        this.fetchConfig()
        const scales = this.scales
        this.scales = []
        this.scales = scales
      }
    },
    clearInterval() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
      }
    },
    async cleanup() {
      const res = await this.call_api('api/config/cleanup', { method: 'POST' })
      console.log(res)
      await this.fetchConfig()
      this.$toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Data cleared successfully.',
        life: 3000,
      })
    },
    setInterval() {
      this.fetchData()
      this.refreshInterval = setInterval(() => {
        this.fetchData()
      }, 1000)
    },
    async fetchPipelineStatus() {
      this.pipeline_status = await this.call_api('api/pipeline/status', {}, false)
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
      this.$toast.add({
        severity: 'success',
        summary: 'SQLyzr stopped!',
        life: 3000,
      })
    },
    addTemp(event) {
      let newTemp = event.query
      this.config.temps.push(newTemp)
      this.suggested_temps = [0.2, 0.5, 1.0]
    },
    async fetchConfig() {
      this.loading = true
      this.error = null
      const data = await this.call_api('api/config', {}, false)
      if (isEqual(data, this.config)) {
        this.loading = false
        return
      }
      Object.assign(this.config, data)

      if (this.config.temps && Array.isArray(this.config.temps)) {
        this.config.temps = this.config.temps.map((temp) => parseFloat(temp))
      } else {
        this.config.temps = []
      }

      if (!this.config.pipeline) {
        this.config.pipeline = {
          predict: false,
          eval: false,
          transformers: false,
          augment: false,
          charts: false,
          scale: false,
        }
      }
      if (!Array.isArray(this.config.charts)) {
        this.config.charts = []
      }
      const highest = this.config.dataset_versions
        .map((v) => parseInt(v.slice(1), 10))
        .reduce((a, b) => Math.max(a, b), -Infinity)
      this.selected_version = `v${highest}`
      this.loading = false
    },

    async saveConfig() {
      console.log('SAVING CONFIG:', this.config)
      this.loading = true
      await this.call_api(
        'api/config',
        {
          method: 'POST',
          body: JSON.stringify(this.config),
        },
        false,
      )
      this.loading = false
    },
    async resetConfig() {
      const response = await this.call_api('api/config/reset', { method: 'POST' }, true)
      await this.fetchConfig()
    },

    async getVerifiedScales() {
      return await this.call_api('api/db/factors', {}, false)
    },
  },
  watch: {
    config: {
      deep: true,
      async handler(newVal) {
        try {
          console.log('WATCHING CONFIG:', newVal)
          await this.saveConfig()
          // await this.fetchConfig()
          this.$toast.add({
            severity: 'success',
            summary: 'Configuration saved!',
            detail: '',
            life: 1000,
          })
        } catch (e) {
          console.error('Error saving configuration:', e, newVal)
          return
        }
      },
    },
    selected_version(newVal) {
      if (newVal && typeof newVal === 'string') {
        const index = parseInt(newVal.replace('v', ''), 10)
        if (!isNaN(index)) {
          this.config.dataset_versions = Array.from({ length: index + 1 }, (_, i) => `v${i}`)
        }
      }
    },
    'config.dataset_versions': {
      handler(newArr) {
        if (newArr && newArr.length > 0) {
          // Find the highest version in the current array to set the dropdown
          const highest = newArr
            .map((v) => parseInt(v.replace('v', ''), 10))
            .reduce((a, b) => Math.max(a, b), 0)
          this.selected_version = `v${highest}`
        }
      },
      deep: true,
    },

    'config.scales': {
      async handler(newArr) {
        const result = await this.getVerifiedScales()
        console.log('VERIFIED SCALES:', result)
        const verified_scales = result.verified_scales
        console.log('SCALES:', result.verified_scales, this.config.scales)
        const isSubset = (a, b) => a.every((v) => b.includes(v))
        const valid_scales = isSubset(this.config.scales, verified_scales)
        if (!valid_scales) {
          this.$toast.add({
            severity: 'warn',
            summary: 'Databases not scaled!',
            detail: 'To use the selected scaling factors, you must run the scaling pipeline first.',
            sticky: true,
          })
          this.selected_pipeline_mode = 'Scaling'
        }
        this.valid_scales = valid_scales
      },
      deep: true,
    },
    selected_pipeline_mode(newMode) {
      if (!this.config.pipeline) return

      const old_pipe = JSON.parse(JSON.stringify(this.config.pipeline))

      const flags = ['scale', 'predict', 'eval', 'charts', 'transformers', 'augment']
      flags.forEach((flag) => {
        this.config.pipeline[flag] = false
      })

      switch (newMode) {
        case 'Evaluation':
          this.config.pipeline.predict = true
          this.config.pipeline.eval = true
          this.config.pipeline.charts = true
          this.config.pipeline.transformers = true
          break
        case 'Augmentation':
          this.config.pipeline.augment = true
          break
        case 'Scaling':
          this.config.pipeline.scale = true
          break
        default:
          this.config.pipeline = old_pipe
      }
    },
    dataset_lock_mode(newVal) {
      if (newVal) {
        this.config.dataset = 'spider'
        this.config.dataset_size = 'small'
      }
    },
    'config.pipeline': {
      handler(newVal) {
        if (!newVal) return
        if (newVal.predict && newVal.eval && newVal.charts && !newVal.augment && !newVal.scale) {
          this.selected_pipeline_mode = 'Evaluation'
        } else if (
          newVal.augment &&
          !newVal.predict &&
          !newVal.eval &&
          !newVal.charts &&
          !newVal.scale
        ) {
          this.selected_pipeline_mode = 'Augmentation'
        } else if (
          newVal.scale &&
          !newVal.predict &&
          !newVal.eval &&
          !newVal.charts &&
          !newVal.augment
        ) {
          this.selected_pipeline_mode = 'Scaling'
        } else {
          this.selected_pipeline_mode = null
        }
      },
      deep: true,
    },
  },
  mounted() {
    this.fetchConfig()
    this.fetchData()
    this.initialized = true
  },

  beforeUnmount() {
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
