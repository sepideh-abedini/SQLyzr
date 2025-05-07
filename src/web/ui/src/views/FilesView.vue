<template>
  <div class="files">
    <Toast/>
    <ConfirmDialog/>

    <h1>SQLyr Output Files</h1>

    <div class="card">
      <h2>File Explorer</h2>
      <div class="path-navigation">
        <Button icon="pi pi-home" @click="navigateTo('')" class="p-button-sm"/>
        <Button icon="pi pi-trash" @click="deleteAllFiles" class="p-button-sm p-button-danger ml-2"
                title="Delete all files"/>
        <span v-for="(segment, index) in pathSegments" :key="index" class="path-segment">
          <span class="separator" v-if="index > 0">/</span>
          <Button :label="segment" class="p-button-text p-button-sm"
                  @click="navigateToSegment(index)"/>
        </span>
      </div>

      <ProgressSpinner v-if="loading" class="my-4"/>

      <div v-else class="file-list">
        <DataTable :value="items" class="p-datatable-sm" stripedRows>
          <Column field="name" header="Name">
            <template #body="slotProps">
              <div class="file-item" @click="handleItemClick(slotProps.data)">
                <i :class="slotProps.data.is_dir ? 'pi pi-folder' : 'pi pi-file'" class="mr-2"></i>
                {{ slotProps.data.name }}
              </div>
            </template>
          </Column>
          <Column field="lines" header="Lines">
            <template #body="slotProps">
              {{ slotProps.data.is_dir ? '-' : slotProps.data.lines }}
            </template>
          </Column>
          <Column field="size" header="Size">
            <template #body="slotProps">
              {{ slotProps.data.is_dir ? '-' : formatSize(slotProps.data.size) }}
            </template>
          </Column>
        </DataTable>
      </div>

      <Dialog v-model:visible="fileDialogVisible" :header="selectedFile?.name"
              :style="{width: '80vw'}" :modal="true">
        <div v-if="fileContent" class="file-content">
          <pre>{{ fileContent }}</pre>
        </div>
        <div v-else-if="fileLoading" class="text-center">
          <ProgressSpinner/>
        </div>
      </Dialog>
    </div>
  </div>
</template>

<script>
import Toast from 'primevue/toast';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import ProgressSpinner from 'primevue/progressspinner';
import ConfirmDialog from 'primevue/confirmdialog';
import {API_BASE_URL} from '../config';

export default {
  data() {
    return {
      loading: false,
      currentPath: '',
      items: [],
      home: null,
      selectedFile: null,
      fileDialogVisible: false,
      fileContent: null,
      fileLoading: false
    }
  },
  computed: {
    pathSegments() {
      if (!this.currentPath) return [this.home];
      return [this.home, ...this.currentPath.split('/')];
    }
  },
  methods: {
    async fetchDirectoryContents(path) {
      this.loading = true;

      try {
        const data = await this.call_api(`api/files?path=${encodeURIComponent(path)}`);
        this.home = data.home;
        this.items = data.items;
        this.currentPath = data.path;
      } catch (error) {
        console.error('Error loading directory contents:', error);
      } finally {
        this.loading = false;
      }
    },

    async fetchFileContent(path) {
      this.fileLoading = true;
      this.fileContent = null;

      try {
        const data = await this.call_api(`api/files/content?path=${encodeURIComponent(path)}`);
        this.fileContent = data.content;
      } catch (error) {
        console.error('Error loading file content:', error);
      } finally {
        this.fileLoading = false;
      }
    },

    handleItemClick(item) {
      if (item.is_dir) {
        this.navigateTo(item.path);
      } else {
        this.selectedFile = item;
        this.fileDialogVisible = true;
        this.fetchFileContent(item.path);
      }
    },

    navigateTo(path) {
      this.fetchDirectoryContents(path);
    },

    navigateToSegment(index) {
      if (index === 0) {
        this.navigateTo('');
      } else {
        const segments = this.pathSegments.slice(1, index + 1);
        this.navigateTo(segments.join('/'));
      }
    },

    formatSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    deleteAllFiles() {
      this.$confirm.require({
        message: 'Are you sure you want to delete all files in this directory?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
          try {
            await this.call_api(`api/files/delete_all?path=${encodeURIComponent(this.currentPath)}`, {
              method: 'POST'
            });
            this.$toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'All files deleted successfully',
              life: 3000
            });
            this.fetchDirectoryContents(this.currentPath);
          } catch (error) {
            console.error('Error deleting files:', error);
            this.$toast.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to delete files',
              life: 3000
            });
          }
        }
      });
    }
  },
  mounted() {
    this.fetchDirectoryContents('');
  },
  components: {
    Toast,
    Button,
    DataTable,
    Column,
    Dialog,
    ProgressSpinner,
    ConfirmDialog
  }
}
</script>

<style>
.files {
  padding: 2rem;
}

.files h1 {
  margin-bottom: 2rem;
  font-weight: bold;
}

.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

.path-navigation {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 0.25rem;
  overflow-x: auto;
}

.path-segment {
  display: inline-flex;
  align-items: center;
}

.separator {
  margin: 0 0.25rem;
  color: #6c757d;
}

.file-list {
  margin-top: 1rem;
}

.file-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.file-item:hover {
  color: #2196F3;
}

.file-content {
  max-height: 70vh;
  overflow-y: auto;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.25rem;
}

.file-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
}

</style>
