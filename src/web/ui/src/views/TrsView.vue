<template>
  <div class="trs">
    <Toast/>

    <h1>SQL Repair Suggestions</h1>

    <div class="card">
      <h2>Select Model and Dataset</h2>
      <div class="selection-container">
        <div class="p-field">
          <label for="model">Model</label>
          <Dropdown id="model" v-model="selectedModel" :options="models" placeholder="Select a Model" class="w-full" />
        </div>
        <div class="p-field">
          <label for="dataset">Dataset</label>
          <Dropdown id="dataset" v-model="selectedDataset" :options="datasets" placeholder="Select a Dataset" class="w-full" />
        </div>
        <Button label="Fetch Suggestions" icon="pi pi-search" @click="fetchTrsData" :disabled="!selectedModel || !selectedDataset" />
      </div>

      <ProgressSpinner v-if="loading" class="my-4"/>

      <div v-else-if="trsData && trsData.length > 0" class="trs-container">
        <h3>Repair Suggestions ({{ trsData.length }} items)</h3>
        <div v-for="(item, index) in trsData" :key="index" class="trs-item">
          <div class="trs-item-header">
            <span class="trs-item-number">{{ index + 1 }}</span>
            <span class="trs-item-db">Database: {{ item.db_id }}</span>
          </div>
          <div class="trs-item-content">
            <div class="trs-sql">
              <h4>Predicted SQL (Wrong)</h4>
              <pre>{{ item.pred }}</pre>
            </div>
            <div class="trs-sql">
              <h4>Gold SQL (Correct)</h4>
              <pre>{{ item.gold }}</pre>
            </div>
            <div class="trs-messages">
              <h4>Repair Messages</h4>
              <ul>
                <li v-for="(message, msgIndex) in item.messages" :key="msgIndex">{{ message }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="error" class="error-message">
        <Message severity="error" :text="error" />
      </div>
      <div v-else-if="fetchAttempted" class="no-data-message">
        <Message severity="info" text="No repair suggestions found for the selected model and dataset." />
      </div>
    </div>
  </div>
</template>

<script>
import Button from "primevue/button";
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import Dropdown from 'primevue/dropdown';
import { API_BASE_URL } from '../config';

export default {
  data() {
    return {
      loading: false,
      error: null,
      models: [],
      datasets: [],
      selectedModel: null,
      selectedDataset: null,
      trsData: null,
      fetchAttempted: false
    }
  },
  methods: {
    async fetchModels() {
      try {
        const data = await this.call_api('api/models');
        this.models = data.models;
      } catch (error) {
        this.error = `Error loading models: ${error.message}`;
        console.error('Error loading models:', error);
      }
    },

    async fetchDatasets() {
      try {
        const data = await this.call_api('api/datasets');
        this.datasets = data.datasets;
      } catch (error) {
        this.error = `Error loading datasets: ${error.message}`;
        console.error('Error loading datasets:', error);
      }
    },

    async fetchTrsData() {
      this.loading = true;
      this.error = null;
      this.trsData = null;
      this.fetchAttempted = true;

      try {
        const data = await this.call_api(`api/trs?model=${this.selectedModel}&dataset=${this.selectedDataset}`);
        this.trsData = data.trs_data;

        if (this.trsData && this.trsData.length > 0) {
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: `Loaded ${this.trsData.length} repair suggestions`,
            life: 3000
          });
        } else {
          this.$toast.add({
            severity: 'info',
            summary: 'Info',
            detail: 'No repair suggestions found',
            life: 3000
          });
        }
      } catch (error) {
        this.error = `Error loading TRS data: ${error.message}`;
        console.error('Error loading TRS data:', error);
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchModels();
    this.fetchDatasets();
  },
  components: {
    Button,
    Message,
    ProgressSpinner,
    Toast,
    Dropdown
  }
}
</script>

<style>
.trs {
  padding: 2rem;
}

.trs h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.selection-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: flex-end;
}

.p-field {
  flex: 1;
  min-width: 200px;
}

.trs-container {
  margin-top: 2rem;
}

.trs-item {
  margin-bottom: 2rem;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  overflow: hidden;
}

.trs-item-header {
  background-color: #f5f5f5;
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.trs-item-number {
  background-color: #2196F3;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.trs-item-content {
  padding: 1rem;
}

.trs-sql {
  margin-bottom: 1rem;
}

.trs-sql pre {
  background-color: #f8f9fa;
  padding: 0.75rem;
  border-radius: 0.25rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
}

.trs-messages ul {
  margin: 0;
  padding-left: 1.5rem;
}

.trs-messages li {
  margin-bottom: 0.5rem;
}

.error-message, .no-data-message {
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .trs {
    padding: 1rem;
  }

  .selection-container {
    flex-direction: column;
  }

  .p-field {
    width: 100%;
  }
}
</style>
