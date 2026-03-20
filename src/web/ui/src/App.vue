<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Menubar from 'primevue/menubar'
import { BUILD_VERSION } from './config'
</script>

<template>
  <Menubar>
    <template #start>
      <h1>SQLyzr</h1>
    </template>
    <template #end>
      <div class="flex items-center gap-2">
        <RouterLink to="/">Dashboard</RouterLink>
        <!--        <RouterLink to="/status">Execution</RouterLink>-->
        <RouterLink to="/charts">Charts</RouterLink>
        <!--        <RouterLink to="/aug">Augmentation</RouterLink>-->
        <RouterLink to="/scores">Scores</RouterLink>
        <RouterLink to="/logs">Logs</RouterLink>
        <RouterLink to="/files">Files</RouterLink>
        <RouterLink to="/data">Data</RouterLink>
        <!--        <RouterLink to="/env">Environment Variables</RouterLink>-->
      </div>
    </template>
  </Menubar>
  <main class="content">
    <RouterView />
  </main>

  <footer class="footer">
    <span>Build version: {{ BUILD_VERSION.slice(0, 7) }} </span>
  </footer>
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
