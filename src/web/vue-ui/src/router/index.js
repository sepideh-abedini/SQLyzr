import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [{
    path: '/config',
    name: 'Configuration',
    component: () => import(/* webpackChunkName: "config" */ '../views/Configuration.vue')
}]

const router = new VueRouter({
    mode: 'history', base: process.env.BASE_URL, routes
})

export default router