import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    optimizeDeps: {
        include: ['lodash', 'ml-distance', 'minisearch', 'react-infinite-scroller'],
        exclude: [
            '@tailwindcss/forms',
            '@tailwindcss/typography',
            '@tensorflow/tfjs',
            '@trivago/prettier-plugin-sort-imports',
            '@types/node',
            '@types/react',
            '@types/react-dom',
            '@vitejs/plugin-react',
            'autoprefixer',
            'cross-env',
            'csv-parse',
            'daisyui',
            'eslint',
            'eslint-config-prettier',
            'eslint-plugin-comment-length',
            'eslint-plugin-import',
            'eslint-plugin-jsdoc',
            'eslint-plugin-node',
            'eslint-plugin-prettier',
            'eslint-plugin-react',
            'eslint-plugin-react-hooks',
            'eslint-plugin-react-refresh',
            'eslint-plugin-sort-exports',
            'eslint-plugin-tailwindcss',
            'ml-kmeans',
            'papaparse',
            'postcss',
            'prettier',
            'prettier-plugin-jsdoc',
            'prettier-plugin-tailwindcss',
            'simple-statistics',
            'tailwind-scrollbar',
            'tailwindcss',
            'vite-plugin-top-level-await',
        ],
    },
    build: {
        sourcemap: false,
    },
});
