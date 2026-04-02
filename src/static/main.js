import * as Vue from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js';
import { loadModule } from 'https://cdn.jsdelivr.net/npm/vue3-sfc-loader@0.9.5/dist/vue3-sfc-loader.esm.js'

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
}

const app = Vue.createApp(Vue.defineAsyncComponent(() => loadModule('./components/main.vue', options)));
app.config.compilerOptions.isCustomElement = (tag) => tag.startsWith('arcgis-')
app.mount('#app');