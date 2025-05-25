import type { Config } from 'tailwindcss';
import baseConfig from '../tailwind.config.base';

const config: Config = {
  ...baseConfig,
  // Специфичные настройки для teamlead (если нужны)
  theme: {
    ...baseConfig.theme,
    extend: {
      ...baseConfig.theme?.extend,
      // Дополнительные токены только для teamlead
    }
  }
};

export default config; 