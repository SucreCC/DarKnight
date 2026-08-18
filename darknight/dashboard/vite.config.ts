import react from "@vitejs/plugin-react";
import { defineConfig, splitVendorChunkPlugin } from "vite";
import svgr from "vite-plugin-svgr";
import { visualizer } from "rollup-plugin-visualizer";
import tsconfigPaths from "vite-tsconfig-paths";

const apiProxyTarget =
  process.env.VITE_API_PROXY_TARGET || "http://127.0.0.1:33100";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    tsconfigPaths(),
    react({
      include: "**/*.tsx",
    }),
    svgr(),
    visualizer(),
    splitVendorChunkPlugin(),
  ],
  server: {
    port: 3000,
    proxy: {
      "/api/v1": {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
});
