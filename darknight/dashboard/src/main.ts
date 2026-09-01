import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import '@/assets/css/globals.css'
import '@/styles/index.scss'

import App from '@/App.vue'
import router from '@/router'
import '@/permission'
import { i18n, setLocale } from '@/plugins/vueI18n'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(VueQueryPlugin)

setLocale(i18n.global.locale.value)

app.mount('#app')
