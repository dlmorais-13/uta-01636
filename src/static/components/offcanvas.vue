<template>
    <div class="offcanvas p-3" :class="{
        'offcanvas-right': position === 'right',
        'offcanvas-left': position === 'left',
    }" v-if="open">
        <div class="offcanvas-header">
            <div class="flex-grow-1">
                <h2>
                    {{title}}
                </h2>
            </div>
            <button type="button" class="btn-close" aria-label="Close" v-if="onClose" @click="onClose()"></button>
        </div>

        <div>
            <slot></slot>
        </div>
    </div>
</template>

<script setup>
defineProps({
    open: {
        type: Boolean,
        default: false
    },

    title: {
        type: String
    },

    position: {
        type: String,
        default: 'right'
    },

    onClose: {
        type: Function,
        default: null
    }
})
</script>

<style scoped>
.offcanvas {
    width: 400px;
    overflow-y: scroll;
    background-color: var(--usu-white);
    position: absolute;
    top: 0;
    bottom: 0;
}

.offcanvas-right {
    right: 0;
    border-left: 3px solid var(--usu-blue-darker);
}

.offcanvas-left {
    left: 0;
    border-right: 3px solid var(--usu-blue-darker);
}

.offcanvas-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.offcanvas-header .btn-close {
    border: none;
    font-size: 1.5rem;
    background-color: transparent;
}

.offcanvas-header .btn-close::before {
    content: '✕';
    color: var(--usu-gray-dark);
}
</style>
