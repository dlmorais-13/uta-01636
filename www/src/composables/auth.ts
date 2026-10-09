import { ref, onMounted } from 'vue';
import OAuthInfo from '@arcgis/core/identity/OAuthInfo';
import IdentityManager from '@arcgis/core/identity/IdentityManager';
import Portal from '@arcgis/core/portal/Portal';
import type PortalUser from '@arcgis/core/portal/PortalUser';

const info = new OAuthInfo({ appId: import.meta.env.VITE_AGOL_CLIENT_ID, popup: false });
IdentityManager.registerOAuthInfos([info]);

export function useAuth() {
  const user = ref<PortalUser | null | undefined>(null);
  const credentials = ref(null);
  const authChecked = ref<boolean>(false);

  async function login() {
    IdentityManager.getCredential(info.portalUrl + "/sharing");
  }

  async function logout() {
    IdentityManager.destroyCredentials();
    user.value = null;
    credentials.value = null;
  }

  async function handleSignedIn() {
    const portal = new Portal();
    portal.load().then(() => {
      user.value = portal.user;
      console.debug("useAuth.user", user.value);
      // credentials.value = portal.credential;
      console.log('portal', portal);
      console.debug("useAuth.credentials", credentials.value);
      authChecked.value = true;
    });
  }

  async function waitForAuth() {
    function check(resolve: () => void) {
      if (authChecked.value) resolve();
      setTimeout(check, 100);
    }
    return new Promise<void>(resolve => check(resolve));
  }

  IdentityManager
    .checkSignInStatus(info.portalUrl + "/sharing")
    .then(() => handleSignedIn())
    .catch(() => { });

  return { user, credentials, login, logout, waitForAuth }
}
