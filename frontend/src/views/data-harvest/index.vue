<template>
  <div class="bg">
    <div class="halo-core"></div>
    <div class="cursor-dot"></div>
  </div>
  <div class="container">
    <template v-for="(module, index) in moduleList">
      <comPanel ref="panelEl" :index="index" @click="activeIndex = index" :active="index == activeIndex">
        <component :is="module"></component>
      </comPanel>
    </template>
  </div>
</template>
<script setup lang="ts">
import comPanel from './components/panel.vue'
import comHarvest from './module/harvest.vue'
import comAnalyze from './module/analyze.vue'
import comCharts from './module/charts.vue'
import comAIAnalyze from './module/aiAnalyze.vue'
import { ref, onMounted } from 'vue'

const activeIndex = ref(0)
const panelEl = ref()
const moduleList = [comHarvest, comAnalyze, comAIAnalyze, comCharts]

onMounted(() => {
  const glow: any = document.querySelector('.halo-core') || {}
  const cursorDot: any = document.querySelector('.cursor-dot') || {}
  let centerX = window.innerWidth / 2;
  let centerY = window.innerHeight / 2;
  let targetX = 0, targetY = 0;
  let currentX = 0, currentY = 0;
  let rafId: any = null;

  // 使用节流的鼠标事件处理
  const onMouseMove = (e: any) => {
    targetX = (e.clientX - centerX) * 0.15;
    targetY = (e.clientY - centerY) * 0.15;

    // 直接更新光标点（即时响应）
    cursorDot.style.left = `${e.clientX}px`;
    cursorDot.style.top = `${e.clientY}px`;

    // 使用RAF节流光晕更新
    if (!rafId) {
      rafId = requestAnimationFrame(updateGlow);
    }
  }

  const updateGlow = () => {
    // 使用缓动动画（降低计算量）
    currentX += (targetX - currentX) * 0.15;
    currentY += (targetY - currentY) * 0.15;

    // 批量更新样式
    glow.style.transform = `
                    translate(-50%, -50%)
                    translate(${currentX}px, ${currentY}px)
                `;

    rafId = requestAnimationFrame(updateGlow);
  }

  // 使用passive事件监听器
  document.addEventListener('mousemove', onMouseMove, { passive: true });

  // 视窗尺寸变化处理
  const onResize = () => {
    centerX = window.innerWidth / 2;
    centerY = window.innerHeight / 2;
    cancelAnimationFrame(rafId);
    rafId = null;
  }
  window.addEventListener('resize', onResize);

  // 初始启动
  updateGlow();
})
</script>
<style lang="less" scoped>
.bg {
  position: fixed;
  z-index: 0;
  width: 100vw;
  height: 100vh;
  background-color: #0B0D1C;

  &::after {
    content: "";
    position: absolute;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(20px);
  }

  .halo-core {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100vw;
    height: 100vw;
    border-radius: 50%;
    min-width: 150px;
    min-height: 150px;
    background: radial-gradient(circle at 50% 50%, #C658E890 0%, transparent 70%);
    position: fixed;
    border-radius: 50%;
    transform:
      translate(-50%, -50%) translate(var(--offsetX), var(--offsetY));
    pointer-events: none;
    // transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1);
  }

  /* 添加辅助光标点 */
  .cursor-dot {
    position: fixed;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    mix-blend-mode: difference;
    transition: transform 0.2s;
  }
}

.container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: auto;
  margin: 0 auto;
  max-width: 1080px;
  min-width: 750px;
  padding: 15px;
  box-sizing: border-box;
}
</style>