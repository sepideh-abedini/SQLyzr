<template>
  <div class="scores">
    <Toast/>

    <h1>Scores Table</h1>

    <Message v-if="error" severity="error">{{ error }}</Message>

    <div class="card">
      <div class="mb-4 flex gap-2">
        <Button label="Refresh Scores" icon="pi pi-refresh" @click="fetchScores"/>
      </div>

      <ProgressSpinner v-if="loading" class="my-4"/>

      <div v-else class="scores-container">
        <DataTable :filters="filters" filter-display="row" :global-filter-fields="['model']"
                   removable-sort size="small" sort-mode="multiple" show-headers
                   v-if="tableData.rows.length > 0" :value="tableRows" stripedRows>
          <Column v-for="col in tableData.headers" :key="col" :field="col" :header="col"
                  sortable="true"/>
        </DataTable>
        <Message v-else severity="info">No scores data available</Message>
      </div>
    </div>
  </div>
</template>

<script>
import Button from "primevue/button";
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import {FilterMatchMode} from '@primevue/core/api';

export default {
  data() {
    return {
      filters: {
        global: {value: null, matchMode: FilterMatchMode.CONTAINS}
      },
      loading: false,
      error: null,
      tableData: {
        headers: [],
        rows: []
      },
      refreshInterval: null
    }
  },
  computed: {
    tableRows() {
      // Convert array data to objects with header keys
      return this.tableData.rows.map(row => {
        const obj = {};
        this.tableData.headers.forEach((header, index) => {
          obj[header] = row[index];
        });
        return obj;
      });
    }
  },
  methods: {
    async fetchScores() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('http://localhost:7777/api/results');

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.data) {
          this.tableData = data.data;
        } else {
          this.tableData = {headers: [], rows: []};
          this.error = 'No scores data available';
        }
      } catch (error) {
        this.error = `Error loading scores: ${error.message}`;
        console.error('Error loading scores:', error);
        this.tableData = {headers: [], rows: []};
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchScores();
    // Auto-refresh scores every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.fetchScores();
    }, 30000);
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
    Toast,
    DataTable,
    Column
  }
}
</script>

<style>
.scores {
  padding: 2rem;
}

.scores h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.scores-container {
  border-radius: 0.5rem;
  padding: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

</style>
