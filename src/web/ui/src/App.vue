<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Menubar from 'primevue/menubar'
</script>

<template>
  <Menubar>
    <template #start>
      <h1>SQLyzr</h1>
    </template>
    <template #end>
      <div class="flex items-center gap-2">
        <RouterLink to="/">Configuration</RouterLink>
        <RouterLink to="/aug">Aug</RouterLink>
        <!--        <RouterLink to="/database">Scale</RouterLink>-->
        <RouterLink to="/status">Execution</RouterLink>
        <RouterLink to="/logs">Logs</RouterLink>
        <RouterLink to="/scores">Scores</RouterLink>
        <RouterLink to="/charts">Charts</RouterLink>
        <RouterLink to="/files">Files</RouterLink>
        <RouterLink to="/data">Data</RouterLink>
        <!--        <RouterLink to="/trs">Repair Suggestions</RouterLink>-->
        <!--        <RouterLink to="/env">Environment Variables</RouterLink>-->
      </div>
    </template>
  </Menubar>
  <RouterView />
</template>

<style scoped>
header {
  margin-top: 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}
</style>
