import * as Vue from 'vue';
import * as VueRouter from 'vue-router';
import { loadModule } from 'vue-sfc-loader';

const options = {
    moduleCache: {
        vue: Vue,
        'vue-router': VueRouter
    },

    async getFile(url) {
        const res = await fetch(url);
        if (!res.ok) throw Object.assign(new Error(res.statusText + ' ' + url), { res });
        return { getContentData: asBinary => asBinary ? res.arrayBuffer() : res.text() }
    },

    addStyle(textContent) {
        const style = Object.assign(document.createElement('style'), { textContent });
        const ref = document.head.getElementsByTagName('style')[0] || null;
        document.head.insertBefore(style, ref);
    },

    log(type, ...args) {
        console.log(type, ...args);
    },

    isCustomElement(tag) { 
      return tag.startsWith('arcgis-');
    }
};

const router = VueRouter.createRouter({
  history: VueRouter.createWebHistory(),
  routes: [{
      path: '',
      component: () => loadModule('/pages/home-page.vue', options)
    },
    {
      path: '/parcels',
      component: () => loadModule('/pages/parcels-page.vue', options)
    },
    {
      path: '/studies',
      component: () => loadModule('/pages/studies-page.vue', options)
    },
    {
      path: '/studies/new',
      component: () => loadModule('/pages/study-create-page.vue', options)
    },
    {
      name: 'studies-view',
      path: '/studies/:id1/:id2?',
      component: () => loadModule('/pages/studies-view-page.vue', options)
    },
    {
      path: '/admin',
      component: () => loadModule('/pages/admin-page.vue', options),
      children: [
        {
          path: '',
          redirect: '/admin/simulations'
        },
        {
          path: 'simulations',
          component: () => loadModule('/pages/admin-simulations-page.vue', options)
        },
        {
          path: 'data-import',
          component: () => loadModule('/pages/admin-data-import-page.vue', options)
        },
        {
          path: 'configurations',
          component: () => loadModule('/pages/admin-configurations-page.vue', options)
        }
      ]
    },
  ]
});

const [esriConfig, Error] = await $arcgis.import([
  "@arcgis/core/config",
  "@arcgis/core/core/Error"
]);

// Intercept all API responses globally
esriConfig.request.interceptors.push({
  after: function(response) {
    // Check if the server payload contains an internal ArcGIS error
    if (response.data && response.data.error) {
      const apiError = response.data.error;
      
      // Standardize and explicitly throw the Esri SDK exception
      throw new Error("api:request-failed", apiError.message, {
        code: apiError.code,
        details: apiError.details
      });
    }
  }
});

const app = Vue.createApp(Vue.defineAsyncComponent(() => loadModule('/components/main.vue', options)));
// app.config.compilerOptions.isCustomElement = (tag) => tag.startsWith('arcgis-');
app.use(router);
app.mount('#app');