import type { NextConfig } from "next";
import path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// Получение абсолютного пути к текущему файлу
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Определение путей
const packagesPath = path.resolve(__dirname, '../packages');
const uiKitPath = path.resolve(packagesPath, 'ui-kit/src');

const nextConfig: NextConfig = {
  transpilePackages: ['@jivapay/ui-kit'],
  webpack: (config) => {
    // Настройка разрешения алиасов для webpack
    config.resolve.alias = {
      ...config.resolve.alias,
      '@jivapay/ui-kit': uiKitPath
    };
    return config;
  },
  experimental: {
    // Настройка разрешения алиасов для Turbopack
    turbo: {
      resolveAlias: {
        '@jivapay/ui-kit': uiKitPath
      }
    }
  }
};

export default nextConfig;
