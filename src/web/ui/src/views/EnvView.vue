<template>
  <div class="env">
    <Toast/>
    <Card>
      <template #title>
        <div class="text-center">
          <h2 class="m-0">Environment Variables</h2>
        </div>
      </template>
      <template #content>
        <div class="p-2">
          <div class="env-section">
            <div class="grid">
              <div v-for="(chunk, chunkIndex) in chunkedEnvVars" :key="chunkIndex" class="col-6">
                <div v-for="item in chunk" :key="item.key" class="flex mb-3">
                  <div class="flex-grow-1 mr-2">
                    <span class="font-bold">{{ item.key }}:</span>
                  </div>
                  <div class="flex-grow-1 mr-2">
                    <InputText v-model="envVars[item.key]" class="w-full"/>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="flex justify-content-center gap-3 mt-3">
          <Button label="Save Changes" icon="pi pi-save" @click="saveEnvVars"
                  class="p-button-primary"/>
          <Button label="Reset" icon="pi pi-refresh" @click="fetchEnvVars"
                  severity="secondary" outlined/>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import Card from "primevue/card";
import Button from "primevue/button";
import InputText from 'primevue/inputtext';
import Toast from 'primevue/toast';
import {API_BASE_URL} from '../config';

export default {
  components: {
    Card,
    Button,
    InputText,
    Toast
  },
  data() {
    return {
      loading: false,
      envVars: {},
      newEnvKey: '',
      newEnvValue: ''
    }
  },
  computed: {
    envVarsArray() {
      return Object.keys(this.envVars).map(key => ({
        key,
        value: this.envVars[key]
      }));
    },
    chunkedEnvVars() {
      const array = this.envVarsArray;
      const middle = Math.ceil(array.length / 2);
      return [
        array.slice(0, middle),
        array.slice(middle)
      ];
    }
  },
  methods: {
    async fetchEnvVars() {
      const data = await this.call_api('api/env');
      this.envVars = data;
    },

    async saveEnvVars() {
      await this.call_api('api/env', {
        method: 'POST',
        body: JSON.stringify(this.envVars)
      });
    },
  },
  mounted() {
    this.fetchEnvVars();
    this.$toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'Current server uses HTTP and communication is not encrypted. ' +
        'DO NOT enter your API keys here!'
    });
  }
}
</script>

<style>
.env {
  padding: 2rem;
}

.env-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  height: 100%;
}

@media (max-width: 768px) {
  .env {
    padding: 1rem;
  }

  .env-section {
    padding: 1rem;
  }
}
</style>
