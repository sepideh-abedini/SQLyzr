import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

const API_CONFIG = '/api/config'
const API_RUN = '/api/run'

export default new Vuex.Store({
    state: {
        config: null,
        loading: false,
        error: null
    },
    mutations: {
        SET_CONFIG(state, config) {
            state.config = config
        },
        SET_LOADING(state, loading) {
            state.loading = loading
        },
        SET_ERROR(state, error) {
            state.error = error
        }
    },
    actions: {
        async fetchConfig({commit}) {
            commit('SET_LOADING', true)
            try {
                const response = await axios.get(API_CONFIG)
                commit('SET_CONFIG', response.data)
                commit('SET_ERROR', null)
            } catch (error) {
                commit('SET_ERROR', `Error loading configuration: ${error.message}`)
            } finally {
                commit('SET_LOADING', false)
            }
        },
        async saveConfig({commit}, config) {
            commit('SET_LOADING', true)
            try {
                await axios.post(API_CONFIG, config)
                commit('SET_CONFIG', config)
                commit('SET_ERROR', null)
                return {success: true, message: 'Configuration saved successfully'}
            } catch (error) {
                commit('SET_ERROR', `Error saving configuration: ${error.message}`)
                console.error('Error saving configuration:', error)
                return {success: false, message: error.message}
            } finally {
                commit('SET_LOADING', false)
            }
        },
        async runSqlyzr({commit}) {
            commit('SET_LOADING', true)
            try {
                const response = await axios.post(API_RUN)
                commit('SET_ERROR', null)
                return {success: true, data: response.data}
            } catch (error) {
                commit('SET_ERROR', `Error running SQLyzr: ${error.message}`)
                console.error('Error running SQLyzr:', error)
                return {success: false, message: error.message}
            } finally {
                commit('SET_LOADING', false)
            }
        },
    },
    getters: {
        isLoading: state => state.loading,
        hasError: state => state.error !== null,
        errorMessage: state => state.error,
        config: state => state.config,
    }
})