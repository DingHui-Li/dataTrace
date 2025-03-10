<template>
  <div class="analyze">
    <div class="title">
      2-初步分析
      <comAIConfig>
        <div class="config">
          <el-icon class="icon">
            <Operation />
          </el-icon>
          配置
        </div>
      </comAIConfig>
      <el-button class="btn"
        v-if="hasData && analyzeResult.status != 'processing' && analyzeResult.progress?.percentage != 100"
        type="primary" @click="startAnalyze">开始分析</el-button>
    </div>
    <div class="error" v-if="analyzeResult.status == 'error'" style="margin-top: 20px;">
      {{ analyzeResult.message }}
    </div>
    <div class="error tip" v-else style="margin-top: 20px;">
      {{ analyzeResult.message }}
    </div>
    <div class="error tip" v-if='analyzeResult.model'>
      from.{{ analyzeResult.model }},此次分析总Token消耗:{{ analyzeResult.total_tokens }}
    </div>
    <div class="progress-num">{{ analyzeResult.progress?.percentage || 0 }}%</div>
    <div class="progress-box">
      <div :class="['progress-line ', analyzeResult.status == 'processing' && 'animation']" v-for="i in 100"
        :style="`animation-delay:${i * 5}ms;background:${progressColors[i]}`"></div>
      <div class="progress" :style="`width:${100 - (analyzeResult.progress?.percentage || 0)}%`"></div>
    </div>
    <comCalendarChart />
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { Operation } from '@element-plus/icons-vue'
import { analyzeResult, startAnalyze } from '@/store/data-analyze'
import { harvestResult } from '@/store/data-harvest'
import comCalendarChart from '../components/calendarChart.vue'
import comAIConfig from '../components/aiConfig.vue'


const progressColors = generateGradientColors()

const hasData = computed(() => {
  let t = false
  Object.keys(harvestResult.value).forEach((key) => {
    if (harvestResult.value[key].current) {
      t = true
    }
  })
  return t
})

// 计算两个颜色之间的渐变颜色数组
function generateGradientColors(startHex = '#FE2B29', endHex = '#FB6126', steps = 100) {
  const startRgb = hexToRgb(startHex);
  const endRgb = hexToRgb(endHex);
  const colors: any = [];

  for (let i = 0; i < steps; i++) {
    const ratio = i / (steps - 1);
    const r = Math.round(startRgb[0] + (endRgb[0] - startRgb[0]) * ratio);
    const g = Math.round(startRgb[1] + (endRgb[1] - startRgb[1]) * ratio);
    const b = Math.round(startRgb[2] + (endRgb[2] - startRgb[2]) * ratio);
    colors.push(`rgb(${r}, ${g}, ${b})`);
  }

  return colors;
}

// 将十六进制颜色转换为 RGB 数组
function hexToRgb(hex = '') {
  hex = hex.replace(/^#/, '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return [r, g, b];
}

</script>
<style lang="less" scoped>
.analyze {
  position: relative;
  padding: 15px;

  .title {
    .config {
      font-weight: normal;
      color: var(--el-color-primary);
      cursor: pointer;
      display: flex;
      align-items: center;
      margin-left: 5px;

      .icon {
        margin-right: 5px;
      }
    }

    .btn {
      margin-left: 10px;
      border-radius: 30px;
    }
  }

  .subtitle {
    font-size: 14px;
    color: #999;
    margin-top: 5px;
  }

  .progress-num {
    position: absolute;
    top: 12px;
    right: 15px;
    background: linear-gradient(to right, #FE2B29, #FB6126);
    border-radius: 15px;
    padding: 5px 10px;
    font-size: 15px;
    color: #fff;
  }

  .progress-box {
    position: relative;
    width: 100%;
    height: 50px;
    display: flex;
    justify-content: space-between;
    overflow: hidden;
    margin: 30px 0;

    .progress-line {
      flex-shrink: 0;
      width: 5px;
      margin: 0 1px;
      border-radius: 10px;

      &.animation {
        animation: wave 1.5s infinite;
        transform-origin: bottom center;
      }
    }

    .progress {
      position: absolute;
      right: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.85);
      transition: all .3s;
    }
  }

  .error {
    font-size: 12px;
    color: red;
    margin-top: 5px;

    &.tip {
      color: #999;
    }
  }

  .btn {}
}

@keyframes wave {
  0% {
    opacity: 0.3;
  }

  50% {
    transform: translateY(30%);
  }

  100% {
    opacity: 1;
  }
}
</style>