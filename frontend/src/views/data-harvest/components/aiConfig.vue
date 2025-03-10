<template>
  <div class="config">
    <div class="btn" @click="popup = !popup">
      <slot />
    </div>
    <el-dialog append-to-body v-model="popup">
      <div :class="['config-popup', popup && 'show']">
        <div class="title">
          <span>配置</span>
        </div>
        <el-form label-width="90px">
          <el-form-item label="API密钥">
            <el-input class="input" v-model="deepseek.api_key" placeholder="api key"></el-input>
          </el-form-item>
          <el-form-item label="模型提供方:">
            <el-input class="input" v-model="deepseek.api_base" placeholder="api_base"></el-input>
          </el-form-item>
          <el-form-item label="初步分析">
            <el-form class="model-form">
              <el-form-item label="模型">
                <el-input class="input" v-model="deepseek.model.summary.name" placeholder="模型名称"></el-input>
              </el-form-item>
              <el-form-item label="严谨与想象(Temperature)">
                <el-slider class="slider" v-model="deepseek.model.summary.temperature" :min="0" :max="2" :step="0.1" />
              </el-form-item>
            </el-form>
          </el-form-item>
          <el-form-item label="分析报告">
            <el-form class="model-form">
              <el-form-item label="模型">
                <el-input class="input" v-model="deepseek.model.analysis.name" placeholder="模型名称"></el-input>
              </el-form-item>
              <el-form-item label="严谨与想象(Temperature)">
                <el-slider class="slider" v-model="deepseek.model.analysis.temperature" :min="0" :max="2" :step="0.1" />
              </el-form-item>
            </el-form>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>sahncu
<script setup lang="ts">
import { ref, watch } from 'vue';
import http from '@/utils/http'

const popup = ref(false)
const deepseek = ref(getInitialConfig())

watch(deepseek.value, (v) => {
  localStorage.setItem('deepseekConfig', JSON.stringify(v));
  saveConfig()
}, { immediate: true, deep: true });

function getInitialConfig() {
  const storedConfig = localStorage.getItem('deepseekConfig');
  if (storedConfig) {
    return JSON.parse(storedConfig);
  }
  return {
    "api_key": "",
    "api_base": "https://api.siliconflow.cn/v1",
    "model": {
      "summary": {
        "name": "Pro/deepseek-ai/DeepSeek-V3",
        "temperature": 1.0
      },
      "analysis": {
        "name": "Pro/deepseek-ai/DeepSeek-R1",
        "temperature": 1.0
      }
    }
  }
}

function saveConfig() {
  http.post('/aiconfig', {
    config: deepseek.value
  }).then(res => {
    console.log(res);
  })
}
</script>
<style lang="less" scoped>
.config {
  position: relative;

  .btn {
    cursor: pointer;
  }
}
</style>
<style lang="less">
.config-popup {

  .title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
    padding: 10px;
    padding-top: 0;
    color: #fff;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .close {
      cursor: pointer;
      font-size: 20px;
    }
  }

  .input {
    .el-input__wrapper {
      background-color: rgba(255, 255, 255, 0.07);
      border: none;
      box-shadow: none;
    }

    .el-input__inner {
      color: #fff;
    }
  }

  .model-form {
    margin-top: 30px;
    width: 100%;

    .el-form-item {
      display: block;
      margin-bottom: 15px;

      .el-form-item__label {
        display: block;
        width: 100%;
      }
    }

    .slider {
      .el-slider__runway {
        background-color: rgba(255, 255, 255, 0.1);
      }

      .el-slider__button-wrapper {
        .el-slider__button {
          // background-color: rgba(255, 255, 255, 0.5);
          border: none;
          width: 14px;
          height: 14px;
        }
      }
    }
  }
}
</style>