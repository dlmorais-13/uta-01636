<template>
    <span class="study-parameter">
        <span class="study-parameter-name">{{ getFormattedName() }}</span>
        <span class="study-parameter-value">{{ value }}</span>
    </span>
</template>

<script setup>
const props = defineProps({
    name: {
        type: String,
        required: true
    },
    value: {
        type: [String, Number],
        required: true
    }
});

function getFormattedName() {
    return props.name;
}
</script>

<style scoped>
.study-parameter {
    display: inline-flex;
    align-items: center;
    background-color: var(--usu-white);
    border-radius: 5px;
    border: 1px solid var(--usu-aggie-blue);
}

.study-parameter > span {
    padding: 0 5px;
}

.study-parameter-name {
    font-weight: bold;
    background-color: var(--usu-aggie-blue);
    color: var(--usu-blue-light);
    text-transform: capitalize;
}

.study-parameter-value {
    font-style: italic;
    color: var(--usu-aggie-blue);
}
</style>
