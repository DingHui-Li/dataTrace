<template>
  <div class="layout">
    <router-view v-slot="{ Component }">
      <transition name="page">
        <keep-alive>
          <component :is="Component" class="page" />
        </keep-alive>
      </transition>
    </router-view>
  </div>
</template>
<script setup lang="ts">
import "./utils/momentCh.js";

</script>
<style lang="less" scoped>
.layout {
  width: 100vw;
  height: 100vh;

  .page {
    position: absolute;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    box-sizing: border-box;
  }
}

.page-enter-active,
.page-leave-active {
  transition: all .3s;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  /* transform: scale(0.9); */
  transform: translateY(20px);
}

.page-enter-to,
.page-leave-from {
  opacity: 1;
  /* transform: scale(1); */
  transform: translateY(0);
}
</style>