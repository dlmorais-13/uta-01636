<template>
    <nav id="sub-menu" class="navbar navbar-expand-lg my-4 px-0 pb-lg-4 pt-lg-0">
        <div class="sub-menu-brand-wrapper pb-1 py-lg-3">
            <a class="sub-menu-brand px-3" href="#">Menu</a>
            <button class="navbar-toggler collapsed custom-toggler" data-toggle="collapse"
                data-target="#sub-menu-navbar" aria-controls="navbarTogglerDemo03" aria-expanded="false"
                aria-label="Toggle navigation"><span class="sr-only">Menu</span>
                <span class="navbar-toggler-icon">&nbsp;</span>
                <svg class="svg-inline--fa fa-times close mx-2 my-1" aria-hidden="true" focusable="false"
                    data-prefix="fas" data-icon="times" role="img" xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 384 512" data-fa-i2svg="">
                    <path fill="currentColor"
                        d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z">
                    </path>
                </svg>
            </button>
        </div>
        <div id="sub-menu-navbar" class="collapse navbar-collapse flex-column">
            <ul class="navbar-nav p-3">
                <li class="nav-item" v-for="l in links">
                    <router-link class="nav-link" :to="l.href">{{ l.text }}</router-link>
                </li>
            </ul>
        </div>
    </nav>
</template>

<script setup>
defineProps({
    links: {
        type: Array,
        required: true,
        default: () => []
    }
});
</script>