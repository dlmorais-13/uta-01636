<template>
  <button :disabled="loading">
    <template v-if="loading">
      <UsuSpinner class="d-inline-flex" inherit-color></UsuSpinner>
    </template>
    <template v-else>
      <slot></slot>
    </template>
  </button>
</template>

<script setup>
import UsuSpinner from './usu-spinner.vue';

defineProps({
  text: {
    type: String,
    default: 'Loading'
  },
  loading: {
    type: Boolean,
    default: false
  }
});
</script>
