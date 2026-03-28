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
                  <label class="field-label">Workload</label>
                  <Select
                    v-model="config.dataset"
                    :options="dataset_options"
                    placeholder="Select Workload"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                    :disabled="dataset_lock_mode"
                  />
                </FormField>
                <FormField class="md:col-6">
                  <label class="field-label">Workload Sample</label>
                  <Select
                    v-model="config.dataset_size"
                    :options="dataset_size_options[config.dataset]"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select Size"
                    class="w-full"
                    :disabled="dataset_lock_mode"
                  />
                </FormField>
              </div>
              <div class="grid">
                <FormField class="md:col-9">
                  <label class="field-label">Text2SQL Model</label>
                  <div class="flex flex-wrap gap-3 mt-2">
                    <MultiSelect
                      v-model="config.models"
                      display="chip"
                      :options="modelOptions"
                      filter
                      optionLabel="label"
                      optionValue="value"
                      placeholder="Select Models"
                      class="w-full"
                    />
                  </div>
                </FormField>
                <FormField class="md:col-3 h-full">
                  <label class="field-label">Batch Mode</label>
                  <div class="flex align-items-center h-full">
                    <ToggleSwitch v-model="config.batch" />
                    <span class="ml-2">{{ config.batch ? 'On' : 'Off' }}</span>
                  </div>
                </FormField>
              </div>
              <div class="grid">
                <FormField class="md:col-3">
                  <label class="field-label">Num Iterations</label>
                  <InputNumber v-model="config.itrs" :min="1" :max="5" fluid> </InputNumber>
                </FormField>
                <FormField class="md:col-9">
                  <label class="field-label">Temperature</label>
                  <Chips
                    v-tooltip.top="{ value: 'Enter a number followed by a comma', autoHide: true }"
                    v-model="config.temps"
                    separator=","
                    placeholder="Enter temperatures"
                    class="w-full chips"
                    fluid
                  />
                </FormField>
              </div>
              <div class="grid">
                <FormField class="md:col-7">
                  <label class="field-label">Scaling Factors</label>
                  <MultiSelect
                    class="w-full"
                    display="chip"
                    filter
                    placeholder="Select scales"
                    v-model="config.scales"
                    :options="avail_scales"
                  >
                  </MultiSelect>
                </FormField>
                <FormField class="md:col-5">
                  <label class="field-label">Augmentation per Subcategory</label>
                  <InputText fluid v-model="config.aug_per_sub_cat" />
                </FormField>
              </div>
              <div class="grid w-full">
                <FormField class="md:col-3">
                  <label class="field-label">Workload Version</label>
                  <Select
                    display="chip"
                    filter
                    placeholder="Select version"
                    v-model="selected_version"
                    :options="config.dataset_versions"
                  />
                </FormField>
                <FormField class="md:col-3">
                  <FloatLabel variant="in">
                    <label class="field-label">Force Evaluation</label>
                    <div class="flex align-items-center">
                      <ToggleSwitch v-model="config.eval_force" />
                      <span class="ml-2">{{ config.eval_force ? 'On' : 'Off' }}</span>
                    </div>
                  </FloatLabel>
                </FormField>
                <FormField class="md:col-6">
                  <FloatLabel variant="in">
                    <label class="field-label">Upload Workload</label>
                    <WorkloadUpload />
                  </FloatLabel>
                </FormField>
                <!--                <RCalc />-->
              </div>
              <div class="w-full flex justify-content-center">
                <Message
                  v-if="config_updated"
                  icon="pi pi-check"
                  :life="3000"
                  size="small"
                  severity="success"
                  variant="outlined"
                  >Configuration Updated!</Message
                >
              </div>
            </div>
          </div>
          <div class="md:col-6 p-2">
            <div class="config-section">
              <FormField class="mb-3">
                <label class="field-label">Error Threshold (Min Acceptable EA)</label>
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
                <label class="field-label">Pipeline Steps</label>
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
                  <label class="field-label">Pipeline Mode</label>
                  <SelectButton
                    severity="success"
                    name="selection"
                    v-model="selected_pipeline_mode"
                    :options="['Evaluation', 'Augmentation', 'Scaling']"
                  />
                </FloatLabel>
              </FormField>
              <FormField class="mb-3">
                <label class="field-label">Plots</label>
                <MultiSelect
                  v-model="config.plots"
                  display="chip"
                  :options="chartOptions"
                  optionLabel="label"
                  optionValue="value"
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
import isEqual from 'lodash/isEqual'
import Message from 'primevue/message'
import WorkloadUpload from '@/views/WorkloadUpload.vue'
import Dialog from 'primevue/dialog'
import Chips from 'primevue/chips'

export default {
  components: {
    WorkloadUpload,
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
    Message,
    Dialog,
    Chips,
  },
  data() {
    return {
      p: 95,
      k: 10,
      valid: true,
      config_updated: false,
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
      dataset_options: [
        {
          label: 'SQLyzr',
          value: 'sqlyzr',
        },
        {
          label: 'Custom',
          value: 'custom',
        },
      ],
      dataset_size_options: {
        sqlyzr: [
          {
            label: 'Sample 1',
            value: 's1',
          },
          {
            label: 'Sample 2',
            value: 's2',
          },
          {
            label: 'Sample 3',
            value: 's3',
          },
          {
            label: 'Full',
            value: 'full',
          },
          {
            label: 'Aligned',
            value: 'aligned',
          },
        ],
        custom: [
          {
            label: 'Full',
            value: 'full',
          },
        ],
      },
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
          plots: false,
          analysis: false,
          scale: false,
        },
        pipeline_status: {
          predict: false,
          eval: false,
          plots: false,
          analysis: false,
          augment: false,
          scale: false,
        },
        plots: [],
      },
      modelOptions: [
        { label: 'DIN-SQL', value: 'din' },
        { label: 'DAIL-SQL', value: 'dail' },
        { label: 'Direct-LLM', value: 'direct' },
      ],
      suggested_temps: [0.2, 0.5, 0.7, 1.0],
      chartOptions: [
        { label: 'Overall', value: 'Overall' },
        { label: 'Execution Accuracy (EA)', value: 'Execution Accuracy' },
        // { label: 'Relaxed Execution Accuracy', value: 'Relaxed Execution Accuracy' },
        { label: 'Exact Match (EM)', value: 'Exact Match' },
        // { label: 'Execution Time', value: 'Execution Time' },
        { label: 'Token Usage (TU)', value: 'Token Usage' },
        { label: 'Execution Time Consistency (ETC)', value: 'Execution Time Consistency' },
        { label: 'Complexity Consistency (CC)', value: 'Complexity Consistency' },
        { label: 'Category Distribution', value: 'Category Distribution' },
        { label: 'Gold Execution Time', value: 'Gold Execution Time' },
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
      return ['scale', 'predict', 'eval', 'plots', 'analysis', 'augment']
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
    on_temp_change(event) {
      console.log('Temp change:', event.value)
    },
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
          plots: false,
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
          analysis: false,
          augment: false,
          plots: false,
          scale: false,
        }
      }
      if (!Array.isArray(this.config.plots)) {
        this.config.plots = []
      }
      const highest = this.config.dataset_versions
        .map((v) => parseInt(v.slice(1), 10))
        .reduce((a, b) => Math.max(a, b), -Infinity)
      this.selected_version = `v${highest}`
      this.loading = false
    },
    async saveConfig() {
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
    'config.dataset': {
      deep: true,
      async handler(newVal, oldVal) {
        this.config.dataset_size = this.dataset_size_options[this.config.dataset][0].value
      },
    },
    config: {
      deep: true,
      async handler(newVal, oldVal) {
        console.log('Config changed:', newVal)
        if (newVal.dataset !== oldVal.dataset) {
          console.log('Config changed:', newVal)
        }
        try {
          if (this.valid) {
            this.config_updated = false
            await this.saveConfig()
            this.config_updated = true
          }
          // await this.fetchConfig()
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
        const verified_scales = result.verified_scales
        const isSubset = (a, b) => a.every((v) => b.includes(v))
        const valid_scales = isSubset(this.config.scales, verified_scales)
        if (!valid_scales) {
          this.$toast.add({
            severity: 'warn',
            summary: 'Databases not scaled!',
            detail: 'To use the selected scaling factors, scaling step must be enabled.',
            life: 5000,
          })
          // this.config.pipeline.scale = true
        }
        this.valid_scales = valid_scales
      },
      deep: true,
    },
    selected_pipeline_mode(newMode) {
      if (!this.config.pipeline) return

      const old_pipe = JSON.parse(JSON.stringify(this.config.pipeline))

      const flags = ['scale', 'predict', 'eval', 'plots', 'analysis', 'augment']
      flags.forEach((flag) => {
        this.config.pipeline[flag] = false
      })

      switch (newMode) {
        case 'Evaluation':
          this.config.pipeline.predict = true
          this.config.pipeline.eval = true
          this.config.pipeline.plots = true
          this.config.pipeline.analysis = true
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
        this.config.dataset = 'sqlyzr'
        this.config.dataset_size = 's1'
      }
    },
    'config.pipeline': {
      handler(newVal) {
        if (!newVal) return
        if (newVal.predict && newVal.eval && newVal.plots && !newVal.augment && !newVal.scale) {
          this.selected_pipeline_mode = 'Evaluation'
        } else if (
          newVal.augment &&
          !newVal.predict &&
          !newVal.eval &&
          !newVal.plots &&
          !newVal.scale
        ) {
          this.selected_pipeline_mode = 'Augmentation'
        } else if (
          newVal.scale &&
          !newVal.predict &&
          !newVal.eval &&
          !newVal.plots &&
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

.p-multiselect,
.p-inputtext,
.p-inputchips-input
{
  height: 40px;
  display: flex;
  align-items: center;
}

.p-select {
  height: 40px;
  display: flex;
  align-items: center;
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
