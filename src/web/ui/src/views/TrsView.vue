<template>
  <div class="trs">
    <Toast position="bottom-right" />

    <h1>Select Repair Report</h1>
    <Tabs v-if="trsData" :value="selectedTrs" @update:value="(val) => (selectedTrs = val)">
      <!--      <TabList>-->
      <!--        <Tab v-for="(item, i) in trsData" :value="i">-->
      <!--          {{ format_file_name(item.name) }}-->
      <!--        </Tab>-->
      <!--      </TabList>-->
      <Select v-model="selectedTrs" :options="trsData.map((_, i) => i)">
        <template #option="slotProps">
          {{ format_file_name(trsData[slotProps.option].name) }}
        </template>

        <template #value="slotProps">
          <span >
            {{ format_file_name(trsData[slotProps.value].name) }}
          </span>
        </template>
      </Select>
      <TabPanels>
        <TabPanel v-for="(item, i) in trsData" :value="i">
          <h2>Repairs Summary</h2>
          <div class="grid">
            <div class="col-12 md:col-6 p-2">
              <h3>Execution Accuracy: {{ item.stats.ea }}/{{ item.stats.count }}</h3>
              <h3>Repaired: {{ item.stats.repaired }}/{{ item.stats.count - item.stats.ea }}</h3>
            </div>
          </div>

          <div v-if="repairs.length > 0" class="trs-container">
            <TabView>
              <TabPanel header="Grouped View">
                <div v-for="(group, index) in groupedByMessages" :key="index" class="message-group">
                  <div class="message-group-header">
                    <div class="flex align-items-center justify-content-between">
                      <Tag severity="info" value="">Group {{ index + 1 }}</Tag>
                      <div class="flex align-items-center">
                        <Badge size="xlarge">
                          {{ group.count }}/{{ repairs.length }} Repairs
                        </Badge>
                      </div>
                    </div>
                    <div class="message-list">
                      <ul>
                        <li v-for="(message, msgIndex) in group.messages" :key="msgIndex">
                          {{ message }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <Button
                    label="View Repairs"
                    icon="pi pi-list"
                    @click="showGroupDetails(group)"
                    class="mt-2"
                  />
                </div>
              </TabPanel>

              <TabPanel header="List View">
                <div class="p-grid">
                  <div class="p-col-4 element-list">
                    <div
                      v-for="(item, index) in repairs"
                      :key="index"
                      class="element-item"
                      :class="{ selected: selectedElement === item }"
                      @click="selectElement(item)"
                    >
                      <Badge class="element-number" severity="info">{{ index + 1 }}</Badge>
                      <Tag severity="secondary" class="element-db">Database: {{ item.db_id }} </Tag>
                    </div>
                  </div>
                  <div class="p-col-8 element-details" v-if="selectedElement">
                    <h4>Element Details</h4>
                    <SQLDiff :gold="selectedElement.gold" :pred="selectedElement.pred" />
                    <div class="trs-messages">
                      <h5>Repair Messages</h5>
                      <ul>
                        <li v-for="(message, msgIndex) in selectedElement.messages" :key="msgIndex">
                          {{ message }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div class="p-col-8 element-details" v-else>
                    <Message
                      severity="info"
                      text="Select an element from the list to view details."
                    />
                  </div>
                </div>
              </TabPanel>
            </TabView>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>

  <Dialog
    v-model:visible="groupDetailsVisible"
    header="Error Fixing Suggestions"
    :style="{ width: '80vw' }"
    :modal="true"
  >
    <div v-if="selectedGroup" class="group-details">
      <div>
        <ul class="mb-3">
          <li v-for="(message, msgIndex) in selectedGroup.messages" :key="msgIndex">
            {{ message }}
          </li>
        </ul>
      </div>

      <div v-for="(item, index) in selectedGroup.items" :key="index" class="trs-item">
        <div class="trs-item-header">
          <Badge class="trs-item-number" severity="info">{{ index + 1 }}</Badge>
          <Tag severity="info" class="trs-item-db">Database: {{ item.db_id }}</Tag>
        </div>
        <div class="trs-item-content">
          <SQLDiff :gold="item.gold" :pred="item.pred" />
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script>
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import Dropdown from 'primevue/dropdown'
import TabView from 'primevue/tabview'
import Dialog from 'primevue/dialog'
import Knob from 'primevue/knob'
import { Badge, Tag, Tab, TabList, TabPanel, Tabs, TabPanels } from 'primevue'

import * as DiffMatchPatch from 'diff-match-patch'
import 'prismjs'
import 'prismjs/components/prism-sql'
import 'prismjs/themes/prism.css'
import SQLDiff from '@/views/components/SqlDiff.vue'
import MultiSelect from 'primevue/multiselect'
import Select from 'primevue/select'

export default {
  components: {
    SQLDiff,
    Badge,
    Button,
    Message,
    ProgressSpinner,
    Toast,
    Dropdown,
    TabView,
    TabPanel,
    Dialog,
    Knob,
    Tab,
    Tag,
    Tabs,
    TabPanels,
    TabList,
    MultiSelect,
    Select,
  },
  data() {
    return {
      loading: false,
      error: null,
      models: [],
      datasets: [],
      selectedModel: null,
      selectedDataset: null,
      trsData: null,
      fetchAttempted: false,
      selectedElement: null,
      groupDetailsVisible: false,
      selectedGroup: null,
      dmp: new DiffMatchPatch.diff_match_patch(),
      showDiff: true,
      selectedTrs: null,
      pred: 'SELECT t1.a, t2.b, t2.c FROM t1 JOIN t2',
      gold: 'SELECT a, b FROM t1 JOIN t2',
    }
  },
  computed: {
    stats() {
      return this.trsData[this.selectedTrs].stats
    },
    repairs() {
      return this.trsData[this.selectedTrs].repairs
    },
    groupedByMessages() {
      if (!this.repairs) return []

      const groups = {}
      this.repairs.forEach((item) => {
        const messagesKey = JSON.stringify(item.messages.sort())
        if (!groups[messagesKey]) {
          groups[messagesKey] = {
            messages: item.messages,
            items: [],
            count: 0,
          }
        }
        groups[messagesKey].items.push(item)
        groups[messagesKey].count++
      })

      return Object.values(groups).sort((a, b) => b.count - a.count)
    },
  },
  methods: {
    format_file_name(file_name) {
      const parts = file_name.split('/')
      console.log(parts)
      file_name = parts[parts.length - 1]
      file_name = file_name.replace('trs', '')
      const tokens = file_name.split('_')

      const temp = tokens[tokens.length - 2]
      const iteration = tokens[tokens.length - 1]
      const base = tokens.slice(0, -2).join(' ')

      return `${base}, temp = ${temp}, iteration = ${iteration}`
    },
    async fetchTrsData() {
      this.loading = true
      this.error = null
      this.trsData = null
      this.selectedElement = null
      this.selectedGroup = null
      this.fetchAttempted = true

      try {
        const data = await this.call_api(`api/trs`)
        this.trsData = data

        if (this.trsData && this.trsData.length > 0) {
          this.selectedTrs = 0
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: `Loaded ${this.trsData.length} repair suggestions`,
            life: 3000,
          })
          this.selectedElement = this.repairs[0]
        } else {
          this.$toast.add({
            severity: 'info',
            summary: 'Info',
            detail: 'No repair suggestions found',
            life: 3000,
          })
        }
      } catch (error) {
        this.error = `Error loading TRS data: ${error.message}`
        console.error('Error loading TRS data:', error)
      } finally {
        this.loading = false
      }
    },
    selectElement(element) {
      this.selectedElement = element
    },
    showGroupDetails(group) {
      this.selectedGroup = group
      this.groupDetailsVisible = true
    },
  },
  async mounted() {
    this.selectedModel = this.models[0]
    this.selectedDataset = this.datasets[0]
    await this.fetchTrsData()
    this.selectedTrs = 0
  },
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
  box-shadow:
    0 2px 1px -1px rgba(0, 0, 0, 0.2),
    0 1px 1px 0 rgba(0, 0, 0, 0.14),
    0 1px 3px 0 rgba(0, 0, 0, 0.12);
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
  background-color: #2196f3;
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

.error-message,
.no-data-message {
  margin-top: 1.5rem;
}

/* Summary Tab Styles */
.message-group {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  background-color: #f9f9f9;
}

.message-group-header {
  margin-bottom: 0.5rem;
}

.message-list ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message-list li {
  margin-bottom: 0.25rem;
}

/* Details Tab Styles */
.p-grid {
  display: flex;
  flex-wrap: wrap;
  margin: -0.5rem;
}

.p-col-4,
.p-col-8 {
  padding: 0.5rem;
  box-sizing: border-box;
}

.p-col-4 {
  flex: 0 0 33.3333%;
  max-width: 33.3333%;
}

.p-col-8 {
  flex: 0 0 66.6667%;
  max-width: 66.6667%;
}

.element-list {
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
}

.element-item {
  padding: 0.75rem;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.element-item:last-child {
  border-bottom: none;
}

.element-item:hover {
  background-color: #f5f5f5;
}

.element-item.selected {
  background-color: #e3f2fd;
}

.element-number {
  background-color: #2196f3;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  margin-right: 0.75rem;
}

.element-db {
  font-weight: bold;
}

.element-details {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  background-color: #fff;
}

/* Group Details Dialog Styles */
.group-details {
  max-height: 70vh;
  overflow-y: auto;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.diff-toggle {
  margin-bottom: 1rem;
}

/* Diff highlighting styles */
.diff-added {
  background-color: #e6ffed;
  color: #22863a;
  text-decoration: none;
  border-radius: 2px;
  padding: 0 1px;
}

.diff-removed {
  background-color: #ffeef0;
  color: #cb2431;
  text-decoration: line-through;
  border-radius: 2px;
  padding: 0 1px;
}

.diff-changed {
  background-color: #e6f7ff;
  color: #0366d6;
  text-decoration: none;
  border-radius: 2px;
  padding: 0 1px;
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

  .p-grid {
    flex-direction: column;
  }

  .p-col-4,
  .p-col-8 {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .element-list {
    max-height: 300px;
    margin-bottom: 1rem;
  }
}
</style>
