<template>
  <div class="data-harvest">
    <div class="title">
      <div style="display: flex;align-items: center;">
        1-收集各平台发布的内容
        <comConfig>
          <div class="config">
            <el-icon class="icon">
              <Operation />
            </el-icon>
            配置
          </div>
        </comConfig>
      </div>
      <el-button class="database" @click="databasePopup = { show: true, platform: '' }" circle :icon="Box"
        type="primary" :loading="loading">
      </el-button>
    </div>
    <div class="platform-list">
      <div :class="['platform-item', !harvestResult[item.key]?.status && 'disabled']" v-for="item in config">
        <div class="line" :style="`background:${item.color}`"></div>
        <div class="platform-name">
          <div v-if="harvestResult[item.key]?.status == 'pending'" class="status" :style="`background:${item.color}`">
            <comLoading :size="16" />
          </div>
          <div class="status success" v-else-if="harvestResult[item.key]?.status == 'success'">
            <el-icon class="icon">
              <Select />
            </el-icon>
          </div>
          <div class="status fail" v-else>
            <el-icon class="icon">
              <Close />
            </el-icon>
          </div>
          {{ item.platform }}
          <el-button text :loading="harvestResult[item.key]?.status == 'pending'" @click="startHarvest(item.key)"
            :icon="RefreshRight" circle size="small"></el-button>
          <div class="count">
            <transition name="roll">
              <div class="num" :key="harvestResult[item.key]?.total || 0">{{ harvestResult[item.key]?.total || 0 }}
              </div>
            </transition>
          </div>
          <div class="btn" @click="databasePopup = { show: true, platform: item.key }">
            条内容
            <el-icon style="color:#999;font-size: 12px">
              <ArrowRight />
            </el-icon>
          </div>
        </div>
        <div class="progress-box">
          <div :class="['progress-line', harvestResult[item.key]?.status == 'pending' && 'animation']" v-for="i in 150"
            :style="`animation-delay:${i * 10}ms;background:${item.color}`"></div>
          <div class="progress" v-if="harvestResult[item.key]?.status != 'pending'"
            :style="`width:${(1 - harvestResult[item.key]?.total / maxPlatformCount) * 100}%`">
          </div>
        </div>
        <div class="msg" v-if="harvestResult[item.key]?.msg">{{ harvestResult[item.key]?.msg }}</div>
      </div>
    </div>
    <el-dialog class="database-panel" v-model="databasePopup.show" append-to-body fullscreen
      style="height: calc(100vh - 60px);top: 60px;border-radius: 20px 20px 0 0;">
      <comDatabase :platform='databasePopup.platform' />
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import comConfig from '../components/config.vue'
import { Operation, Close, Select, RefreshRight, Box, ArrowRight } from '@element-plus/icons-vue'
import { computed, ref } from 'vue'
import { harvestResult, config, startHarvest } from '@/store/data-harvest'
import comLoading from '../components/loading.vue'
import comDatabase from '../components/database.vue'

const databasePopup = ref({
  show: false,
  platform: ""
})

const loading = computed(() => {
  let t = false
  Object.keys(harvestResult.value).forEach((key) => {
    if (harvestResult.value[key].status == 'pending') {
      t = true
    }
  })
  return t
})

const maxPlatformCount = computed(() => {
  let t = 0;
  Object.keys(harvestResult.value).forEach((key) => {
    t = Math.max(t, harvestResult.value[key]?.total)
  })
  return t
})
</script>
<style lang="less" scoped>
.data-harvest {
  position: relative;
  padding: 15px;

  .title {
    position: relative;
    justify-content: space-between;

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

    .database {
      position: absolute;
      top: -5px;
      right: 0;
    }
  }

  .platform-list {

    .platform-item {
      position: relative;
      padding: 10px;
      // box-shadow: 1px 1px 1px 1px rgba(0, 0, 0, 0.03);
      margin-bottom: 15px;
      border-radius: 10px;
      overflow: hidden;

      &.disabled {
        opacity: 0.5;
        filter: grayscale(1);
      }

      .line {
        position: absolute;
        top: 20px;
        left: 20px;
        width: 1px;
        height: calc(100% - 30px);
      }

      .platform-name {
        display: flex;
        align-items: center;
        font-size: 12px;
        color: #999;
        margin-bottom: 10px;
        user-select: none;

        .status {
          position: relative;
          width: 22px;
          height: 22px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0;
          margin-right: 5px;

          .icon {
            color: #fff;
            font-size: 14px;
          }

          &.success {
            background-color: #4CAF50;
          }

          &.fail {
            background-color: #FF5252;
          }
        }
      }

      .count {
        position: relative;
        flex: 1;
        text-align: right;
        float: right;
        overflow: hidden;
        font-size: 15px;
        padding-left: 28px;
        color: #fff;
        height: 20px;
        font-weight: bold;
        margin-right: 5px;

        .num {
          position: absolute;
          right: 0;
        }
      }

      .btn {
        display: flex;
        align-items: center;
        cursor: pointer;

        &:active {
          opacity: 0.8;
        }
      }

      .progress-box {
        position: relative;
        width: calc(100% - 28px);
        height: 50px;
        display: flex;
        justify-content: space-between;
        margin-left: 28px;
        overflow: hidden;

        .progress-line {
          flex-shrink: 0;
          width: 3px;
          margin-right: 3px;

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

      .msg {
        padding-left: 28px;
        margin-top: 10px;
        font-size: 12px;
        color: #FF5252;
      }
    }
  }
}

@keyframes wave {
  0% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(30%) rotateY(70deg);

  }

  100% {
    transform: translateY(0);
  }
}

.roll-enter-active,
.roll-leave-active {
  transition: all .5s;
  top: 0;
  opacity: 1;
}

.roll-leave-to {
  top: -1em;
  opacity: 0;
}

.roll-enter-active {
  top: 1em;
  opacity: 0;
}

.roll-enter-to {
  top: 0;
  opacity: 1;
}
</style>