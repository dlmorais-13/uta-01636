import * as Vue from 'vue';
import { loadModule } from 'vue-sfc-loader'
import { createRouter, createWebHistory } from 'vue-router'

const options = {
    moduleCache: {
        vue: Vue,
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
    }
};

const router = createRouter({
  history: createWebHistory(),
  routes: [{
      path: '',
      component: Vue.defineAsyncComponent(() => loadModule('./pages/home-page.vue', options))
    },
    {
      path: '/map',
      component: Vue.defineAsyncComponent(() => loadModule('./pages/map-page.vue', options))
    },
    {
      path: '/admin',
      component: Vue.defineAsyncComponent(() => loadModule('./pages/admin-page.vue', options))
    },
  ]
});

const app = Vue.createApp(Vue.defineAsyncComponent(() => loadModule('./components/main.vue', options)));
app.config.compilerOptions.isCustomElement = (tag) => tag.startsWith('arcgis-');
app.use(router);
app.mount('#app');