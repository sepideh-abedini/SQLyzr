<template>
  <div class="configuration">
    <h1>SQLyzr Configuration</h1>

    <b-alert v-if="hasError" variant="danger" show>{{ errorMessage }}</b-alert>

    <b-overlay :show="isLoading" rounded="sm">
      <b-card>
        <b-card-body>
          <b-form @submit.prevent="saveConfig">
            <div class="mb-3">
              <b-button variant="primary" @click="saveConfig">Save Configuration</b-button>
              <b-button variant="success" class="ml-2" @click="runSqlyzr">Run SQLyzr</b-button>
            </div>

            <b-row>
              <b-col md="6">
                <b-form-group label="Models" label-for="models">
                  <div>
                    <b-form-checkbox v-for="model in modelOptions" :key="model.value"
                                     :id="'model_' + model.value"
                                     v-model="formConfig.models"
                                     :value="model.value">
                      {{ model.text }}
                    </b-form-checkbox>
                  </div>
                </b-form-group>

                <b-form-group label="Dataset" label-for="dataset">
                  <b-form-input id="dataset" v-model="formConfig.dataset"></b-form-input>
                </b-form-group>

                <b-form-group label="Dataset Size" label-for="dataset_size">
                  <b-form-input id="dataset_size" v-model="formConfig.dataset_size"></b-form-input>
                </b-form-group>

                <b-form-group label="Iterations" label-for="itrs">
                  <b-form-input id="itrs" v-model.number="formConfig.itrs" type="number" min="1"></b-form-input>
                </b-form-group>

                <b-form-group label="Temperatures" label-for="temps">
                  <b-form-tags
                      id="temps"
                      v-model="formConfig.temps"
                      tag-variant="primary"
                      tag-pills
                      size="md"
                      separator=" "
                      placeholder="Add a temperature"
                      class="mb-2"
                      :tag-validator="validateTemperature"
                      :input-attrs="{ type: 'number', step: '0.1', min: '0' }"
                      @tag-state="onTagState"
                  >
                    <template #add-button-text>
                      <span class="d-none d-sm-inline">Add</span>
                    </template>
                    <template #tag="{ tag, tagClass, removeTag }">
                      <span :class="tagClass">{{ typeof tag === 'number' ? tag.toFixed(1) : tag }}</span>
                      <button @click="removeTag" class="close">×</button>
                    </template>
                  </b-form-tags>
                  <b-dropdown text="Select Temperature" variant="outline-secondary" class="mt-2">
                    <b-dropdown-item @click="addTemperature(0.1)">0.1</b-dropdown-item>
                    <b-dropdown-item @click="addTemperature(0.2)">0.2</b-dropdown-item>
                    <b-dropdown-item @click="addTemperature(0.5)">0.5</b-dropdown-item>
                    <b-dropdown-item @click="addTemperature(0.7)">0.7</b-dropdown-item>
                    <b-dropdown-item @click="addTemperature(1.0)">1.0</b-dropdown-item>
                  </b-dropdown>
                </b-form-group>

                <b-form-group label="GPT Mode" label-for="batch_mode">
                  <b-form-radio-group
                      id="batch_mode"
                      v-model="formConfig.batch"
                      :options="[]"
                      :buttons="true"
                      :button-variant="'outline-primary'"
                      class="mb-2"
                  >
                    <b-form-radio :value="true">Batch</b-form-radio>
                    <b-form-radio :value="false">Single</b-form-radio>
                  </b-form-radio-group>
                </b-form-group>

                <b-form-group label="Augmentations Per Sub Category" label-for="aug_per_sub_cat">
                  <b-form-input id="aug_per_sub_cat" v-model.number="formConfig.aug_per_sub_cat" type="number"
                                min="1"></b-form-input>
                </b-form-group>

                <b-form-group label="Error Threshold" label-for="error_threshold">
                  <b-form-input id="error_threshold" v-model.number="formConfig.error_threshold" type="number"
                                min="0"></b-form-input>
                </b-form-group>

                <b-form-group>
                  <b-form-checkbox id="force" v-model="formConfig.force">Force</b-form-checkbox>
                </b-form-group>
              </b-col>

              <b-col md="6">
                <div class="config-section">
                  <h5 class="section-title">Pipeline</h5>
                  <b-form-group>
                    <b-form-checkbox id="pipeline_verify" v-model="formConfig.pipeline.verify">Verify</b-form-checkbox>
                  </b-form-group>

                  <b-form-group>
                    <b-form-checkbox id="pipeline_predict" v-model="formConfig.pipeline.predict">Predict
                    </b-form-checkbox>
                  </b-form-group>

                  <b-form-group>
                    <b-form-checkbox id="pipeline_eval" v-model="formConfig.pipeline.eval">Evaluate</b-form-checkbox>
                  </b-form-group>

                  <b-form-group>
                    <b-form-checkbox id="pipeline_transformers" v-model="formConfig.pipeline.transformers">Transformers
                    </b-form-checkbox>
                  </b-form-group>

                  <b-form-group>
                    <b-form-checkbox id="pipeline_augment" v-model="formConfig.pipeline.augment">Augment
                    </b-form-checkbox>
                  </b-form-group>

                  <b-form-group>
                    <b-form-checkbox id="pipeline_charts" v-model="formConfig.pipeline.charts">Charts</b-form-checkbox>
                  </b-form-group>
                </div>

                <div class="config-section">
                  <h5 class="section-title">Charts</h5>
                  <b-form-group v-for="chart in chartOptions" :key="chart.value">
                    <b-form-checkbox
                        :id="'chart_' + chart.value.toLowerCase().replace(/ /g, '_')"
                        v-model="formConfig.charts"
                        :value="chart.value">
                      {{ chart.text }}
                    </b-form-checkbox>
                  </b-form-group>
                </div>
              </b-col>
            </b-row>
          </b-form>
        </b-card-body>
      </b-card>
    </b-overlay>
  </div>
</template>

<script>
import {mapGetters, mapActions} from 'vuex'

export default {
  name: 'Configuration',
  data() {
    return {
      formConfig: {
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
  computed: {
    ...mapGetters(['isLoading', 'hasError', 'errorMessage', 'config'])
  },
  watch: {
    config: {
      handler(newConfig) {
        if (newConfig) {
          this.formConfig = JSON.parse(JSON.stringify(newConfig))
          if (this.formConfig.temps && Array.isArray(this.formConfig.temps)) {
            this.formConfig.temps = this.formConfig.temps.map(temp => parseFloat(temp))
          } else {
            this.formConfig.temps = []
          }
        }
      },
      immediate: true
    }
  },
  methods: {
    ...mapActions(['fetchConfig', 'saveConfig', 'runSqlyzr']),
    addTemperature(temp) {
      if (!this.formConfig.temps.includes(temp)) {
        this.formConfig.temps.push(temp)
      }
    },
    validateTemperature(tag) {
      const num = parseFloat(tag)
      return !isNaN(num) && num >= 0
    },
    onTagState(newTag, valid) {
      if (valid && newTag) {
        return parseFloat(newTag)
      }
      return newTag
    },
    async saveConfig() {
      const result = await this.$store.dispatch('saveConfig', this.formConfig)
      if (result.success) {
      }
    },
    async runSqlyzr() {
      await this.saveConfig()
      const result = await this.$store.dispatch('runSqlyzr')
      if (result.success) {
      } else {
      }
    }
  },
  created() {
    this.fetchConfig()
  }
}
</script>

<style scoped>
.config-section {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.section-title {
  margin-bottom: 15px;
  font-weight: bold;
}
</style>
