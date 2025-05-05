import {createRouter, createWebHistory} from 'vue-router'
import ConfigView from "@/views/ConfigView.vue";
import LogsView from "@/views/LogsView.vue";
import ScoresView from "@/views/ScoresView.vue";
import ChartsView from "@/views/ChartsView.vue";


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
      component: ChartsView,
    },
  ],
})

export default router
