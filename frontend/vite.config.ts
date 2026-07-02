import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

declare const process: {
  env: Record<string, string | undefined>;
};

export default defineConfig({
  base: process.env.GITHUB_PAGES === "true"
    ? (() => {
        const repoName = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "";
        return repoName.endsWith(".github.io") ? "/" : `/${repoName}/`;
      })()
    : "/",
  plugins: [react()],
  server: {
    port: 5173,
    watch: {
      ignored: ["**/*.xlsx", "**/*.xls", "**/~$*"],
    },
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
