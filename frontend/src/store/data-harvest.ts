import { computed, ref, watch } from "vue";
import http from "@/utils/http";

const STORAGE_KEY = "data_harvest_config";

// 从localStorage获取初始配置
const getInitialConfig = (): Array<DataSourceConfig> => {
  const storedConfig = localStorage.getItem(STORAGE_KEY);
  if (storedConfig) {
    return JSON.parse(storedConfig);
  }
  return [
    {
      platform: "微博",
      key: "weibo",
      color: "#ff8200",
      baseUrl: "",
      cookie: "",
      needCookie: true,
    },
    {
      platform: "知乎",
      color: "#0066CC",
      key: "zhihu",
      baseUrl: "",
      cookie: "",
    },
    {
      platform: "贴吧",
      color: "#4CA3FF",
      key: "tieba",
      baseUrl: "",
      cookie: "",
    },
    // {
    //   platform: "豆瓣",
    //   color: "#3caa3c",
    //   key: "douban",
    //   baseUrl: "",
    //   cookie: "",
    // },
  ];
};

export const config = ref<Array<DataSourceConfig>>(getInitialConfig());
export const harvestResult = ref<any>({});
export const configMap = computed(() => {
  let t: any = {};
  config.value.forEach((v) => {
    t[v.key] = v;
  });
  return t;
});

watch(config.value, (v) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(v));
});
getDatabaseStat();
export function getDatabaseStat() {
  http.get("/data/stats").then((res: any) => {
    try {
      Object.keys(res).forEach((platform) => {
        harvestResult.value[platform] = {
          current: res[platform],
          total: Number(res[platform]),
          status: "success",
        };
      });
    } catch {}
  });
}

// 开始数据爬取
export const startHarvest = async (singlePlatform: string) => {
  // 循环调用每个平台的爬取接口
  for (const platform of config.value) {
    const baseUrl = platform.baseUrl;
    if (harvestResult.value[platform.key]?.status == "pending") continue;
    if (baseUrl && (!singlePlatform || singlePlatform == platform.key)) {
      harvestResult.value[platform.key] = {
        list: [],
        status: "pending",
      };
      fetch(`http://127.0.0.1:8348/api/harvest/${platform.key}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ base_url: baseUrl, cookie: platform.cookie }),
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
              const data = JSON.parse(line);
              console.log(data);

              if (data.status === "error") {
                harvestResult.value[platform.key] = {
                  status: "fail",
                  current: data.current || 0,
                  total: data.total || 0,
                  msg: data.message || `${platform.platform}数据采集失败`,
                };
              } else if (data.status === "processing") {
                harvestResult.value[platform.key] = {
                  ...harvestResult.value[platform.key],
                  current: data.current,
                  total: data.total,
                  status: "pending",
                };
              } else if (data.status === "complete") {
                harvestResult.value[platform.key] = {
                  current: data.current,
                  total: data.total,
                  status: data.success ? "success" : "fail",
                };
                getDatabaseStat();
              }
            }
          }
        })
        .catch((error) => {
          harvestResult.value[platform.key] = {
            status: "fail",
            list: [],
            msg: error?.message || `${platform.platform}数据采集失败`,
          };
        });
    }
  }
};

interface DataSourceConfig {
  baseUrl: string;
  platform: string;
  key: string;
  color: string;
  cookie: string;
  needCookie?: boolean;
}
