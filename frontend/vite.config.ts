import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@": resolve("./src"),
    },
  },
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:8348",
        changeOrigin: true,
      },
    },
    hmr: true,
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
