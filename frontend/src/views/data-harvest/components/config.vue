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
        <el-form label-width="60px">
          <el-form-item v-for="item in config" :label="item.platform" :key="item.key">
            <el-input class="input" v-model="item.baseUrl" placeholder="用户主页地址"></el-input>
            <el-input v-if="item.needCookie" class="input" v-model="item.cookie" placeholder="填写cookie，某些网站需要登录才能浏览"
              style="margin-top: 5px;"></el-input>
          </el-form-item>
          <el-form-item label='清空'>
            <el-popconfirm width='250' title="此操作将删除所有收集到的数据和初步分析的数据." confirm-button-text='删除' cancel-button-text='取消'
              confirm-button-type='danger' @confirm="clearData">
              <template #reference>
                <el-button type='danger'>清空数据</el-button>
              </template>
            </el-popconfirm>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>sahncu
<script setup lang="ts">
import { ref } from 'vue';
import { config } from '@/store/data-harvest';
import http from '@/utils/http'
import { ElMessage } from 'element-plus'
import { getProgress } from '@/store/data-analyze'
import { getDatabaseStat } from '@/store/data-harvest'

const popup = ref(false)

function clearData() {
  http.get('/data/clear').then((res: any) => {
    if (res?.result) {
      ElMessage({
        message: '清空数据成功',
        type: 'success',
      })
      getDatabaseStat()
      getProgress()
    }
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
}
</style>