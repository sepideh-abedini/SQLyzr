<template>
  <div class="config">
    <Card>
      <template #header>
      </template>
      <template #title>SQLyzr Configuration</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6">
            <FormField>
              Dataset:
              <Select v-model="config.dataset" :options="dataset_options" placeholder="Dataset"/>
            </FormField>
            <FormField name="Salam">
              Dataset Size:
              <Select v-model="config.dataset_size" :options="size_options" placeholder="Dataset Size"/>
            </FormField>
            <FormField name="Salam">
              Models:
              <div class="flex flex-wrap justify-center gap-4">
                <div v-for="model in modelOptions" :key="model" class="flex items-center gap-2">
                  <Checkbox v-model="config.models" :inputId="model" :value="model" :name="model"/>
                  <label :for="model">{{ model }}</label>
                </div>
              </div>
            </FormField>
            <FormField name="Salam">
              Num Iterations:
              <InputNumber v-model="config.itrs" showButtons buttonLayout="horizontal" :min="1"
                           :max="5">
                <template #incrementbuttonicon>
                  <span class="pi pi-plus"/>
                </template>
                <template #decrementbuttonicon>
                  <span class="pi pi-minus"/>
                </template>
              </InputNumber>
            </FormField>
            <FormField name="Salam">
              Temperature:
              <MultiSelect class="w-full" v-model="config.temps" display="chip" :options="suggested_temps"
                           placeholder="Temperatures"
                           :maxSelectedLabels="3"/>
            </FormField>
            <FormField name="Salam">
              Batch Mode:
              <span v-if="config.batch"> On</span>
              <span v-else> Off</span>
              <div class="flex">
                <ToggleSwitch v-model="config.batch"/>
              </div>
            </FormField>
          </div>


          <div class="col-12 md:col-6">
            <FormField name="Salam">
              Aug Per sub:
              <InputText v-model.number="config.aug_per_sub_cat"/>
              <Slider v-model="config.aug_per_sub_cat" min="1" max="10" class="w-full"/>
            </FormField>
            <FormField name="Salam">
              Error Threshold:
              <Knob value-color="red" v-model="config.error_threshold"/>
            </FormField>
            <FormField name="Salam">
              Pipeline:
              <div class="flex flex-wrap justify-center gap-4">
                {{ config.pipeline }}
                <div v-for="(active,step) in config.pipeline" :key="step" class="flex items-center gap-2">
                  <ToggleButton v-model="config.pipeline[step]" :on-label="step" :off-label="step"/>
                  <i class="pi pi-arrow-right"></i>
                </div>

              </div>
            </FormField>
            <FormField name="Salam">
              Charts:
              <MultiSelect v-model="config.charts" display="chip" :options="chartOptions" filter
                           placeholder="Selected Charts"
                           class="w-full md:w-80"/>
            </FormField>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import Card from "primevue/card";
import Button from "primevue/button";
import Checkbox from 'primevue/checkbox';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import RadioButton from 'primevue/radiobutton';
import Chip from 'primevue/chip';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import FormField from '@primevue/forms/formfield'
import FieldSet from 'primevue/fieldset'
import Select from 'primevue/select'
import AutoComplete from 'primevue/autocomplete'
import MultiSelect from 'primevue/multiselect'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import Knob from 'primevue/knob'
import Breadcrumb from 'primevue/breadcrumb'
import {ToggleButton} from "primevue";

export default {

  components: {
    Card,
    Button,
    Checkbox,
    InputText,
    InputNumber,
    RadioButton,
    Chip,
    Message,
    ProgressSpinner,
    Toast,
    FormField,
    FieldSet,
    Select,
    AutoComplete,
    MultiSelect,
    Slider,
    ToggleSwitch,
    Knob,
    Breadcrumb,
    ToggleButton
  },
  data() {
    return {
      loading: false,
      error: null,
      dataset_options: [
        'spider',
        'bird',
        'beaver',
        'agg'
      ],
      size_options: [
        'small',
        'all'
      ],
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
          charts: false
        },
        charts: []
      },
      modelOptions: [
        'din',
        'dail'
      ],
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
        'Complexity Inconsistency']
    }
  },
  computed: {
    pipeline_values() {
      return [
        {step: 'verify', active: this.config.pipeline.verify},
        {step: 'predict', active: this.config.pipeline.verify},
        {step: 'eval', active: this.config.pipeline.verify},
      ]
    }
  },
  methods: {
    async fetchConfig() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('http://localhost:7777/api/config');

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.config = data;

        if (this.config.temps && Array.isArray(this.config.temps)) {
          this.config.temps = this.config.temps.map(temp => parseFloat(temp));
        } else {
          this.config.temps = [];
        }

        if (!this.config.pipeline) {
          this.config.pipeline = {
            verify: false,
            predict: false,
            eval: false,
            transformers: false,
            augment: false,
            charts: false
          };
        }

        if (!Array.isArray(this.config.charts)) {
          this.config.charts = [];
        }
      } catch (error) {
        this.error = `Error loading configuration: ${error.message}`;
        console.error('Error loading configuration:', error);
      } finally {
        this.loading = false;
      }
    },

    async saveConfig() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('http://localhost:7777/api/config', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.config)
        });

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Configuration saved successfully',
          life: 3000
        });
      } catch (error) {
        this.error = `Error saving configuration: ${error.message}`;
        console.error('Error saving configuration:', error);
      } finally {
        this.loading = false;
      }
    },

    async runSqlyzr() {
      // First save the configuration
      await this.saveConfig();

      if (this.error) {
        return; // Don't proceed if there was an error saving
      }

      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('/api/run', {
          method: 'POST'
        });

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'SQLyzr started successfully',
          life: 3000
        });
      } catch (error) {
        this.error = `Error running SQLyzr: ${error.message}`;
        console.error('Error running SQLyzr:', error);
      } finally {
        this.loading = false;
      }
    },

    addTemperature(temp) {
      if (!this.config.temps.includes(temp)) {
        this.config.temps.push(temp);
      }
    }
  },
  mounted() {
    this.fetchConfig();
  }
}
</script>
<style>
.config {
  padding: 2rem;
}
</style>
