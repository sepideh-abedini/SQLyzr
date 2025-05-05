<script setup lang="ts">
import {RouterLink, RouterView} from 'vue-router'
</script>

<template>
  <nav>
    <RouterLink to="/">Configuration</RouterLink>
    |
    <RouterLink to="/logs">Logs</RouterLink>
    |
    <RouterLink to="/scores">Scores</RouterLink>
    |
    <RouterLink to="/charts">Charts</RouterLink>
  </nav>
  <RouterView/>
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
