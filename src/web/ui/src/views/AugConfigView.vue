<template xmlns="http://www.w3.org/1999/html">
  <div class="grid">
    <FormField v-if="modified" class="col-6">
      <Button
        label="Save Configuration"
        v-tooltip="'Save the current configuration before running evaluation.'"
        icon="pi pi-save"
        severity="info"
        @click="saveConfig"
      />
    </FormField>
    <FormField v-if="modified" class="col-6">
      <Button
        label="Discard Changes"
        icon="pi pi-times"
        @click="fetchConfig"
        severity="secondary"
      />
    </FormField>
    <div class="grid m-0 w-full">
      <FormField class="md:col-6">
        <label class="field-label">Text2SQL Systems:</label>
        <MultiSelect display="chip" filter v-model="config.models" :options="avail_models" />
      </FormField>
      <FormField class="md:col-5">
        <label class="field-label">Workload:</label>
        <Select :options="avail_datasets" v-model="config.dataset" />
      </FormField>
    </div>
    <div class="grid m-0 w-full">
      <FormField class="md:col-6">
        <label class="field-label">Scaling Factors:</label>
        <MultiSelect
          display="chip"
          filter
          placeholder="Select scales"
          v-model="config.scales"
          :options="avail_scales"
        >
        </MultiSelect>
      </FormField>
      <FormField class="md:col-6">
        <label class="field-label">Workload Versions:</label>
        <MultiSelect
          display="chip"
          filter
          placeholder="Select scales"
          v-model="config.dataset_versions"
          :options="avail_versions"
        />
      </FormField>
    </div>
    <div class="grid m-0 w-full">
      <FormField class="md:col-6">
        <FloatLabel variant="in">
          <label>Number of new data per Subcategory</label>
          <InputText v-model="config.aug_per_sub_cat" />
        </FloatLabel>
      </FormField>
      <FormField class="md:col-6">
        <Slider v-model="config.aug_per_sub_cat" :min="1" :max="100" :step="1" class="w-5 mt-4" />
      </FormField>
    </div>
    <div class="grid m-0 w-full">
      <FormField class="md:col-6">
        <FloatLabel variant="in">
          <label>Error Threshold</label>
          <InputText v-model="config.error_threshold" />
        </FloatLabel>
      </FormField>
      <FormField class="md:col-6">
        <Slider v-model="config.error_threshold" :min="0" :max="1" :step="0.01" class="w-5 mt-4" />
      </FormField>
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
import { c } from 'vite/dist/node/moduleRunnerTransport.d-DJ_mE5sf'

const charts = {
  REA: 'mean__relaxed__execution__accuracy_per__sub_category',
  Overall: 'overall__scores',
  GET: 'mean__gold__execution__time_per_scale',
  'SubCategory Dist': 'sub_cat_count',
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
      selectedPlot: 'EA',
      selectedHue: 'Model',
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
      latestConfig: '',
    }
  },
  props: {
    modelValue: Boolean,
  },
  emits: ['update:modelValue'],
  computed: {
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
    modified() {
      return JSON.stringify(this.config, null, 2) != this.latestConfig
    },
  },
  methods: {
    async fetchConfig() {
      const stats = await this.call_api('api/aug/stats')
      this.db_stats = stats.db_stats
      const data = await this.call_api('api/aug/config')
      Object.assign(this.config, data)
      this.latestConfig = JSON.stringify(this.config, null, 2)
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
      await this.fetchConfig()
    },
  },
  watch: {
    config: {
      handler(newVal) {
        const conf_str = JSON.stringify(this.config, null, 2)
        const result = conf_str != this.latestConfig
        this.$emit('update:modelValue', result)
      },
      deep: true,
      flush: 'post',
    },
  },
  mounted() {
    this.fetchConfig()
  },
  beforeUnmount() {},
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
  },
}
</script>

<style scoped>
.plot {
  width: 100%;
}
</style>
