<template>
  <div class="database">
    <div class="title">
      <div style="display: flex;align-items: center;">
        数据采集记录：
        <el-button @click='handleRefresh' :loading='loading' :icon="Refresh" circle></el-button>
      </div>
      <!-- <div class="filter">
        <el-config-provider :locale="zhCn">
          <el-date-picker v-model="startTime" type="datetime" placeholder="开始时间" value-format="X" />
        </el-config-provider>
        <el-config-provider :locale="zhCn">
          <el-date-picker v-model="endTime" type="datetime" placeholder="结束时间" value-format="X" />
        </el-config-provider>
        <el-button @click="fetchData" type="success">查询</el-button>
      </div> -->
    </div>
    <el-table class="table" :data="tableData" style="width: 100%" v-loading="loading">
      <el-table-column prop="platform" label="平台名称" width="120">
        <template #default="scope">
          <el-tag class="tag" :color="configMap[scope.row.platform]?.color" style="color:#fff">
            {{ configMap[scope.row.platform]?.platform }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="create_time" label="发布时间" width="180">
        <template #default="scope">
          {{ formatTimestamp(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="链接" width="120" fixed="right">
        <template #default="scope">
          <el-button class="btn" plain :icon="Link" size="small" type="primary" @click="openUrl(scope.row.url)" />
        </template>
      </el-table-column>
    </el-table>
    <div class="">
      <el-pagination class="pagination" v-model:current-page="currentPage" v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next" :total="total"
        @size-change="handleSizeChange" @current-change="handleCurrentChange" />
    </div>
  </div>
</template>

<script setup lang="ts">
// import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { ref, defineProps, onMounted, watch } from 'vue'
import { Link, Refresh } from '@element-plus/icons-vue'
import http from "@/utils/http";
import { configMap } from '@/store/data-harvest'

const props = defineProps({
  platform: {
    type: String,
    default: ''
  }
})

interface TableItem {
  platform: string
  title: string
  content: string
  images: string[]
  create_time: number
  location: string
  url: string
  type: string
}

const tableData = ref<TableItem[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const startTime = ref('')
const endTime = ref('')

watch([() => props.platform], () => {
  fetchData()
}, { immediate: true })

const formatTimestamp = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

const openUrl = (url: string) => {
  if (url) {
    window.open(url, '_blank')
  }
}

function handleRefresh() {
  currentPage.value = 1
  fetchData()
}

function fetchData() {
  loading.value = true
  http.get('/data/query', {
    params: {
      platform: props.platform,
      page: currentPage.value,
      page_size: pageSize.value,
      start_time: startTime.value || undefined,
      end_time: endTime.value || undefined
    }
  }).then((response: any) => {
    tableData.value = response.list
    total.value = response.total || 0
  }).catch(err => {
    console.log(err)
  }).finally(() => {
    loading.value = false
  })
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="less" scoped>
.database {
  padding: 10px;

  .title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
    padding: 10px;
    color: #fff;
    padding-top: 0;

    .filter {
      display: flex;
      gap: 10px;
    }
  }
}
</style>
<style lang="less">
.table {
  background-color: transparent;
  margin-bottom: 30px;

  .el-table__inner-wrapper {
    &::before {
      display: none;
    }
  }

  tr,
  .el-table__cell {
    background-color: transparent !important;
    border-color: rgba(255, 255, 255, 0.07) !important;
    color: #fff;
  }

  .hover-row {
    background-color: transparent !important;
  }

  .el-table__row {
    background-color: transparent;
  }

  .tag {
    border: none;
  }

  .btn {
    background-color: transparent;
    border-radius: 5px;
    ;
  }
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;

  .el-select {
    .el-select__wrapper {
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: none;
      background-color: rgba(0, 0, 0, 0.8);
    }
  }

  .btn-prev,
  .btn-next {
    background-color: transparent !important;
  }

  .el-pager {
    .number {
      background-color: transparent;
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #999;

      &.is-active {
        color: #fff;
      }
    }

    .more {
      background-color: transparent;
    }
  }
}
</style>