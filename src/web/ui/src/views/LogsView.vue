<template>
  <div class="logs">
    <Toast/>

    <h1>SQLyr Logs</h1>

    <div class="card">
      <ProgressSpinner v-if="loading" class="my-4"/>
      <div v-else class="log-container">
        <pre class="log-content">{{ logs }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import { API_BASE_URL } from '../config';

export default {
  data() {
    return {
      loading: false,
      logs: '',
      refreshInterval: null
    }
  },
  methods: {
    async fetchLogs() {
      this.loading = true;

      try {
        const response = await fetch(`${API_BASE_URL}/api/log`);

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.logs = data.logs || 'No logs available';
      } catch (error) {
        console.error('Error loading logs:', error);
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: `Error loading logs: ${error.message}`,
          life: 5000
        });
      } finally {
        this.loading = false;
        this.$nextTick(() => {
          const logContainer = document.querySelector('.log-container');
          if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight;
          }
        });
      }
    }
  },
  mounted() {
    this.fetchLogs();
    this.refreshInterval = setInterval(() => {
      this.fetchLogs();
    }, 10000);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  components: {
    ProgressSpinner,
    Toast
  }
}
</script>

<style>
.logs {
  padding: 2rem;
}

.logs h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.log-container {
  border-radius: 0.5rem;
  padding: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

.log-content {
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

@media (max-width: 768px) {
  .logs {
    padding: 1rem;
  }
}
</style>
