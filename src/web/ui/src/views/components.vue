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

  <!--              <FormField class="mb-3">-->
  <!--                <label class="field-label">Pipeline Steps:</label>-->
  <!--                <div class="pipeline-container mt-2">-->
  <!--                  <div-->
  <!--                    v-for="(step, index) in sorted_pipeline_steps"-->
  <!--                    :key="step"-->
  <!--                    class="pipeline-step"-->
  <!--                  >-->
  <!--                    <ToggleButton-->
  <!--                      v-model="config.pipeline[step]"-->
  <!--                      :on-label="step"-->
  <!--                      :off-label="step"-->
  <!--                      class="text-capitalize"-->
  <!--                    />-->
  <!--                    <i-->
  <!--                      v-if="index < sorted_pipeline_steps.length - 1"-->
  <!--                      class="pi pi-arrow-right pipeline-arrow"-->
  <!--                    ></i>-->
  <!--                  </div>-->
  <!--                </div>-->
  <!--              </FormField>-->
</template>
