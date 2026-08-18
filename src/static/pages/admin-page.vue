<template>
    <div class="flex-grow-1">
        <HeroBanner text="Administration"></HeroBanner>
        <div class="container my-5">
            <div class="row" v-if="portalCredentials">
                <div class="col-lg-3">
                    <VerticalMenu :links="links">
                        <template v-slot:header>
                            <span class="d-block">Welcome, {{ portalUser.sourceJSON.firstName }}!</span>
                            <small>({{ portalUser.username }})</small>

                            <button class="btn btn-secondary btn-block mt-2">Logout</button>
                        </template>
                    </VerticalMenu>
                </div>
                <div class="col-lg-9">
                    <router-view v-slot="{ Component }">
                        <Suspense :timeout="0">
                            <component :is="Component" :credentials="portalCredentials" />

                            <template #fallback>
                                <div class="align-items-center d-flex justify-content-center mt-5 text-bright">
                                    <strong>Loading...</strong>
                                    <div class="spinner-border ml-3" role="status" aria-hidden="true"></div>
                                </div>
                            </template>
                        </Suspense>
                    </router-view>
                </div>
            </div>

            <div v-else>
                <p>
                    You need to login to access the administration functionalities.
                </p>

                <button class="btn btn-bright-light" @click="triggerLogin()" v-if="!portalUser">
                    Login with ArgGIS Online
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import HeroBanner from '../components/hero-banner.vue';
import VerticalMenu from '../components/vertical-menu.vue';

const links = [{
    href: '/admin/simulations',
    text: 'Simulations'
}, {
    href: '/admin/configurations',
    text: 'Configurations'
}, {
    href: '/admin/jobs',
    text: 'Jobs'
}];

const [Portal, OAuthInfo, identityManager] = await $arcgis.import([
    "@arcgis/core/portal/Portal.js",
    "@arcgis/core/identity/OAuthInfo.js",
    "@arcgis/core/identity/IdentityManager.js",
]);

const info = new OAuthInfo({
    appId: "YS4qIS7FPw7CW9FD",
    popup: false, // the default
});
identityManager.registerOAuthInfos([info]);

const portalUser = ref(null);
const portalCredentials = ref(null);
async function handleSignedIn() {
    const portal = new Portal();
    portal.load().then(() => {
        portalUser.value = portal.user;
        portalCredentials.value = portal.credential;
        // console.log(portalCredentials.value);
    });
}

function triggerLogin() {
    identityManager.getCredential(info.portalUrl + "/sharing");
}

await identityManager
    .checkSignInStatus(info.portalUrl + "/sharing")
    .then(() => handleSignedIn())
    .catch(() => { })
</script>