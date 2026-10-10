import { createRouter, createWebHashHistory } from 'vue-router';

const router = createRouter({
  history: createWebHashHistory(import.meta.env.VITE_BASE_PATH),
  routes: [{
    path: '',
    component: () => import('@/pages/home-page.vue')
  },
  {
    path: '/simulations',
    component: () => import('@/pages/simulations-page.vue')
  },
  {
    path: '/simulations/new',
    component: () => import('@/pages/simulation-create-page.vue')
  },
  {
    name: 'simulations-view',
    path: '/simulations/:id1/:id2?',
    component: () => import('@/pages/simulations-view-page.vue')
  },
    // {
    //   path: '/admin',
    //   component: () => import('./pages/admin-page.vue'),
    //   children: [
    //     {
    //       path: '',
    //       redirect: '/admin/simulations'
    //     },
    //     {
    //       path: 'simulations',
    //       component: () => import('./pages/admin-simulations-page.vue')
    //     },
    //     {
    //       path: 'data-import',
    //       component: () => import('./pages/admin-data-import-page.vue')
    //     },
    //     {
    //       path: 'configurations',
    //       component: () => import('./pages/admin-configurations-page.vue')
    //     }
    //   ]
    // }
  ]
});

export default router;
