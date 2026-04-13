<template>
    <div class="form-group">
        <label class="d-block">{{ label }}</label>
        <slot></slot>
        <small class="form-text text-muted" v-if="helpText">{{ helpText }}</small>
    </div>
</template>

<script setup>
defineProps({
    label: { type: String, required: true },
    helpText: { type: String, required: false }
});
</script>
