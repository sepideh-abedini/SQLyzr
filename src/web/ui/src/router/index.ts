import { createRouter, createWebHistory } from 'vue-router'
import ConfigView from '@/views/ConfigView.vue'
import LogsView from '@/views/LogsView.vue'
import ScoresView from '@/views/ScoresView.vue'
import ChartsView from '@/views/ChartsView.vue'
import FilesView from '@/views/FilesView.vue'
import DataView from '@/views/DataView.vue'
import TrsView from '@/views/TrsView.vue'
import StatusView from '@/views/StatusView.vue'
import EnvView from '@/views/EnvView.vue'
import DatabaseView from '@/views/DatabaseView.vue'
import AugView from '@/views/AugView.vue'
import CategoriesView from '@/views/CategoriesView.vue'
import MetricsView from '@/views/MetricsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'about',
      component: ConfigView,
    },
    {
      path: '/logs',
      name: 'logs',
      component: LogsView,
    },
    {
      path: '/scores',
      name: 'scores',
      component: ScoresView,
    },
    {
      path: '/charts',
      name: 'charts',
      component: AugView,
    },
    {
      path: '/files',
      name: 'files',
      component: FilesView,
    },
    {
      path: '/data',
      name: 'data',
      component: DataView,
    },
    {
      path: '/status',
      name: 'status',
      component: StatusView,
    },
    {
      path: '/errors',
      name: 'errors',
      component: TrsView,
    },
    {
      path: '/env',
      name: 'env',
      component: EnvView,
    },
    {
      path: '/database',
      name: 'database',
      component: DatabaseView,
    },
    {
      path: '/aug',
      name: 'aug',
      component: AugView,
    },
    {
      path: '/categories',
      name: 'categories',
      component: CategoriesView,
    },
    {
      path: '/metrics',
      name: 'metrics',
      component: MetricsView,
    },
  ],
})

export default router
