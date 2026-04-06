<template>
    <nav class="accordion" id="site-header-nav" aria-label="Quick Menu">
        <Transition name="accordion">
            <div id="header-quicklinks" class="collapse show overflow-hidden" data-parent="#site-header-nav"
                v-if="quickLinksOpen">
                <div class="container">
                    <div class="row">
                        <div class="col d-flex justify-content-end py-3">
                            <ul class="list-inline small m-0 mr-3" role="navigation">
                                <li class="list-inline-item">
                                    <a href="https://www.usu.edu/apply/">Apply</a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="https://www.usu.edu/visit/">Visit</a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="https://www.usu.edu/advancement/">Give</a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="https://www.usu.edu/calendar/">Calendar</a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="https://www.usu.edu/azindex/">A-Z Index</a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="https://directory.usu.edu/">Directory</a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="https://library.usu.edu/">Libraries</a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>

        <nav class="navbar navbar-expand py-0 my-0 pl-lg-3">
            <div class="container">
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a id="quick-links" class="nav-link small px-1 px-lg-2" role="button" href="#"
                                data-toggle="collapse" data-target="#header-quicklinks"
                                aria-controls="header-quicklinks" :aria-expanded="quickLinksOpen"
                                @click="quickLinksOpen = !quickLinksOpen" :class="quickLinksOpen ? 'active' : ''">
                                <svg class="svg-inline--fa fa-list mr-2" aria-hidden="true" focusable="false"
                                    data-prefix="fas" data-icon="list" role="img" xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 512 512" data-fa-i2svg="">
                                    <path fill="currentColor"
                                        d="M40 48C26.7 48 16 58.7 16 72l0 48c0 13.3 10.7 24 24 24l48 0c13.3 0 24-10.7 24-24l0-48c0-13.3-10.7-24-24-24L40 48zM192 64c-17.7 0-32 14.3-32 32s14.3 32 32 32l288 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L192 64zm0 160c-17.7 0-32 14.3-32 32s14.3 32 32 32l288 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-288 0zm0 160c-17.7 0-32 14.3-32 32s14.3 32 32 32l288 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-288 0zM16 232l0 48c0 13.3 10.7 24 24 24l48 0c13.3 0 24-10.7 24-24l0-48c0-13.3-10.7-24-24-24l-48 0c-13.3 0-24 10.7-24 24zM40 368c-13.3 0-24 10.7-24 24l0 48c0 13.3 10.7 24 24 24l48 0c13.3 0 24-10.7 24-24l0-48c0-13.3-10.7-24-24-24l-48 0z">
                                    </path>
                                </svg><!-- <i class="fas fa-list mr-2"></i> -->QUICK LINKS
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link small px-1 px-lg-2" href="https://my.usu.edu/">
                                <svg class="svg-inline--fa fa-user mr-2" aria-hidden="true" focusable="false"
                                    data-prefix="fas" data-icon="user" role="img" xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 448 512" data-fa-i2svg="">
                                    <path fill="currentColor"
                                        d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3C0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7C448 383.8 368.2 304 269.7 304l-91.4 0z">
                                    </path>
                                </svg><!-- <i class="fas fa-user mr-2"></i> -->MyUSU
                            </a>
                        </li>
                        <li class="nav-item">
                            <a id="header-search-btn" class="nav-link small px-1 px-lg-2 search-btn"
                                @click="onOpenSearchOverlay()" role="button" aria-haspopup="dialog">
                                <svg class="svg-inline--fa fa-search mr-2" aria-hidden="true" focusable="false"
                                    data-prefix="fas" data-icon="search" role="img" xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 512 512" data-fa-i2svg="">
                                    <path fill="currentColor"
                                        d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z">
                                    </path>
                                </svg><!-- <i class="fas fa-search mr-2"></i> -->SEARCH
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    </nav>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
    onOpenSearchOverlay: {
        type: Function,
        default: () => { console.warning('usu-quick-links function to open search overlay not defined.') }
    }
});

const quickLinksOpen = ref(false);
</script>

<style scoped>
.navbar-collapse {
    justify-content: flex-end;
}

#site-header-nav>.collapse a,
#site-header-nav>.collapsing a {
    color: var(--usu-gray);
}

#site-header-nav>.collapse,
#site-header-nav>.collapsing {
    background-color: var(--usu-blue-darker);
    color: var(--usu-white);
}

.navbar-collapse a {
    background-color: transparent;
    color: var(--usu-white);
}

.navbar-collapse a.active {
    background-color: var(--usu-blue-darker);
    color: var(--usu-white);
}

.navbar-collapse a:hover {
    background-color: var(--usu-bright-light);
}

.svg-inline--fa {
    display: var(--fa-display, inline-block);
    height: 1em;
    overflow: visible;
    vertical-align: -.125em;
}
</style>
