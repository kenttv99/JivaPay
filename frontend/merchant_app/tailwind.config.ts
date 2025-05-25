import type { Config } from 'tailwindcss';
import baseConfig from '../tailwind.config.base';

const config: Config = {
  ...baseConfig,
  // Специфичные настройки для merchant (если нужны)
  theme: {
    ...baseConfig.theme,
    extend: {
      ...baseConfig.theme?.extend,
      // Дополнительные токены только для merchant
    }
  }
};

export default config; 