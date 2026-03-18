<script setup lang="ts"></script>
<template>
  <FormField class="md:col-4">
    <label class="field-label">ETC Ratio (R):</label>
    <div class="flex align-items-center">
      <InputText v-model.number="config.etcr" class="w-12" />
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
