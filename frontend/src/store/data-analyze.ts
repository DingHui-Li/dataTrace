import { computed, ref, watch } from "vue";
import http from "@/utils/http";
import { isMemoryCleared } from './data-harvest'

export const analyzeResult = ref<any>({});
export const loading = ref(false);
export const list = ref<Array<any>>([]);

// 监听内存清空状态，清空分析数据
watch(isMemoryCleared, (cleared) => {
  if (cleared) {
    list.value = [];
    analyzeResult.value = {};
  }
});

watch(
  analyzeResult,
  () => {
    if (analyzeResult.value.progress?.percentage == 100) {
      getDataList();
    }
  },
  { deep: true }
);

getProgress();
getDataList();
export function getProgress() {
  list.value = [];
  http.get("/analyze/checkprogress").then((res) => {
    analyzeResult.value.progress = res || {};
  });
}

export function startAnalyze() {
  // 开始分析时，重置清空状态
  isMemoryCleared.value = false;
  analyzeResult.value = {
    status: "processing",
    message: `数据分析中...`,
    progress: {
      percentage: 0,
    },
  };
  fetch(`http://127.0.0.1:8348/api/analyze`, {
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
          if (data.data) {
            list.value.push(data.data);
          }
          analyzeResult.value = data;
        }
      }
    })
    .catch((error) => {
      analyzeResult.value = {
        status: "error",
        list: [],
        message: error?.message || `数据分析失败`,
      };
    });
}

function getDataList() {
  // 如果内存已清空，不加载数据
  if (isMemoryCleared.value) {
    list.value = [];
    return;
  }
  loading.value = true;
  http
    .get("chart/alldata")
    .then((res: any) => {
      list.value = res || [];
    })
    .finally(() => {
      loading.value = false;
    });
}
