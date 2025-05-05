<template>
  <div class="charts">
    <Toast/>

    <h1>Charts</h1>

    <Message v-if="error" severity="error">{{ error }}</Message>

    <ProgressSpinner v-if="loading" class="my-4"/>

    <div v-else class="card">
      <div class="mb-4 flex gap-2">
        <Button label="Refresh Charts" icon="pi pi-refresh" @click="fetchCharts"/>
      </div>

      <div class="grid">
        <!-- Left side - Chart list -->
        <div class="col-12 md:col-3">
          <h3>Available Charts</h3>
          <div class="chart-list">
            <ul class="list-none p-0 m-0">
              <li v-for="chart in charts" :key="chart"
                  class="chart-item p-2 cursor-pointer"
                  :class="{ 'selected': selectedChart === chart }"
                  @click="selectChart(chart)">
                {{ chart }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Right side - Selected chart display -->
        <div class="col-12 md:col-9">
          <div v-if="selectedChart" class="chart-display">
            <h3>{{ selectedChart }}</h3>
            <div v-if="chartLoading" class="flex justify-content-center">
              <ProgressSpinner />
            </div>
            <div v-else-if="chartError" class="p-3">
              <Message severity="error">{{ chartError }}</Message>
            </div>
            <div v-else class="chart-image">
              <img :src="chartUrl" :alt="selectedChart" class="w-full" />
            </div>
          </div>
          <div v-else class="flex justify-content-center align-items-center h-full">
            <Message severity="info">Select a chart from the list to view</Message>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Button from "primevue/button";
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';

export default {
  data() {
    return {
      loading: false,
      error: null,
      charts: [],
      selectedChart: null,
      chartLoading: false,
      chartError: null,
      chartUrl: null
    }
  },
  methods: {
    async fetchCharts() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('http://localhost:7777/api/charts');

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.charts = data.charts || [];

        if (this.charts.length === 0) {
          this.error = 'No charts available';
        } else if (this.selectedChart === null && this.charts.length > 0) {
          // Auto-select the first chart if none is selected
          this.selectChart(this.charts[0]);
        }
      } catch (error) {
        this.error = `Error loading charts: ${error.message}`;
        console.error('Error loading charts:', error);
      } finally {
        this.loading = false;
      }
    },

    async selectChart(chartName) {
      this.selectedChart = chartName;
      this.chartLoading = true;
      this.chartError = null;

      try {
        // Create URL with timestamp to prevent caching
        this.chartUrl = `http://localhost:7777/api/charts/${encodeURIComponent(chartName)}?t=${Date.now()}`;

        // Pre-load the image to check if it exists
        const img = new Image();
        img.onload = () => {
          this.chartLoading = false;
        };
        img.onerror = () => {
          this.chartError = `Failed to load chart: ${chartName}`;
          this.chartLoading = false;
        };
        img.src = this.chartUrl;
      } catch (error) {
        this.chartError = `Error loading chart: ${error.message}`;
        this.chartLoading = false;
      }
    }
  },
  mounted() {
    this.fetchCharts();
  },
  components: {
    Button,
    Message,
    ProgressSpinner,
    Toast
  }
}
</script>

<style>
.charts {
  padding: 2rem;
}

.charts h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.charts h3 {
  margin-bottom: 1rem;
  font-weight: 600;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.chart-list {
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.chart-item {
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.chart-item:hover {
  background-color: #f5f5f5;
}

.chart-item.selected {
  background-color: #e3f2fd;
  font-weight: 600;
}

.chart-display {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  min-height: 400px;
}

.chart-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (max-width: 768px) {
  .charts {
    padding: 1rem;
  }

  .chart-display {
    margin-top: 1rem;
  }
}
</style>
