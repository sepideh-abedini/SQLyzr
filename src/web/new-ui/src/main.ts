import './assets/main.css'
import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Aura from '@primeuix/themes/aura';
import {definePreset} from '@primeuix/themes';

const app = createApp(App)
const MyPreset = definePreset(Aura, {});
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: MyPreset
  }
});
app.use(ToastService);

app.mount('#app')
