import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  base: './',
  css: {
    postcss: {
      plugins: []
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        app: resolve(process.cwd(), 'app.html'),
        main: resolve(process.cwd(), 'index.html'),
        comparison: resolve(process.cwd(), 'comparison.html'),
        liveLocation: resolve(process.cwd(), 'live-location.html'),
        planetaryMap: resolve(process.cwd(), 'planetary-map.html'),
        missionDashboard: resolve(process.cwd(), 'mission-control-dashboard.html')
      }
    }
  }
});
