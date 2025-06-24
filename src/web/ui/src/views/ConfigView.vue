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
              <FormField class="md:col-12">
                <label class="field-label">Num Iterations:</label>
                <InputNumber
                  v-model="config.itrs"
                  showButtons
                  buttonLayout="horizontal"
                  :min="1"
                  :max="5"
                  w-full
                >
                  <template #incrementbuttonicon>
                    <span class="pi pi-plus" />
                  </template>
                  <template #decrementbuttonicon>
                    <span class="pi pi-minus" />
                  </template>
                </InputNumber>
              </FormField>
              <FormField class="md:col-6">
                <label class="field-label">Temperature:</label>
                <AutoComplete
                  :typeahead="false"
                  multiple
                  :suggestions="suggested_temps"
                  v-model="config.temps"
                  @complete="addTemp"
                />
              </FormField>
              <FormField class="md:col-6">
                <label class="field-label">Batch Mode:</label>
                <div class="flex align-items-center">
                  <ToggleSwitch v-model="config.batch" />
                  <span class="ml-2">{{ config.batch ? 'On' : 'Off' }}</span>
                </div>
              </FormField>
              <FormField class="mb-3">
                <label class="field-label">Number of Synthetic Examples Per Sub-Category:</label>
                <div class="flex align-items-center">
                  <InputText v-model.number="config.aug_per_sub_cat" class="w-3 mr-2" />
                  <Slider v-model="config.aug_per_sub_cat" :min="10" :max="1000" class="w-full" />
                </div>
              </FormField>
            </div>
          </div>

          <div class="col-12 md:col-6 p-2">
            <div class="config-section">
              <FormField class="mb-3">
                <label class="field-label">Error Threshold (Min Acceptable REA):</label>
                <div class="flex justify-content-center mt-2">
                  <Knob
                    value-color="red"
                    valueTemplate="{value}%"
                    :size="100"
                    :min="0"
                    :max="100"
                    v-model="config.error_threshold"
                  />
                </div>
              </FormField>
              <FormField class="mb-3">
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
                    />
                    <i
                      v-if="index < sorted_pipeline_steps.length - 1"
                      class="pi pi-arrow-right pipeline-arrow"
                    ></i>
                  </div>
                </div>
              </FormField>
              <FormField class="mb-3">
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
          </div>
        </div>
      </template>
      <template #footer>
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
import { API_BASE_URL } from '../config'

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
      loading: false,
      dataset_options: ['spider', 'bird', 'beaver', 'custom', 'agg'],
      size_options: ['small', 'all'],
      config: {
        models: [],
        dataset: '',
        dataset_size: '',
        itrs: 1,
        temps: [],
        batch: false,
        force: false,
        aug_per_sub_cat: 5,
        error_threshold: 90,
        pipeline: {
          verify: false,
          predict: false,
          eval: false,
          transformers: false,
          augment: false,
          charts: false,
        },
        charts: [],
      },
      modelOptions: ['din', 'dail'],
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
  },
  methods: {
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
  },
  mounted() {
    this.fetchConfig()
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
