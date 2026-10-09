<template>
    <div class="hero-banner jumbotron-fluid jumbotron-full color-blend jumbotron-content-bottom-left">
        <div class="jumbotron-content xl h-bold container text-white">
            <h1 class="text-white mb-0">{{ text }}</h1>

            <div v-if="$slots.actions" style="right: 3em; bottom: -2em; gap: .5em;" class="d-flex position-absolute">
                <slot name="actions"></slot>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
defineProps({
    text: {
        type: String,
        default: ''
    }
});
</script>

<style scoped>
.hero-banner {
    height: 200px;
    /* #2472b5 */
    background: linear-gradient(90deg, var(--usu-info) 0%, var(--usu-blue) 100%);
    min-height: 97.5px;
}

.jumbotron-full {
    width: 100%;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: flex-end;
}

.jumbotron-narrow {
    max-width: 1920px;
    margin-left: auto;
    margin-right: auto;
}

.jumbotron-content {
    text-align: left;
    z-index: 3;
    position: relative;
    margin-bottom: 1.5rem;
    font-size: 1.167rem;
    font-family: "Roboto Condensed", Helvetica, Arial, sans-serif;
}
</style>