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
        // JivaPay Color Palette
        'shady-lady': 'var(--color-shady-lady)',
        'ghost': 'var(--color-ghost)',
        'rich-black': 'var(--color-rich-black)',
        'tory-blue': 'var(--color-tory-blue)',
        
        // Семантические цвета (наша система)
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
        muted: 'var(--color-muted)',

        // shadcn/ui цвета (HSL формат)
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        sidebar: {
          DEFAULT: 'hsl(var(--sidebar-background))',
          foreground: 'hsl(var(--sidebar-foreground))',
          primary: 'hsl(var(--sidebar-primary))',
          'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
          accent: 'hsl(var(--sidebar-accent))',
          'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
          border: 'hsl(var(--sidebar-border))',
          ring: 'hsl(var(--sidebar-ring))',
        },
        
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
        
        // Поверхности для совместимости
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        surface: 'hsl(var(--surface))'
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