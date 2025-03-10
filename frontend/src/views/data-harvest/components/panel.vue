<template>
  <div :class="['module-panel', !active && 'shrink']" :style="style">
    <div class="content" ref="contentRef">
      <slot />
    </div>
  </div>
</template>
<script setup lang="ts">
import { defineProps, watch, computed, onMounted, ref } from 'vue'
import { update } from './panel.ts'

const props = defineProps({
  index: {
    type: Number,
    default: 0
  },
  active: {
    type: Boolean,
    default: false
  }
})
const contentRef = ref()
const panelHeight = ref(0)

onMounted(() => {
  panelHeight.value = contentRef.value?.clientHeight + 50
})

const style = computed(() => {
  return `
  z-index:${props.index + 1};
max-height:${panelHeight.value ? (panelHeight.value + 'px') : 'none'};
  `
})

watch(update, v => {
  if (v) {
    panelHeight.value = contentRef.value?.clientHeight + 50
  }
})

</script>
<style lang="less" scoped>
.module-panel {
  position: relative;
  background-color: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  border-radius: 10px;
  margin-bottom: 15px;
  transition: all .3s ease-in-out;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.4), transparent);
  }

  &.shrink {
    max-height: 55px !important;
    cursor: pointer;

    &::before {
      display: none;
    }

    &:hover {
      opacity: 0.4;
    }
  }

  &:deep(.title) {
    display: flex;
    align-items: center;
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #fff;
  }
}
</style>