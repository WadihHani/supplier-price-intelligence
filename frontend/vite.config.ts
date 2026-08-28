import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, process.cwd(), "");

  if (!environment.VITE_API_BASE_URL) {
    throw new Error("VITE_API_BASE_URL must be configured.");
  }

  return {
    plugins: [react()],
  };
});
