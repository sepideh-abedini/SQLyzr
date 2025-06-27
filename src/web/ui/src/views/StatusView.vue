<template>
  <div class="status">
    <Toast />

    <Card class="w-1/2">
      <template #title>
        <div class="text-center">
          <h1>Execution Status</h1>
        </div>
      </template>
      <template #content>
        <div class="status-section">
          <h3 class="section-title">Control Panel</h3>
          <div class="flex justify-content-center gap-3 mb-4">
            <Button label="Run SQLyzr" icon="pi pi-play" @click="runSqlyzr" severity="primary" />
            <Button label="Kill SQLyzr" icon="pi pi-times" @click="killSqlyzr" severity="danger" />
          </div>

          <div class="status-info mb-3">
            <div v-if="running" class="status-badge running">
              <i class="pi pi-spin pi-spinner mr-2"></i>
              <span>Running: {{ current_step }}</span>
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

          <ProgressBar
            v-if="running"
            mode="indeterminate"
            style="height: 6px"
            class="mb-4"
          ></ProgressBar>

          <div class="resource-usage mb-4">
            <div class="grid">
              <div class="col-12 md:col-3 p-2">
                <div class="resource-label">CPU Percentage</div>
                <div class="flex justify-content-center">
                  <Knob
                    v-model="cpu_percent"
                    valueTemplate="{value}%"
                    :size="100"
                    :readonly="true"
                    valueColor="#4CAF50"
                    :max="max_cpu"
                  />
                </div>
                <div class="resource-value">{{ cpu_percent }}%</div>
              </div>
              <div class="col-12 md:col-3 p-2">
                <div class="resource-label">Memory Percentage</div>
                <div class="flex justify-content-center">
                  <Knob
                    v-model="memory_percent"
                    valueTemplate="{value}%"
                    :size="100"
                    :readonly="true"
                    valueColor="#2196F3"
                  />
                </div>
                <div class="resource-value">{{ memory_percent }}%</div>
              </div>
              <div class="col-12 md:col-3 p-2">
                <div class="resource-label">Memory Usage</div>
                <div class="flex justify-content-center">
                  <Knob
                    v-model="memory_gb"
                    valueTemplate="{value} GB"
                    :size="100"
                    :readonly="true"
                    valueColor="#4CAF50"
                  />
                </div>
                <div class="resource-value">{{ memory_gb }} MB</div>
              </div>

              <div class="col-12 md:col-3 p-2">
                <div class="resource-label">Elapsed Time</div>
                <div class="resource-value">{{ elapsed_time }} seconds</div>
              </div>
            </div>
          </div>

          <div class="pipeline-container">
            <div v-for="(step, index) in sorted_pipeline_steps" :key="step" class="pipeline-step">
              <Button
                :outlined="!pipeline_config[step]"
                :label="step"
                :loading="is_current_step(step)"
                :severity="pipeline_status[step] ? 'success' : 'info'"
                class="text-capitalize"
              />
              <i
                v-if="index < sorted_pipeline_steps.length - 1"
                class="pi pi-arrow-right pipeline-arrow"
              ></i>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import Button from 'primevue/button'
import Message from 'primevue/message'
import Toast from 'primevue/toast'
import Card from 'primevue/card'
import { ProgressBar, Timeline } from 'primevue'
import Knob from 'primevue/knob'
import { API_BASE_URL } from '../config'

export default {
  data() {
    return {
      running: false,
      loading: false,
      memory_percent: 0,
      memory_gb: 0,
      cpu_percent: 0,
      elapsed_time: 0,
      max_cpu: 0,
      success: false,
      fail: false,
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
      },
    }
  },
  computed: {
    sorted_pipeline_steps() {
      return ['verify', 'predict', 'eval', 'charts', 'transformers', 'augment']
    },
    finished() {
      for (let step of this.sorted_pipeline_steps) {
        if (this.pipeline_config[step]) {
          if (!this.pipeline_status[step]) {
            return false
          }
        }
      }
      return true
    },
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
    is_current_step(step) {
      return this.running && this.current_step === step
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
        if (data.return_code === 0) {
          this.success = true
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'SQLyzr completed successfully',
            life: 3000,
          })
        }
        if (data.return_code > 0) {
          this.fail = true
          this.$toast.add({
            severity: 'error',
            summary: 'Failure',
            detail: 'SQLyzr failed!',
            life: 3000,
          })
        }
      }

      if (this.success || this.fail) {
        this.finished = true
        this.clearInterval()
      }
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
    },
    clear() {
      this.running = false
      this.success = false
      this.fail = false
    },
    clearInterval() {
      console.log('clearing interval')
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
      }
    },
    setInterval() {
      this.fetchData()
      this.refreshInterval = setInterval(() => {
        this.fetchData()
      }, 1000)
    },
  },
  mounted() {
    this.fetchData()
  },
  beforeUnmount() {
    console.log('Unmount')
    this.clearInterval()
  },
  components: {
    Button,
    Message,
    ProgressBar,
    Toast,
    Knob,
    Timeline,
    Card,
  },
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
  box-shadow:
    0 2px 1px -1px rgba(0, 0, 0, 0.2),
    0 1px 1px 0 rgba(0, 0, 0, 0.14),
    0 1px 3px 0 rgba(0, 0, 0, 0.12);
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

.resource-usage {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 0.5rem;
}

.resource-item {
  display: flex;
  flex-direction: column;
}

.resource-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
}

.resource-value {
  text-align: right;
  font-size: 0.9rem;
  color: #6c757d;
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
