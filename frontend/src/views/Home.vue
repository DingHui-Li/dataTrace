<template>
  <div class="smoke-bg" id="smoke-bg"></div>
  <div class="home">
    <h1>DataTrace-数迹</h1>
    <div>
      <h3>数据有迹，人生可循</h3>
    </div>
    <el-button class="btn" type="primary" @click="router.replace('/data-harvest/index')">立即开始</el-button>
    <div class="statement">
      <div>声明</div>
      <ul>
        <li>收集的数据均来自互联网公开数据</li>
        <li>收集到的数据均100%存储于本地设备</li>
        <li>不会将任何数据上传至云端服务器或第三方存储平台</li>
        <li>与第三方AI进行分析的数据将受其隐私政策约束</li>
        <li>建议您在使用前阅读并确认第三方AI的隐私条款</li>
        <li>我们无法控制第三方AI对已接收数据的后续处理</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import SmokeBg from './smokeBg.js'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

onMounted(() => {
  new SmokeBg('smoke-bg')
})

const router = useRouter()
</script>

<style scoped lang="less">
.smoke-bg {
  position: fixed;
  z-index: 0;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #0E0F24;
}

.home {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  user-select: none;
  color: #fff;

  h3 {
    margin: 0;
  }

  .btn {
    margin-top: 100px;
  }

  .statement {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    color: #999;

    div {
      text-align: center;
      font-size: 14px;
    }

    li {
      font-size: 12px;
    }
  }
}
</style>