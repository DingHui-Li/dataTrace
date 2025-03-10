<template>
  <div class="ai-analyze">
    <div class="title">
      <div style="display: flex;align-items: center;">
        3-分析报告
        <comLoading v-if="loading" />
      </div>
      <el-button :plain="result" :disabled='loading' @click="startAnalyze" type="success">
        {{ result ? "重新分析" : "开始分析" }}
      </el-button>
    </div>
    <div class="error">{{ errorMsg }}</div>
    <div class="label" v-if="reason">
      {{ reason ? "思考完成" : "思考中..." }}
    </div>
    <div class="reason" v-html="reason"></div>
    <div class="result" v-html="result"></div>
    <div class="info" v-if="info.usage?.total_tokens">
      from.{{ info.model }},总Token消耗:{{ info.usage.total_tokens }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'
import comLoading from '../components/pulseLoading.vue'
import { handleUpdate } from '../components/panel.ts'

const reason = ref('')
const result = ref(localStorage.getItem('AIAnalyzeResult') || '')
const loading = ref(false);
const errorMsg = ref('')
const info = ref<any>({})

function startAnalyze() {
  loading.value = true
  errorMsg.value = ''
  reason.value = ''
  result.value = ''
  let reasonStr = ''
  let resultStr = ''
  fetch(`http://127.0.0.1:8348/api/chart/ai`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(async (response) => {
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter(Boolean);

        for (const line of lines) {
          const data: any = JSON.parse(line);
          if (data.error) {
            errorMsg.value = data.error
          }
          if (data.type == 'result') {
            reasonStr += data.analysis
            result.value = await marked(reasonStr)
          } else if (data.type == 'reasoning') {
            resultStr += data.analysis
            reason.value = await marked(resultStr)
          }
          if (data.usage) {
            info.value = data
          }
          if (data.is_final) {
            localStorage.setItem('AIAnalyzeResult', result.value)
          }
        }
        handleUpdate()
      }
    }).finally(() => {
      loading.value = false
    })
}
</script>
<style lang="less" scoped>
.ai-analyze {
  padding: 15px;
  padding-top: 10px;

  .title {
    justify-content: space-between;

    &:deep(.el-button) {

      &.is-plain {
        background-color: transparent;
      }
    }
  }

  .error {
    color: red;
    font-size: 12px;
    margin-bottom: 15px;
  }

  .label {
    font-size: 12px;
    color: #999;
  }

  .reason {
    font-size: 12px;
    color: #999;
    margin-bottom: 15px;
  }

  .result {
    font-size: 15px;
    color: #fff;
  }

  &:deep(hr) {
    border-color: rgba(255, 255, 255, 0.07);
  }

  &:deep(table) {
    width: 100%;

    td {
      text-align: center;
    }
  }

  .info {
    font-size: 12px;
    color: #999;
    text-align: right;
  }
}
</style>