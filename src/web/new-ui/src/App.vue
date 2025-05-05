<script setup lang="ts">
import {RouterLink, RouterView} from 'vue-router'
</script>

<template>
  <div>
    <header>
      <nav>
        <RouterLink to="/">Configuration</RouterLink>
        |
        <RouterLink to="/logs">Logs</RouterLink>
        |
        <RouterLink to="/scores">Scores</RouterLink>
        |
        <RouterLink to="/charts">Charts</RouterLink>
      </nav>
    </header>
    <main>
      <RouterView/>
    </main>
  </div>
</template>

<style scoped>
nav {
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}
</style>
