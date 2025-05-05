<template>
  <div class="logs">
    <Toast/>

    <h1>Live Logs</h1>

    <Message v-if="error" severity="error">{{ error }}</Message>

    <div class="card">
      <div class="mb-4 flex gap-2">
        <Button label="Refresh Logs" icon="pi pi-refresh" @click="fetchLogs"/>
      </div>

      <ProgressSpinner v-if="loading" class="my-4"/>

      <div v-else class="log-container">
        <pre class="log-content">{{ logs }}</pre>
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
      logs: '',
      refreshInterval: null
    }
  },
  methods: {
    async fetchLogs() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('http://localhost:7777/api/log');

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        this.logs = data.logs || 'No logs available';
      } catch (error) {
        this.error = `Error loading logs: ${error.message}`;
        console.error('Error loading logs:', error);
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchLogs();
    // Auto-refresh logs every 10 seconds
    this.refreshInterval = setInterval(() => {
      this.fetchLogs();
    }, 10000);
  },
  beforeUnmount() {
    // Clear the interval when component is destroyed
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
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
