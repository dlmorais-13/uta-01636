<template>
    <span class="simulation-parameter">
        <span class="simulation-parameter-name">{{ getName() }}</span>
        <span class="simulation-parameter-value">{{ getValue() }}</span>
    </span>
</template>

<script setup>
const props = defineProps({
    parameter: {
        type: Object,
        required: true
    }
});

function getName() {
    switch(props.parameter.type) {
        case 'target':
            return `${props.parameter.name}: ${props.parameter.value}`;
            
        default:
            return props.parameter.name;
    }
}

function getValue() {
    switch(props.parameter.type) {
        case 'target':
            return `${Number(props.parameter.target * 100).toFixed(3)}%`;
            
        default:
            return props.parameter.value;
    }
}
</script>

<style scoped>
.simulation-parameter {
    display: inline-flex;
    align-items: center;
    background-color: var(--usu-white);
    border-radius: 5px;
    border: 1px solid var(--usu-aggie-blue);
}

.simulation-parameter > span {
    padding: 0 5px;
}

.simulation-parameter-name {
    font-weight: bold;
    background-color: var(--usu-aggie-blue);
    color: var(--usu-blue-light);
    text-transform: capitalize;
}

.simulation-parameter-value {
    font-style: italic;
    color: var(--usu-aggie-blue);
}
</style>
