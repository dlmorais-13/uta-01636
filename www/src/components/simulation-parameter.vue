<template>
    <span class="simulation-parameter">
        <span class="simulation-parameter-name" :class="{ 'simulation-parameter-calculated': calculated }">{{ getName()
            }}</span>
        <span class="simulation-parameter-value">{{ getValue() }}</span>
    </span>
</template>

<script setup lang="ts">
import type { SimulationFilters, SimulationParameters } from '@/types';

const props = withDefaults(defineProps<{
    parameter: SimulationFilters | SimulationParameters,
    calculated?: boolean
}>(), {
    calculated: false
});

function getName() {
    switch (props.parameter.type) {
        case 'target':
            return `${props.parameter.name}: ${props.parameter.value}`;

        default:
            return props.parameter.name;
    }
}

function getValue() {
    switch (props.parameter.type) {
        case 'target':
            return `${Number(props.parameter.target! * 100).toFixed(3)}%`;

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

.simulation-parameter>span {
    padding: 0 5px;
}

.simulation-parameter-name {
    font-weight: bold;
    background-color: var(--usu-aggie-blue);
    color: var(--usu-blue-light);
    text-transform: capitalize;
    border-radius: 5px 0px 0px 5px;
}

.simulation-parameter-calculated {
    background-color: var(--usu-blue-light);
    color: var(--usu-black);
}

.simulation-parameter-value {
    font-style: italic;
    color: var(--usu-aggie-blue);
    border-radius: 0px 5px 5px 0px;
}
</style>
