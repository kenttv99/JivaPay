import type { Config } from 'tailwindcss';

const baseConfig: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    '../ui-kit/components/**/*.{js,ts,jsx,tsx}',
    '../packages/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      // CSS переменные как Tailwind токены
      colors: {
        // Семантические цвета
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)', 
        accent: 'var(--color-accent)',
        
        // Статусные цвета
        success: 'var(--color-success)',
        'success-light': 'var(--color-success-light)',
        'success-text': 'var(--color-success-text)',
        
        error: 'var(--color-error)',
        'error-light': 'var(--color-error-light)',
        'error-text': 'var(--color-error-text)',
        
        warning: 'var(--color-warning)',
        'warning-light': 'var(--color-warning-light)',
        'warning-text': 'var(--color-warning-text)',
        
        info: 'var(--color-info)',
        'info-light': 'var(--color-info-light)',
        'info-text': 'var(--color-info-text)',
        
        // Нейтральные
        neutral: 'var(--color-neutral)',
        'neutral-light': 'var(--color-neutral-light)',
        'neutral-text': 'var(--color-neutral-text)',
        
        // Поверхности
        background: 'var(--color-bg)',
        surface: 'var(--color-surface)',
        border: 'var(--color-border)'
      },
      
      borderRadius: {
        'sm': 'var(--radius-sm)',
        'md': 'var(--radius-md)', 
        'lg': 'var(--radius-lg)'
      },
      
      boxShadow: {
        'sm': 'var(--shadow-sm)',
        'md': 'var(--shadow-md)'
      },
      
      fontFamily: {
        sans: 'var(--font-family)'
      }
    }
  },
  plugins: []
};

export default baseConfig; 