<template>
  <div class="logs">
    <Toast/>

    <h1>SQLyr Logs</h1>

    <div class="card">
      <Button icon="pi pi-trash" @click="clearLogs" class="p-button-sm p-button-danger ml-2"
              label="Clear Logs"/>
      <ToggleButton @value-change="" v-model="autoRefresh" class="w-48" on-label="Auto Refresh"
                    off-label="Auto Refresh"/>
      <ProgressSpinner v-if="loading" class="my-4"/>
      <div v-else class="log-container">
        <pre class="log-content" v-html="colorizedLogs"></pre>
      </div>

    </div>
  </div>
</template>

<script>
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import Button from 'primevue/button';
import ToggleButton from 'primevue/togglebutton';

import {API_BASE_URL} from '../config';

export default {

  components: {
    ProgressSpinner,
    Toast,
    Button,
    ToggleButton
  },
  data() {
    return {
      loading: false,
      logs: '',
      refreshInterval: null,
      autoRefresh: true,
    }
  },
  computed: {
    colorizedLogs() {
      if (!this.logs) return '';
      return this.ansiToHtml(this.logs);
    }
  },
  watch: {
    autoRefresh(newValue, oldValue) {
      if (newValue) {
        this.refreshInterval = setInterval(() => {
          this.fetchLogs();
        }, 1000);
      } else {
        if (this.refreshInterval) {
          clearInterval(this.refreshInterval);
        }
      }
    }
  },
  methods: {
    async fetchLogs() {
      const data = await this.call_api('api/logs', {}, false);
      this.logs = data.logs || 'No logs available';
      this.loading = false;
      this.$nextTick(() => {
        const logContainer = document.querySelector('.log-container');
        if (logContainer) {
          logContainer.scrollTop = logContainer.scrollHeight;
        }
      });
    },
    async clearLogs() {
      await this.call_api('api/logs', {method: 'DELETE'});
      this.fetchLogs();
    },

    ansiToHtml(text) {
      if (!text) return '';

      const ansiRegex = /\u001b\[((?:\d{1,3};?)+)m/g;

      let currentFgColor = '';
      let currentBgColor = '';
      let isBold = false;

      let html = text.replace(ansiRegex, (match, p1) => {
        const codes = p1.split(';').map(Number);

        for (const code of codes) {
          if (code === 0) {
            currentFgColor = '';
            currentBgColor = '';
            isBold = false;
            return '</span><span class="ansi">';
          }

          if (code === 1) {
            isBold = true;
          }

          if (code >= 30 && code <= 37) {
            currentFgColor = `ansi-fg-${code - 30}`;
          }

          if (code >= 40 && code <= 47) {
            currentBgColor = `ansi-bg-${code - 40}`;
          }

          if (code >= 90 && code <= 97) {
            currentFgColor = `ansi-fg-bright-${code - 90}`;
          }

          if (code >= 100 && code <= 107) {
            currentBgColor = `ansi-bg-bright-${code - 100}`;
          }
        }

        const classes = ['ansi'];
        if (currentFgColor) classes.push(currentFgColor);
        if (currentBgColor) classes.push(currentBgColor);
        if (isBold) classes.push('ansi-bold');

        return `</span><span class="${classes.join(' ')}">`;
      });

      return `<span class="ansi">${html}</span>`;
    }
  },
  mounted() {
    this.fetchLogs();
    this.refreshInterval = setInterval(() => {
      this.fetchLogs();
    }, 1000);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
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
  background-color: #1e1e1e;
  color: #f0f0f0;
}

.log-content {
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

/* ANSI Colors */
.ansi {
  color: inherit;
}

.ansi-bold {
  font-weight: bold;
}

/* Standard foreground colors */
.ansi-fg-0 {
  color: #000000;
}

/* Black */
.ansi-fg-1 {
  color: #cd3131;
}

/* Red */
.ansi-fg-2 {
  color: #0dbc79;
}

/* Green */
.ansi-fg-3 {
  color: #e5e510;
}

/* Yellow */
.ansi-fg-4 {
  color: #2472c8;
}

/* Blue */
.ansi-fg-5 {
  color: #bc3fbc;
}

/* Magenta */
.ansi-fg-6 {
  color: #11a8cd;
}

/* Cyan */
.ansi-fg-7 {
  color: #e5e5e5;
}

/* White */

/* Bright foreground colors */
.ansi-fg-bright-0 {
  color: #666666;
}

/* Bright Black (Gray) */
.ansi-fg-bright-1 {
  color: #f14c4c;
}

/* Bright Red */
.ansi-fg-bright-2 {
  color: #23d18b;
}

/* Bright Green */
.ansi-fg-bright-3 {
  color: #f5f543;
}

/* Bright Yellow */
.ansi-fg-bright-4 {
  color: #3b8eea;
}

/* Bright Blue */
.ansi-fg-bright-5 {
  color: #d670d6;
}

/* Bright Magenta */
.ansi-fg-bright-6 {
  color: #29b8db;
}

/* Bright Cyan */
.ansi-fg-bright-7 {
  color: #ffffff;
}

/* Bright White */

/* Standard background colors */
.ansi-bg-0 {
  background-color: #000000;
}

/* Black */
.ansi-bg-1 {
  background-color: #cd3131;
}

/* Red */
.ansi-bg-2 {
  background-color: #0dbc79;
}

/* Green */
.ansi-bg-3 {
  background-color: #e5e510;
}

/* Yellow */
.ansi-bg-4 {
  background-color: #2472c8;
}

/* Blue */
.ansi-bg-5 {
  background-color: #bc3fbc;
}

/* Magenta */
.ansi-bg-6 {
  background-color: #11a8cd;
}

/* Cyan */
.ansi-bg-7 {
  background-color: #e5e5e5;
}

/* White */

/* Bright background colors */
.ansi-bg-bright-0 {
  background-color: #666666;
}

/* Bright Black (Gray) */
.ansi-bg-bright-1 {
  background-color: #f14c4c;
}

/* Bright Red */
.ansi-bg-bright-2 {
  background-color: #23d18b;
}

/* Bright Green */
.ansi-bg-bright-3 {
  background-color: #f5f543;
}

/* Bright Yellow */
.ansi-bg-bright-4 {
  background-color: #3b8eea;
}

/* Bright Blue */
.ansi-bg-bright-5 {
  background-color: #d670d6;
}

/* Bright Magenta */
.ansi-bg-bright-6 {
  background-color: #29b8db;
}

/* Bright Cyan */
.ansi-bg-bright-7 {
  background-color: #ffffff;
}

/* Bright White */

@media (max-width: 768px) {
  .logs {
    padding: 1rem;
  }
}
</style>
