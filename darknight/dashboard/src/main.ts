import { createApp } from 'vue'
import { createHead } from '@unhead/vue/client'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import '@/assets/css/globals.css'
import '@/styles/index.scss'

import App from '@/App.vue'
import router from '@/router'
import '@/permission'
import { applyLocaleFromQuery, i18n, setLocale } from '@/plugins/vueI18n'

const app = createApp(App)
const head = createHead()

app.use(createPinia())
app.use(head)
app.use(router)
app.use(i18n)
app.use(VueQueryPlugin)

applyLocaleFromQuery(router)
setLocale(i18n.global.locale.value)

app.mount('#app')
