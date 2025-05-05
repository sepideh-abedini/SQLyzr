import './assets/main.css'
import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Aura from '@primeuix/themes/aura';
import {definePreset} from '@primeuix/themes';
import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css'
import 'vuefinder/dist/style.css'
// @ts-ignore
import VueFinder from 'vuefinder/dist/vuefinder'


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

app.mount('#app')
