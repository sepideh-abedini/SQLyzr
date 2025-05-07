import './assets/main.css'
import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import Aura from '@primeuix/themes/aura';
import {definePreset} from '@primeuix/themes';
import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css'
import 'vuefinder/dist/style.css'
// @ts-ignore
import VueFinder from 'vuefinder/dist/vuefinder'
import api_mixin from './api_mixin';


const app = createApp(App)
const MyPreset = definePreset(Aura, {});
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.lightmode'
    }
  }
});
app.use(VueFinder);
app.use(ToastService);
app.use(ConfirmationService);
app.config.errorHandler = function (err, vm, info) {
  console.error("Error Handler:", err);
  vm?.$toast.add({
    severity: 'error',
    summary: 'Error',
    detail: `Error fetching configuration: ${err}`,
    life: 5000
  });
}
app.mixin(api_mixin);

app.mount('#app')
