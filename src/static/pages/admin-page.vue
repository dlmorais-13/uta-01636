<template>
    <div class="flex-grow-1">
        <HeroBanner text="Administration Page"></HeroBanner>
        <div class="container my-5">
            <div class="row">
                <div class="col-lg-3">
                    <VerticalMenu :links="links"></VerticalMenu>
                </div>
                <div class="col-lg-9">
                    <router-view></router-view>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import HeroBanner from '../components/hero-banner.vue';
import VerticalMenu from '../components/vertical-menu.vue';

const links = [{
    href: '/admin/simulations',
    text: 'Simulations'
}, {
    href: '/admin/data-import',
    text: 'Data Import'
}]
</script>