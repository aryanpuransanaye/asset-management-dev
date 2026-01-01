import { createApp } from 'vue'
import App from './App.vue'
import router from './router'  // <-- اضافه شد
import { createPinia } from 'pinia'

import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css';


const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
.use(router)   // <-- استفاده از روتر
.mount('#app')

app.directive('can', {
  mounted(el, binding) {
    const auth = useAuthStore()
    const permission = binding.value
    
    if (!auth.hasPermission(permission)) {
      el.style.display = 'none' // یا کلاً از DOM حذفش کن: el.remove()
    }
  }
})