import { API_BASE_URL } from './config'

export default {
  methods: {
    async call_api(endpoint: string, options = {}, notify: boolean = false) {
      const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`

      console.log(`Calling API: ${url}`)
      const defaultOptions = {
        headers: {
          'Content-Type': 'application/json',
        },
      }

      const fetchOptions = { ...defaultOptions, ...options }

      const response = await fetch(url, fetchOptions)

      if (response.ok) {
        if (notify) {
          //@ts-expect-error $toast is added to vue instance
          this.$toast.add({
            severity: 'success',
            summary: 'Success',
            detail: `API Request was successful ${response.status}, ${response.statusText}`,
            life: 5000,
          })
        }
      } else {
        const msg = await response.text()
        //@ts-expect-error $toast is added to vue instance
        this.$toast.add({
          severity: 'error',
          summary: 'Error',
          detail: `Request failed with status code ${response.status}, ${msg}`,
          life: 5000,
        })
        return null
      }

      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }

      return await response.text()
    },
  },
}
