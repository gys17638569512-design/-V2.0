import { createRouter, createWebHistory } from 'vue-router'
import { APP_NAME } from '@/constants/app'
import { routerRoutes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routerRoutes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title} - ${APP_NAME}`
})

export default router
