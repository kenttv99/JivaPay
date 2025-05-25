import type { Config } from 'tailwindcss';
import baseConfig from '../tailwind.config.base';

const config: Config = {
  ...baseConfig,
  // Специфичные настройки для admin (если нужны)
  theme: {
    ...baseConfig.theme,
    extend: {
      ...baseConfig.theme?.extend,
      // Дополнительные токены только для admin
    }
  }
};

export default config; 