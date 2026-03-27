<script setup lang="ts">
import Menubar from 'primevue/menubar'
import { BUILD_VERSION } from './config'

const items = [
  { label: 'Dashboard', route: '/' },
  { label: 'Plots', route: '/plots' },
  { label: 'Error Analysis', route: '/errors' },
  { label: 'Categories', route: '/categories' },
  { label: 'Scores', route: '/scores' },
  { label: 'Logs', route: '/logs' },
  { label: 'Files', route: '/files' },
  { label: 'Data', route: '/data' },
]
</script>

<template>
  <Menubar :model="items">
    <template #start>
      <h1>SQLyzr</h1>
    </template>

    <template #item="{ item, props }">
      <router-link v-if="item.route" :to="item.route" custom v-slot="{ href, navigate, isActive }">
        <a
          v-ripple
          :href="href"
          v-bind="props.action"
          @click="navigate"
          :class="{ active: isActive }"
        >
          <span>{{ item.label }}</span>
        </a>
      </router-link>

      <a v-else v-ripple :href="item.url" v-bind="props.action">
        <span>{{ item.label }}</span>
      </a>
    </template>
  </Menubar>

  <main class="content">
    <RouterView />
  </main>

  <footer class="footer">
    <span>Build version: {{ BUILD_VERSION.slice(0, 7) }}</span>
  </footer>
</template>

<style scoped>
.active {
  font-weight: 600;
  border-bottom: 2px solid currentColor;
}
</style>


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
footer {
  position: fixed;
  bottom: 0;
  left: 0;
  padding: 1rem;
  width: 100%;
}
</style>
