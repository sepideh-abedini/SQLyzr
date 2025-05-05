<template>
  <div class="config">
    <Toast/>

    <h1>SQLyzr Configuration</h1>

    <Message v-if="error" severity="error">{{ error }}</Message>

    <ProgressSpinner v-if="loading" class="my-4"/>

    <div v-else class="card">
      <div class="mb-4 flex gap-2">
        <Button label="Save Configuration" icon="pi pi-save" @click="saveConfig"/>
        <Button label="Run SQLyzr" icon="pi pi-play" severity="success" @click="runSqlyzr"/>
      </div>

      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <h3>Models</h3>
            <div class="flex flex-column gap-2">
              <div v-for="model in modelOptions" :key="model.value" class="flex align-items-center">
                <Checkbox v-model="config.models" :value="model.value"
                          :inputId="'model_' + model.value"/>
                <label :for="'model_' + model.value" class="ml-2">{{ model.text }}</label>
              </div>
            </div>
          </div>

          <div class="field">
            <label for="dataset">Dataset</label>
            <InputText id="dataset" v-model="config.dataset" class="w-full"/>
          </div>

          <div class="field">
            <label for="dataset_size">Dataset Size</label>
            <InputText id="dataset_size" v-model="config.dataset_size" class="w-full"/>
          </div>

          <div class="field">
            <label for="itrs">Iterations</label>
            <InputNumber id="itrs" v-model="config.itrs" :min="1" class="w-full"/>
          </div>

          <div class="field">
            <label>Temperatures</label>
            <Chip v-model="config.temps" separator=" " class="w-full"/>
            <div class="mt-2">
              <Button v-for="temp in [0.1, 0.2, 0.5, 0.7, 1.0]"
                      :key="temp"
                      :label="temp.toString()"
                      size="small"
                      outlined
                      class="mr-2 mb-2"
                      @click="addTemperature(temp)"/>
            </div>
          </div>

          <div class="field">
            <label>GPT Mode</label>
            <div class="flex">
              <RadioButton v-model="config.batch" :value="true" inputId="batch_true"/>
              <label for="batch_true" class="ml-2 mr-4">Batch</label>

              <RadioButton v-model="config.batch" :value="false" inputId="batch_false"/>
              <label for="batch_false" class="ml-2">Single</label>
            </div>
          </div>

          <div class="field">
            <label for="aug_per_sub_cat">Augmentations Per Sub Category</label>
            <InputNumber id="aug_per_sub_cat" v-model="config.aug_per_sub_cat" :min="1"
                         class="w-full"/>
          </div>

          <div class="field">
            <label for="error_threshold">Error Threshold</label>
            <InputNumber id="error_threshold" v-model="config.error_threshold" :min="0"
                         class="w-full"/>
          </div>

          <div class="field">
            <Checkbox v-model="config.force" inputId="force" :binary="true"/>
            <label for="force" class="ml-2">Force</label>
          </div>
        </div>

        <div class="col-12 md:col-6">
          <div class="config-section">
            <h3>Pipeline</h3>
            <div class="field">
              <Checkbox v-model="config.pipeline.verify" inputId="pipeline_verify" :binary="true"/>
              <label for="pipeline_verify" class="ml-2">Verify</label>
            </div>

            <div class="field">
              <Checkbox v-model="config.pipeline.predict" inputId="pipeline_predict"
                        :binary="true"/>
              <label for="pipeline_predict" class="ml-2">Predict</label>
            </div>

            <div class="field">
              <Checkbox v-model="config.pipeline.eval" inputId="pipeline_eval" :binary="true"/>
              <label for="pipeline_eval" class="ml-2">Evaluate</label>
            </div>

            <div class="field">
              <Checkbox v-model="config.pipeline.transformers" inputId="pipeline_transformers"
                        :binary="true"/>
              <label for="pipeline_transformers" class="ml-2">Transformers</label>
            </div>

            <div class="field">
              <Checkbox v-model="config.pipeline.augment" inputId="pipeline_augment"
                        :binary="true"/>
              <label for="pipeline_augment" class="ml-2">Augment</label>
            </div>

            <div class="field">
              <Checkbox v-model="config.pipeline.charts" inputId="pipeline_charts" :binary="true"/>
              <label for="pipeline_charts" class="ml-2">Charts</label>
            </div>
          </div>

          <div class="config-section">
            <h3>Charts</h3>
            <div v-for="chart in chartOptions" :key="chart.value" class="field">
              <Checkbox v-model="config.charts" :value="chart.value"
                        :inputId="'chart_' + chart.value.toLowerCase().replace(/ /g, '_')"/>
              <label :for="'chart_' + chart.value.toLowerCase().replace(/ /g, '_')"
                     class="ml-2">{{ chart.text }}</label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Button from "primevue/button";
import Checkbox from 'primevue/checkbox';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import RadioButton from 'primevue/radiobutton';
import Chip from 'primevue/chip';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';

export default {

  data() {
    return {
      loading: false,
      error: null,
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
        {value: 'din', text: 'din'},
        {value: 'dail', text: 'dail'}
      ],
      chartOptions: [
        {value: 'Execution Accuracy', text: 'Execution Accuracy'},
        {value: 'Relaxed Execution Accuracy', text: 'Relaxed Execution Accuracy'},
        {value: 'Exact Match', text: 'Exact Match'},
        {value: 'Execution Time', text: 'Execution Time'},
        {value: 'Token Usage', text: 'Token Usage'},
        {value: 'Execution Time Consistency', text: 'Execution Time Consistency'},
        {value: 'Execution Time Inconsistency', text: 'Execution Time Inconsistency'},
        {value: 'Complexity Consistency', text: 'Complexity Consistency'},
        {value: 'Complexity Inconsistency', text: 'Complexity Inconsistency'}
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
  },
  components: {
    Button,
    Checkbox,
    InputText,
    InputNumber,
    RadioButton,
    Chip,
    Message,
    ProgressSpinner,
    Toast
  }
}
</script>
<style>
.config {
  padding: 2rem;
}
</style>
