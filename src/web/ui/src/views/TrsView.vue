<template>
  <div class="trs">
    <Toast/>

    <h1>Error Fixing Suggestions</h1>

    <div class="card">
      <h2>Select Model and Dataset</h2>
      <div class="selection-container">
        <div class="p-field">
          <label for="model">Model</label>
          <Dropdown id="model" v-model="selectedModel" :options="models"
                    placeholder="Select a Model" class="w-full"
                    @value-change="fetchTrsData"
          />
        </div>
        <div class="p-field">
          <label for="dataset">Dataset</label>
          <Dropdown id="dataset" v-model="selectedDataset" :options="datasets"
                    placeholder="Select a Dataset" class="w-full"
                    @value-change="fetchTrsData"
          />
        </div>
      </div>
      <Tabs v-if="trsData" v-model="selectedTrs">
        <TabList>
          <Tab v-for="(item,i) in trsData" :value="i">
            {{ item.name }}
          </Tab>
        </TabList>
        <TabPanels>
          <TabPanel v-for="(item,i) in trsData" :value="i">
            <h1>Repairs Summary</h1>
            <div class="grid">
              <div class="col-12 md:col-6 p-2">
                <h3> Execution Accuracy:</h3>
                <Knob disabled :model-value="item.stats.ea" :max="item.stats.count"/>
              </div>
              <div class="col-12 md:col-6 p-2">
                <h3> Repaired:</h3>
                <Knob disabled :model-value="item.stats.repaired" :max="item.stats.count - item.stats.ea"/>
              </div>
            </div>

            <div v-if="repairs.length > 0" class="trs-container">
              <TabView>
                <TabPanel header="Grouped View">
                  <div v-for="(group, index) in groupedByMessages" :key="index"
                       class="message-group">
                    <div class="message-group-header">
                      <div class="flex align-items-center justify-content-between">
                        <Tag severity="info" value="">Group {{ index + 1 }}</Tag>
                        <div class="flex align-items-center">
                          <Badge size="xlarge"> {{ group.count }}/{{ repairs.length }} Repairs
                          </Badge>
                        </div>
                      </div>
                      <div class="message-list">
                        <ul>
                          <li v-for="(message, msgIndex) in group.messages" :key="msgIndex">{{
                              message
                            }}
                          </li>
                        </ul>
                      </div>
                    </div>
                    <Button label="View Repairs" icon="pi pi-list" @click="showGroupDetails(group)"
                            class="mt-2"/>
                  </div>
                </TabPanel>

                <TabPanel header="List View">
                  <div class="p-grid">
                    <div class="p-col-4 element-list">
                      <div v-for="(item, index) in repairs" :key="index"
                           class="element-item"
                           :class="{ 'selected': selectedElement === item }"
                           @click="selectElement(item)">
                        <Badge class="element-number" severity="info">{{ index + 1 }}</Badge>
                        <Tag severity="secondary" class="element-db">Database: {{
                            item.db_id
                          }}
                        </Tag>
                      </div>
                    </div>
                    <div class="p-col-8 element-details" v-if="selectedElement">
                      <h4>Element Details</h4>
                      <div class="diff-toggle">
                        <Button :label="showDiff ? 'Hide Diff' : 'Show Diff'"
                                :icon="showDiff ? 'pi pi-eye-slash' : 'pi pi-eye'"
                                @click="showDiff = !showDiff"
                                class="p-button-sm mb-2"/>
                      </div>
                      <div class="trs-sql">
                        <h5>Predicted SQL (Wrong)</h5>
                        <pre v-html="highlightSQL(selectedElement.pred)"></pre>
                      </div>
                      <div class="trs-sql">
                        <h5>Gold SQL (Correct)</h5>
                        <pre v-html="showDiff ? calculateDiff(selectedElement.pred, selectedElement.gold) : highlightSQL(selectedElement.gold)"></pre>
                      </div>
                      <div class="trs-messages">
                        <h5>Repair Messages</h5>
                        <ul>
                          <li v-for="(message, msgIndex) in selectedElement.messages"
                              :key="msgIndex">
                            {{ message }}
                          </li>
                        </ul>
                      </div>
                    </div>
                    <div class="p-col-8 element-details" v-else>
                      <Message severity="info"
                               text="Select an element from the list to view details."/>
                    </div>
                  </div>
                </TabPanel>
              </TabView>
            </div>

          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>


    <Dialog v-model:visible="groupDetailsVisible"
            header="Error Fixing Suggestions"
            :style="{width: '80vw'}" :modal="true">
      <div v-if="selectedGroup" class="group-details">
        <div>
          <div class="diff-toggle">
            <Button :label="showDiff ? 'Hide Diff' : 'Show Diff'"
                    :icon="showDiff ? 'pi pi-eye-slash' : 'pi pi-eye'"
                    @click="showDiff = !showDiff"
                    class="p-button-sm mb-2"/>
          </div>
          <ul class="mb-3">
            <li v-for="(message, msgIndex) in selectedGroup.messages" :key="msgIndex">{{
                message
              }}
            </li>
          </ul>
        </div>

        <div v-for="(item, index) in selectedGroup.items" :key="index" class="trs-item">
          <div class="trs-item-header">
            <Badge class="trs-item-number" severity="info">{{ index + 1 }}</Badge>
            <Tag severity="info" class="trs-item-db">Database: {{ item.db_id }}</Tag>
          </div>
          <div class="trs-item-content">
            <div class="trs-sql">
              <Tag severity="warn">Predicted SQL</Tag>
              <pre
                v-html="showDiff ? calculateDiff(item.pred, item.gold) : highlightSQL(item.pred)"></pre>
            </div>
            <div class="trs-sql">
              <Tag>Gold SQL</Tag>
              <pre v-html="highlightSQL(item.gold)"></pre>
            </div>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
import Button from "primevue/button";
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import Dropdown from 'primevue/dropdown';
import TabView from 'primevue/tabview';
import Dialog from 'primevue/dialog';
import Knob from 'primevue/knob';
import {Badge, Tag, Tab, TabList, TabPanel, Tabs, TabPanels} from 'primevue';

import * as DiffMatchPatch from 'diff-match-patch';
import 'prismjs';
import 'prismjs/components/prism-sql';
import 'prismjs/themes/prism.css';

export default {
  components: {
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
    TabList
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
      selectedTrs: 0,
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
      if (!this.repairs) return [];

      const groups = {};
      this.repairs.forEach(item => {
        const messagesKey = JSON.stringify(item.messages.sort());
        if (!groups[messagesKey]) {
          groups[messagesKey] = {
            messages: item.messages,
            items: [],
            count: 0
          };
        }
        groups[messagesKey].items.push(item);
        groups[messagesKey].count++;
      });

      return Object.values(groups).sort((a, b) => b.count - a.count);
    }
  },
  methods: {
    highlightSQL(sql) {
      return Prism.highlight(sql, Prism.languages.sql, 'sql');
    },
    calculateDiff(base, target) {
      const diffs = this.dmp.diff_main(base, target);
      this.dmp.diff_cleanupSemantic(diffs);

      let html = '';
      for (const [op, text] of diffs) {
        if (op === 1) {
          html += `<span class="diff-added">${this.highlightSQL(text)}</span>`;
        } else if (op === -1) {
          html += `<span class="diff-removed">${this.highlightSQL(text)}</span>`;
        } else {
          html += this.highlightSQL(text);
        }
      }
      return html;
    },

    async fetchModels() {
      try {
        const data = await this.call_api('api/models');
        this.models = data.models;
      } catch (error) {
        this.error = `Error loading models: ${error.message}`;
        console.error('Error loading models:', error);
      }
    },

    async fetchDatasets() {
      try {
        const data = await this.call_api('api/datasets');
        this.datasets = data.datasets;
      } catch (error) {
        this.error = `Error loading datasets: ${error.message}`;
        console.error('Error loading datasets:', error);
      }
    },

    async fetchTrsData() {
      this.loading = true;
      this.error = null;
      this.trsData = null;
      this.selectedElement = null;
      this.selectedGroup = null;
      this.fetchAttempted = true;

      try {
        const data = await this.call_api(`api/trs?model=${this.selectedModel}&dataset=${this.selectedDataset}`);
        console.log('TRS data:', data);
        this.trsData = data;

        if (this.trsData && this.trsData.length > 0) {
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: `Loaded ${this.trsData.length} repair suggestions`,
            life: 3000
          });
        } else {
          this.$toast.add({
            severity: 'info',
            summary: 'Info',
            detail: 'No repair suggestions found',
            life: 3000
          });
        }
      } catch (error) {
        this.error = `Error loading TRS data: ${error.message}`;
        console.error('Error loading TRS data:', error);
      } finally {
        this.loading = false;
      }
    },

    selectElement(element) {
      this.selectedElement = element;
    },

    showGroupDetails(group) {
      this.selectedGroup = group;
      this.groupDetailsVisible = true;
    }
  },
  async mounted() {
    await this.fetchModels();
    await this.fetchDatasets();
    this.selectedModel = this.models[0];
    this.selectedDataset = this.datasets[0];
    await this.fetchTrsData();
    this.selectedTrs = 0;
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
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
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
  background-color: #2196F3;
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

.error-message, .no-data-message {
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

.p-col-4, .p-col-8 {
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
  background-color: #2196F3;
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

  .p-col-4, .p-col-8 {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .element-list {
    max-height: 300px;
    margin-bottom: 1rem;
  }

}
</style>
