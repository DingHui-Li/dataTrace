<template>
  <svg :width="props.size" :height="props.size" :fill="color" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,20a9,9,0,1,1,9-9A9,9,0,0,1,12,21Z" />
    <rect class="spinner_d9Sa spinner_qQQY" x="11" y="6" rx="1" width="2" height="7" />
    <rect class="spinner_d9Sa spinner_pote" x="11" y="11" rx="1" width="2" height="9" />
  </svg>
</template>
<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps({
  size: {
    type: Number,
    default: 12
  },
  color: {
    type: String,
    default: "#fff"
  }
})
</script>
<style lang="less" scoped>
.spinner_d9Sa {
  transform-origin: center
}

.spinner_qQQY {
  animation: spinner_ZpfF 9s linear infinite
}

.spinner_pote {
  animation: spinner_ZpfF .75s linear infinite
}

@keyframes spinner_ZpfF {
  100% {
    transform: rotate(360deg)
  }
}
</style>