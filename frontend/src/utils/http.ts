import axios, {
  AxiosInstance,
  InternalAxiosRequestConfig,
  AxiosResponse,
} from "axios";

// 创建axios实例
const instance: AxiosInstance = axios.create({
  baseURL: "http://127.0.0.1:8348/api", // 基础URL，与vite配置中的代理配置相对应
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 设置5分钟超时，因为爬虫操作可能需要较长时间
  timeoutErrorMessage: "请求超时，请稍后重试",
});

// 请求拦截器
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem("token");
    if (token) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    // 直接返回响应数据
    return response.data;
  },
  (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem("token");
          // 这里可以使用router进行页面跳转
          break;
        case 403:
          // 权限不足
          console.error("没有权限访问该资源");
          break;
        case 404:
          console.error("请求的资源不存在");
          break;
        case 500:
          console.error("服务器错误");
          break;
        default:
          console.error(`未知错误：${error.response.status}`);
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error("网络错误，请检查您的网络连接");
    } else {
      // 请求配置出错
      console.error("请求配置错误：", error.message);
    }
    return Promise.reject(error);
  }
);

// 导出实例
export default instance;
