<template>
  <div class="status">
    <Toast/>

    <h1>SQLyr Status</h1>

    <div class="card w-1/2">
      <div class="status-section">
        <h3 class="section-title">Control Panel</h3>
        <div class="flex justify-content-center gap-3 mb-4">
          <Button label="Run SQLyzr" icon="pi pi-play" @click="runSqlyzr" severity="primary"/>
          <Button label="Kill SQLyzr" icon="pi pi-times" @click="" severity="danger"/>
        </div>

        <div class="status-info mb-3">
          <div v-if="is_running" class="status-badge running">
            <i class="pi pi-spin pi-spinner mr-2"></i>
            <span>Running: {{ current_step }}</span>
          </div>
          <div v-else-if="finished" class="status-badge completed">
            <i class="pi pi-check-circle mr-2"></i>
            <span>Completed</span>
          </div>
          <div v-else class="status-badge idle">
            <i class="pi pi-pause mr-2"></i>
            <span>Not Running</span>
          </div>
        </div>

        <ProgressBar v-if="is_running" mode="indeterminate" style="height: 6px" class="mb-4"></ProgressBar>
      </div>

      <div class="status-section">
        <h3 class="section-title">Pipeline Progress</h3>
        <div class="pipeline-container">
          <div v-for="(step, index) in sorted_pipeline_steps" :key="step" class="pipeline-step">
            <Button :outlined="!pipeline_config[step]"
                    :label="step"
                    :loading="is_current_step(step)"
                    :severity="pipeline_status[step] ? 'success' : 'info'"
                    class="text-capitalize"/>
            <i v-if="index < sorted_pipeline_steps.length - 1" class="pi pi-arrow-right pipeline-arrow"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Button from "primevue/button";
import Message from 'primevue/message';
import Toast from 'primevue/toast';
import {ProgressBar} from "primevue";

export default {
  data() {
    return {
      is_running: false,
      loading: false,
      pipeline_status: {
        verify: false,
        predict: false,
        eval: false,
        charts: false,
        transformers: false,
        augment: false,
      },
      pipeline_config: {
        verify: false,
        predict: false,
        eval: false,
        charts: false,
        transformers: false,
        augment: false,
      }
    }
  },
  computed: {
    sorted_pipeline_steps() {
      return [
        "verify", "predict", "eval", "charts", "transformers", "augment",
      ]
    },
    finished() {
      for (let step of this.sorted_pipeline_steps) {
        if (this.pipeline_config[step]) {
          if (!this.pipeline_status[step]) {
            return false;
          }
        }
      }
      return true;
    },
    current_step() {
      let max_i = -1;
      for (let i = 0; i < this.sorted_pipeline_steps.length; i++) {
        let step = this.sorted_pipeline_steps[i];
        if (this.pipeline_status[step])
          max_i = i > max_i ? i : max_i;
      }
      for (let i = max_i + 1; i < this.sorted_pipeline_steps.length; i++) {
        let step = this.sorted_pipeline_steps[i];
        if (this.pipeline_config[step]) {
          return step;
        }
      }
      return null;
    },
  },
  methods: {
    is_current_step(step) {
      return this.is_running && this.current_step === step;
    },
    async fetchStatus() {
      const response = await fetch('http://localhost:7777/api/run/status');
      const data = await response.json();
      this.is_running = data.is_running;
    },
    async fetchPipelineStatus() {
      const response = await fetch('http://localhost:7777/api/pipeline/status');
      this.pipeline_status = await response.json()
      if (this.finished) {
        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'SQLyzr finished successfully',
          life: 600000
        });
        this.clearInterval();
      }
    },
    async fetchPipelineConfig() {
      const response = await fetch('http://localhost:7777/api/config');
      const data = await response.json();
      this.pipeline_config = data.pipeline;
    },
    async fetchData() {
      await this.fetchPipelineConfig();
      await this.fetchStatus();
      await this.fetchPipelineStatus();
    },
    async runSqlyzr() {
      try {
        this.setInterval();
        const response = await fetch('http://localhost:7777/api/run', {
          method: 'POST'
        });

        if (!response.ok) {
          console.log(response);
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'SQLyzr started successfully',
          life: 3000
        });
      } catch (error) {
        console.error('Error running SQLyzr:', error);
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: `Error running SQLyzr: ${error.message}`,
          life: 3000
        });
      } finally {
        this.loading = false;
      }
    },
    clearInterval() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
    },
    setInterval() {
      this.fetchData();
      this.refreshInterval = setInterval(() => {
        this.fetchData();
      }, 3000);
    }
  },
  mounted() {
    this.fetchData();
    this.setInterval();
  },
  beforeUnmount() {
    this.clearInterval();
  },
  components: {
    Button,
    Message,
    ProgressBar,
    Toast
  }
}
</script>

<style>
.status {
  padding: 2rem;
}

.status h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.status-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.status-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #495057;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.status-info {
  display: flex;
  justify-content: center;
}

.status-badge {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
}

.status-badge.running {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.status-badge.completed {
  background-color: #e8f5e9;
  color: #1b5e20;
}

.status-badge.idle {
  background-color: #f5f5f5;
  color: #616161;
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

@media (max-width: 768px) {
  .status {
    padding: 1rem;
  }

  .status-section {
    padding: 1rem;
  }
}
</style>
