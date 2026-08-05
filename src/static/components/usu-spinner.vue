<template>
  <div class="d-flex gap-half text-blue small justify-around spinner-increase">
    <div class="spinner-grow spinner-grow-sm fast-spin" role="status">
      <span class="sr-only">Loading...</span>
    </div>
    <div class="spinner-grow spinner-grow-sm normal-spin" role="status">
      <span class="sr-only">Loading...</span>
    </div>
    <div class="spinner-grow spinner-grow-sm slow-spin" role="status">
      <span class="sr-only">Loading...</span>
    </div>
  </div>
</template>

<style scoped>
.spinner-increase :nth-child(1) { animation-delay: 0ms; }
.spinner-increase :nth-child(2) { animation-delay: 37ms; }
.spinner-increase :nth-child(3) { animation-delay: 75ms; }
</style>
