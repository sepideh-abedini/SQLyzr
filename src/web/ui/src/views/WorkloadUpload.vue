<template>
  <Button label="Upload" @click="visible = true" icon="pi pi-upload" severity="info" />
  <Dialog v-model:visible="visible" modal header="Upload Custom Workload">
    <div class="grid">
      <div class="col-12 text-align-center">
        Upload a zip file containing the custom workload data.
      </div>
      <div class="col-12">
        <div class="flex justify-end gap-2">
          <FileUpload
            mode="basic"
            accept=".zip"
            :maxFileSize="50000000"
            customUpload
            @uploader="onUpload"
            :auto="true"
            chooseLabel="Upload ZIP"
            class="ml-2"
          />
        </div>
        <div class="col-12">
          <label class="field-label">Overwrite Existing Files?</label>
          <div class="flex align-items-center h-full">
            <ToggleSwitch v-model="overwrite" />
            <span class="ml-2">{{ overwrite ? 'On' : 'Off' }}</span>
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script>
import Card from 'primevue/card'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import { API_BASE_URL } from '@/config.ts'
import ToggleSwitch from 'primevue/toggleswitch'
import Dialog from 'primevue/dialog'

export default {
  components: {
    Card,
    FileUpload,
    ToggleSwitch,
    Button,
    Dialog,
  },
  data() {
    return {
      loading: false,
      overwrite: true,
      visible: false,
    }
  },
  methods: {
    onUpload(event) {
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

      fetch(`${API_BASE_URL}/api/data/upload?overwrite=${this.overwrite}`, {
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
            detail: 'Workload uploaded successfully. Select the Custom to use this workload.',
            life: 3000,
          })
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
          this.visible = false
        })
    },
  },
}
</script>
