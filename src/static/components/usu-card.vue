<template>
    <div class="card border-0">
        <h2 class="h4 card-header text-white" :class="{ 'p-1': !title }">{{ title }}</h2>
        <div class="card-body border">
            <slot></slot>
        </div>
    </div>
</template>

<script setup>
defineProps({
    title: { type: String }
})
</script>

<style scoped>
.card-header {
    margin-top: 0;
    margin-bottom: 0;
    line-height: 1.1;
    font-weight: bold;
    background-color: var(--usu-aggie-blue);
}
</style>
