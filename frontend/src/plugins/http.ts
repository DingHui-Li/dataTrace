import type { App } from 'vue'
import http from '../utils/http'

export default {
  install: (app: App) => {
    // 将http实例挂载到全局属性
    app.config.globalProperties.$http = http
    // 同时也可以通过provide/inject的方式提供给组件使用
    app.provide('http', http)
  }
}

// 扩展ComponentCustomProperties以支持TypeScript类型推断
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $http: typeof http
  }
}