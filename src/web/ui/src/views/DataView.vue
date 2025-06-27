<template>
  <div class="data">
    <Toast />
    <ConfirmDialog />

    <Card>
      <template #title>
        <div class="text-center">
          <h1>Input Data Files</h1>
        </div>
      </template>
      <template #content>

        <div class="path-navigation">
          <Button icon="pi pi-home" @click="navigateTo('')" class="p-button-sm" />
          <Button
            icon="pi pi-trash"
            @click="deleteTopLevelContents"
            class="p-button-sm p-button-danger ml-2"
            title="Delete all files in top-level directory"
          />
          <span v-for="(segment, index) in pathSegments" :key="index" class="path-segment">
          <span class="separator" v-if="index > 0">/</span>
          <Button
            :label="segment"
            class="p-button-text p-button-sm"
            @click="navigateToSegment(index)"
          />
        </span>
          <Button
            v-if="currentPath"
            icon="pi pi-trash"
            @click="deleteAllFiles"
            class="p-button-sm p-button-danger ml-auto"
            title="Delete all files in current directory"
          />
          <FileUpload
            mode="basic"
            accept=".zip"
            :maxFileSize="50000000"
            customUpload
            @uploader="uploadZip"
            :auto="true"
            chooseLabel="Upload ZIP"
            class="ml-2"
          />
        </div>

        <ProgressSpinner v-if="loading" class="my-4" />

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
            <Column header="Actions" style="width: 150px">
              <template #body="slotProps">
                <Button
                  icon="pi pi-pencil"
                  class="p-button-sm p-button-secondary mr-2"
                  @click.stop="promptRename(slotProps.data)"
                  title="Rename file/directory"
                />
                <Button
                  icon="pi pi-trash"
                  class="p-button-sm p-button-danger"
                  @click.stop="deleteFile(slotProps.data)"
                  title="Delete file/directory"
                />
              </template>
            </Column>
          </DataTable>
        </div>

        <Dialog
          v-model:visible="fileDialogVisible"
          :header="selectedFile?.name"
          :style="{ width: '80vw' }"
          :modal="true"
        >
          <div v-if="fileContent" class="file-content">
            <pre>{{ fileContent }}</pre>
          </div>
          <div v-else-if="fileLoading" class="text-center">
            <ProgressSpinner />
          </div>
        </Dialog>

        <Dialog
          v-model:visible="renameDialogVisible"
          header="Rename Item"
          :style="{ width: '30vw' }"
          :modal="true"
        >
          <div class="p-fluid">
            <div class="p-field">
              <label for="newName">New Name</label>
              <InputText id="newName" v-model="newName" autofocus />
            </div>
          </div>
          <template #footer>
            <Button
              label="Cancel"
              icon="pi pi-times"
              class="p-button-text"
              @click="renameDialogVisible = false"
            />
            <Button label="Rename" icon="pi pi-check" class="p-button-text" @click="renameItem" />
          </template>
        </Dialog>
      </template>
    </Card>
  </div>
</template>
<script>
import Toast from 'primevue/toast'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import ConfirmDialog from 'primevue/confirmdialog'
import FileUpload from 'primevue/fileupload'
import InputText from 'primevue/inputtext'
import Card from 'primevue/card'
import { API_BASE_URL } from '../config'

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
      fileLoading: false,
      renameDialogVisible: false,
      itemToRename: null,
      newName: '',
    }
  },
  computed: {
    pathSegments() {
      if (!this.currentPath) return [this.home]
      return [this.home, ...this.currentPath.split('/')]
    },
  },
  methods: {
    async fetchDirectoryContents(path) {
      this.loading = true

      try {
        const data = await this.call_api(`api/data?path=${encodeURIComponent(path)}`)
        this.home = data.home
        this.items = data.items
        this.currentPath = data.path
      } catch (error) {
        console.error('Error loading directory contents:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchFileContent(path) {
      this.fileLoading = true
      this.fileContent = null

      try {
        const data = await this.call_api(`api/data/content?path=${encodeURIComponent(path)}`)
        this.fileContent = data.content
      } catch (error) {
        console.error('Error loading file content:', error)
      } finally {
        this.fileLoading = false
      }
    },

    handleItemClick(item) {
      if (item.is_dir) {
        this.navigateTo(item.path)
      } else {
        this.selectedFile = item
        this.fileDialogVisible = true
        this.fetchFileContent(item.path)
      }
    },

    navigateTo(path) {
      this.fetchDirectoryContents(path)
    },

    navigateToSegment(index) {
      if (index === 0) {
        this.navigateTo('')
      } else {
        const segments = this.pathSegments.slice(1, index + 1)
        this.navigateTo(segments.join('/'))
      }
    },

    formatSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    deleteAllFiles() {
      this.$confirm.require({
        message: 'Are you sure you want to delete all files in this directory?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
          try {
            await this.call_api(
              `api/data/delete_all?path=${encodeURIComponent(this.currentPath)}`,
              {
                method: 'POST',
              },
            )
            this.$toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'All files deleted successfully',
              life: 3000,
            })
            this.fetchDirectoryContents(this.currentPath)
          } catch (error) {
            console.error('Error deleting files:', error)
            this.$toast.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to delete files',
              life: 3000,
            })
          }
        },
      })
    },

    deleteFile(item) {
      const isDirectory = item.is_dir
      const itemType = isDirectory ? 'directory' : 'file'

      this.$confirm.require({
        message: `Are you sure you want to delete this ${itemType}?`,
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
          try {
            await this.call_api(`api/data/delete?path=${encodeURIComponent(item.path)}`, {
              method: 'POST',
            })
            this.$toast.add({
              severity: 'success',
              summary: 'Success',
              detail: `${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully`,
              life: 3000,
            })
            this.fetchDirectoryContents(this.currentPath)
          } catch (error) {
            console.error(`Error deleting ${itemType}:`, error)
            this.$toast.add({
              severity: 'error',
              summary: 'Error',
              detail: `Failed to delete ${itemType}`,
              life: 3000,
            })
          }
        },
      })
    },

    deleteTopLevelContents() {
      this.$confirm.require({
        message: 'Are you sure you want to delete all files in the top-level directory?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
          try {
            await this.call_api(`api/data/delete_all?path=`, {
              method: 'POST',
            })
            this.$toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'All files in top-level directory deleted successfully',
              life: 3000,
            })
            // Refresh the current directory view
            this.fetchDirectoryContents(this.currentPath)
          } catch (error) {
            console.error('Error deleting top-level files:', error)
            this.$toast.add({
              severity: 'error',
              summary: 'Error',
              detail: 'Failed to delete top-level files',
              life: 3000,
            })
          }
        },
      })
    },

    uploadZip(event) {
      const file = event.files[0]

      if (!file) {
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No file selected',
          life: 3000,
        })
        return
      }

      if (!file.name.endsWith('.zip')) {
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'File must be a zip archive',
          life: 3000,
        })
        return
      }

      const formData = new FormData()
      formData.append('file', file)

      this.loading = true

      fetch(`${API_BASE_URL}/api/data/upload`, {
        method: 'POST',
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            throw new Error(data.error)
          }

          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: data.message,
            life: 3000,
          })

          // Refresh the current directory view
          this.fetchDirectoryContents(this.currentPath)
        })
        .catch((error) => {
          console.error('Error uploading zip file:', error)
          this.$toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.message || 'Failed to upload zip file',
            life: 3000,
          })
        })
        .finally(() => {
          this.loading = false
        })
    },

    promptRename(item) {
      this.itemToRename = item
      this.newName = item.name
      this.renameDialogVisible = true
    },

    async renameItem() {
      if (!this.itemToRename || !this.newName) {
        return
      }

      if (this.newName === this.itemToRename.name) {
        this.renameDialogVisible = false
        return
      }

      try {
        const response = await this.call_api('api/data/rename', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            path: this.itemToRename.path,
            new_name: this.newName,
          }),
        })

        this.$toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Item renamed successfully',
          life: 3000,
        })

        // Refresh the current directory view
        this.fetchDirectoryContents(this.currentPath)
      } catch (error) {
        console.error('Error renaming item:', error)
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: error.message || 'Failed to rename item',
          life: 3000,
        })
      } finally {
        this.renameDialogVisible = false
      }
    },
  },
  mounted() {
    this.fetchDirectoryContents('')
  },
  components: {
    Toast,
    Button,
    DataTable,
    Column,
    Dialog,
    ProgressSpinner,
    ConfirmDialog,
    FileUpload,
    InputText,
    Card,
  },
}
</script>

<style>
.data {
  padding: 2rem;
}

.data h1 {
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
  color: #2196f3;
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

.p-fileupload-buttonbar {
  display: flex;
  justify-content: flex-end;
}
</style>
