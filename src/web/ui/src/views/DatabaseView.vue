<template>
  <div class="database">
    <Toast />
    <Card>
      <template #title>
        <div class="text-center">
          <h1>Database Scaling</h1>
        </div>
      </template>
      <template #content>
        <div class="p-fluid mb-4">
          <div class="p-field">
            <label for="db-select" class="font-bold">Select Database</label>
            <AutoComplete
              id="db-select"
              v-model="selectedDb"
              :suggestions="filteredDbs"
              @complete="searchDbs"
              placeholder="Search and select a database"
              :dropdown="true"
              class="mb-3"
              aria-label="Database Selection"
            />
          </div>
        </div>

        <div class="button-container mb-4">
          <div class="action-buttons">
            <Button
              label="Get Row Counts"
              icon="pi pi-table"
              @click="getTableRows"
              :disabled="!selectedDb"
              class="p-button-primary mr-2"
              aria-label="Get Row Counts"
              severity="info"
            />

            <div class="scale-container">
              <Button
                label="Scale Database"
                icon="pi pi-window-maximize"
                @click="scaleTableRows"
                :disabled="!selectedDb"
                class="p-button-success mr-2"
                aria-label="Scale Database"
              />
              <div class="scale-input">
                <label for="scale-factor" class="scale-label">Factor:</label>
                <InputNumber
                  id="scale-factor"
                  v-model="scale"
                  showButtons
                  buttonLayout="horizontal"
                  :min="1"
                  :max="100"
                  :step="1"
                  aria-label="Scale Factor"
                />
              </div>
            </div>

            <Button
              label="Revert Changes"
              icon="pi pi-replay"
              @click="revert"
              :disabled="!selectedDb"
              aria-label="Revert Changes"
              severity="warn"
            />
          </div>
        </div>

        <div v-if="loading" class="loading-container">
          <ProgressSpinner />
          <p class="mt-2">Loading data...</p>
        </div>

        <div v-else-if="tableRows.length > 0" class="table-rows">
          <h2>{{ selectedDb }} tables statistics</h2>
          <DataTable
            :value="tableRows"
            class="p-datatable-sm"
            stripedRows
            sortField="table"
            :sortOrder="1"
            responsiveLayout="scroll"
          >
            <Column field="table" header="Table Name" sortable />
            <Column field="rows" header="Row Count" sortable>
              <template #body="slotProps">
                <span v-if="slotProps.data.error" class="error-text">
                  Error: {{ slotProps.data.error }}
                </span>
                <span v-else>
                  {{ slotProps.data.rows }}
                </span>
              </template>
            </Column>
          </DataTable>
        </div>

      </template>
    </Card>
  </div>
</template>

<script>
import Toast from 'primevue/toast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import AutoComplete from 'primevue/autocomplete'
import DataTable from 'primevue/datatable'
import InputNumber from 'primevue/inputnumber'
import Column from 'primevue/column'
import ProgressSpinner from 'primevue/progressspinner'
import apiMixin from '@/api_mixin'

export default {
  name: 'DatabaseView',
  mixins: [apiMixin],
  data() {
    return {
      dbIds: [],           // List of all available database IDs
      selectedDb: null,    // Currently selected database
      filteredDbs: [],     // Filtered database IDs for autocomplete
      tableRows: [],       // Table row count data
      loading: false,      // Loading state indicator
      scale: 1,            // Scale factor for database scaling
    }
  },
  methods: {
    /**
     * Fetches the list of available databases from the API
     */
    async fetchDatabases() {
      try {
        this.loading = true
        const response = await this.call_api('api/db/list')
        if (response && response.db_ids) {
          this.dbIds = response.db_ids.sort() // Sort alphabetically for better UX
        } else {
          throw new Error('Invalid response format')
        }
      } catch (error) {
        console.error('Error fetching databases:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Database List Error',
          detail: 'Failed to fetch the list of databases',
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },

    /**
     * Filters database IDs based on user input for the autocomplete dropdown
     * @param {Object} event - The autocomplete event object
     */
    searchDbs(event) {
      const query = event.query.toLowerCase()
      this.filteredDbs = this.dbIds.filter((db) => db.toLowerCase().includes(query))
    },

    /**
     * Fetches row counts for all tables in the selected database
     */
    async getTableRows() {
      if (!this.selectedDb) return

      try {
        this.loading = true
        this.tableRows = []

        const response = await this.call_api(
          `api/db/table_rows?db_id=${encodeURIComponent(this.selectedDb)}`,
        )

        if (response && response.tables) {
          this.tableRows = response.tables
        } else {
          throw new Error('Invalid response format')
        }
      } catch (error) {
        console.error('Error fetching table rows:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Data Loading Error',
          detail: `Failed to fetch table information for database "${this.selectedDb}". ${error.message || ''}`,
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },

    /**
     * Scales the selected database by the specified factor
     */
    async scaleTableRows() {
      if (!this.selectedDb) return

      try {
        this.loading = true
        this.$toast.add({
          severity: 'info',
          summary: 'Scaling Database',
          detail: `Scaling "${this.selectedDb}" by factor ${this.scale}`,
          life: 3000,
        })

        const response = await this.call_api(
          `api/db/scale?db_id=${encodeURIComponent(this.selectedDb)}&scale=${this.scale}`,
          { method: 'POST' },
        )

        // Show success message
        this.$toast.add({
          severity: 'success',
          summary: 'Database Scaled',
          detail: `Successfully scaled database "${this.selectedDb}" by factor ${this.scale}`,
          life: 3000,
        })

        // Refresh table data
        await this.getTableRows()
      } catch (error) {
        console.error('Error scaling database:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Scaling Error',
          detail: `Failed to scale database "${this.selectedDb}". ${error.message || ''}`,
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },

    /**
     * Reverts the selected database to its original state
     */
    async revert() {
      if (!this.selectedDb) return

      try {
        this.loading = true

        // Show info message about the operation
        this.$toast.add({
          severity: 'info',
          summary: 'Reverting Database',
          detail: `Reverting database "${this.selectedDb}" `,
          life: 3000,
        })

        const response = await this.call_api(
          `api/db/revert?db_id=${encodeURIComponent(this.selectedDb)}`,
        )

        // Show success message
        this.$toast.add({
          severity: 'success',
          summary: 'Database Reverted',
          detail: `Successfully reverted database "${this.selectedDb}" `,
          life: 3000,
        })

        // Refresh table data
        await this.getTableRows()
      } catch (error) {
        console.error('Error reverting database:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Revert Error',
          detail: `Failed to revert database "${this.selectedDb}". ${error.message || ''}`,
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },
  },
  mounted() {
    this.fetchDatabases()
  },
  components: {
    Toast,
    Card,
    Button,
    InputNumber,
    AutoComplete,
    DataTable,
    Column,
    ProgressSpinner,
  },
}
</script>

<style>
.database {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.database h1 {
  margin-bottom: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.database h2 {
  color: #3f51b5;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

/* Button container styling */
.button-container {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

/* Scale input container */
.scale-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.scale-input {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #ced4da;
}

.scale-label {
  margin-right: 0.5rem;
  font-weight: 600;
  color: #495057;
}

/* Table styling */
.table-rows {
  margin-top: 1.5rem;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.error-text {
  color: #f44336;
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 1rem;
}

/* Loading container */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #3f51b5;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .database {
    padding: 1rem;
  }

  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .scale-container {
    flex-direction: column;
    align-items: stretch;
  }

  .scale-input {
    margin-top: 0.5rem;
  }
}
</style>
