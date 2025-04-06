// src/router/routes.js
import MainLayout from 'src/layouts/MainLayout.vue'
import DashboardPage from 'pages/DashboardPage.vue'
import CamerasPage from 'src/pages/CamerasPage.vue'
import EventsPage from 'src/pages/EventsPage.vue'
import EventDetailPage from 'src/pages/EventDetailPage.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: DashboardPage },
      { path: 'cameras', component: CamerasPage },
      { path: 'events', component: EventsPage },
      { path: 'events/:eventId', component: EventDetailPage }
    ]
  }
]

export default routes
