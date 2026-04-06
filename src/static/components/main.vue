<template>
    <div>
        <div class="d-flex flex-column justify-content-between min-vh-100">
            <UsuHeader></UsuHeader>

            <main class="flex-grow-1 align-items-stretch d-flex">
                <RouterView></RouterView>
            </main>
        </div>

        <footer id="site-footer">
            <UsuFatFooter></UsuFatFooter>
            <UsuGlobalFooter></UsuGlobalFooter>

            <a href="#" id="back-to-top" style="display: block;"><svg class="svg-inline--fa fa-chevron-up"
                    aria-hidden="true" focusable="false" data-prefix="fas" data-icon="chevron-up" role="img"
                    xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" data-fa-i2svg="">
                    <path fill="currentColor"
                        d="M233.4 105.4c12.5-12.5 32.8-12.5 45.3 0l192 192c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L256 173.3 86.6 342.6c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3l192-192z">
                    </path>
                </svg>
                <span class="sr-only">Back to top of the page</span>
            </a>
        </footer>
    </div>
</template>

<script setup>
import UsuHeader from './usu-header.vue';
import UsuFatFooter from './usu-fat-footer.vue';
import UsuGlobalFooter from './usu-global-footer.vue';
</script>

<style scoped>
#back-to-top {
    position: fixed;
    display: none;
    background: rgba(0, 0, 0, 0.5);
    color: var(--usu-white);
    padding: 6px 12px 9px 12px;
    font-size: 16px;
    border-radius: 2px;
    right: 15px;
    bottom: 15px;
    z-index: 6;
}
</style>