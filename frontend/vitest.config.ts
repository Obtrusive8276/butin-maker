/// <reference types="vitest" />
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: 'happy-dom',
      setupFiles: ['./tests/setup.ts'],
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      exclude: ['node_modules', 'dist'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        include: [
          'src/hooks/**/*.ts',
          'src/utils/**/*.ts',
          'src/stores/**/*.ts',
          'src/components/RenameEditor.tsx',
          'src/components/Finalize.tsx',
        ],
        exclude: [
          'src/**/*.d.ts',
          'src/**/*.test.*',
          'src/**/*.spec.*',
          'src/main.tsx',
          'src/App.tsx',
        ],
      },
    },
  })
);
