import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import dotenv from 'dotenv';



const envFile = process.env.NODE_ENV === 'production' ? '.env.prod' : '.env';
dotenv.config({ path: path.resolve(__dirname, envFile) });

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
