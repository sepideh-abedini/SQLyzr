<template>
  <FormField class="md:col-4">
    <label class="field-label">ETC Ratio (R):</label>
    <div class="flex align-items-center">
      <InputText v-model.number="etcr" class="w-12" />
    </div>
  </FormField>
  <FormField class="md:col-2">
    <label class="field-label">Percentile:</label>
    <div class="flex align-items-center">
      <InputText v-model.number="p" class="w-12" />
    </div>
  </FormField>
  <FormField class="md:col-3">
    <label class="field-label">Num Executions:</label>
    <div class="flex align-items-center">
      <InputText v-model.number="k" class="w-12" />
    </div>
  </FormField>
  <FormField class="md:col-2">
    <label class="field-label" style="visibility: hidden"> button </label>
    <Button :loading="calculating" label="Calculate" @click="calculate" class="p-button-primary" />
  </FormField>
</template>

<script>
import Card from 'primevue/card'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import FormField from '@primevue/forms/formfield'
import Select from 'primevue/select'
import MultiSelect from 'primevue/multiselect'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import Knob from 'primevue/knob'
import Toast from 'primevue/toast'
import { ToggleButton, AutoComplete } from 'primevue'
import LogsView from '@/views/LogsView.vue'
import ChartsView from '@/views/ChartsView.vue'

export default {
  components: {
    LogsView,
    ChartsView,
    Card,
    Button,
    Checkbox,
    InputText,
    InputNumber,
    Toast,
    FormField,
    Select,
    MultiSelect,
    Slider,
    ToggleSwitch,
    Knob,
    ToggleButton,
    AutoComplete,
  },
  data() {
    return {
      p: 95,
      k: 10,
      etcr: 1.46,
      running: false,
      loading: false,
    }
  },
  methods: {
    async calculate() {
      this.calculating = true
      this.error = null

      try {
        const response = await this.call_api('api/utils/calcr', {
          method: 'POST',
          body: JSON.stringify({
            p: this.p,
            k: this.k,
          }),
        })

        if (response) {
          this.config.etcr = response.result

          this.$toast.add({
            severity: 'success',
            summary: 'Calculation Complete',
            detail: `R calculation is done`,
            life: 3000,
          })
        }
      } catch (error) {
        console.error('Error calculating:', error)
        this.error = error.message || 'An error occurred during calculation'

        this.$toast.add({
          severity: 'error',
          summary: 'Calculation Error',
          detail: this.error,
          life: 5000,
        })
      } finally {
        this.calculating = false
      }
    },
  },
  mounted() {
  },

  beforeUnmount() {
    console.log('Unmount')
    this.clearInterval()
  },
}
</script>

<style scoped></style>
