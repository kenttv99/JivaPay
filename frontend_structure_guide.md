# Руководство по структуре фронтенд-проектов JivaPay

Данный документ описывает рекомендуемую структуру для мульти-SPA фронтенд-приложений JivaPay на TypeScript.

## 1. Монорепозиторий и общие пакеты
- Использовать PNPM Workspaces или Turborepo для организации монорепозитория.
- Общие пакеты:
  - `packages/ui-kit` — стилизованные компоненты UI и тема.
  - `packages/types` — автоматически генерируемые TypeScript-типы из OpenAPI.
  - `packages/utils` — утилиты без зависимостей от UI.
  - `packages/hooks` — переиспользуемые React-хуки.
  - `packages/config` — конфигурации ESLint, Prettier, TSConfig.
  - `packages/i18n` — конфигурация и переводы.

## 2. Структура каждого приложения
В каждом приложении (`merchant_app`, `trader_app`, `admin_app`, `support_app`, `teamlead_app`) рекомендуется иметь:

```
/<app>_app/
  ├── src/
  │   ├── assets/         # Статика, изображения, шрифты
  │   ├── components/     # Общие UI-компоненты
  │   ├── layouts/        # Обёртки страниц (хедер, сайдбар)
  │   ├── pages/          # Маршруты или страницы приложения
  │   ├── services/       # HTTP/SSE клиенты для API
  │   ├── hooks/          # Кастомные хуки
  │   ├── store/          # Глобальное состояние (React Query/Redux)
  │   ├── types/          # Локальные типы/интерфейсы
  │   ├── utils/          # Вспомогательные функции
  │   ├── styles/         # Глобальные переменные и темы
  │   └── index.tsx       # Точка входа (ReactDOM.render или аналог)
  ├── public/            # Публичные ресурсы (favicon, robots.txt)
  ├── package.json
  ├── tsconfig.json
  ├── .eslintrc.js
  └── .prettierrc
```

## 3. API-клиент и управление состоянием
- **Сервис API**: в `services/api.ts` или `services/{entity}.ts` на базе Axios или Fetch.
- **Типизация**: импорт типов из `packages/types`.
- **Server State**: использовать React Query или RTK Query для кэширования и фетчинга.
- **SSE/WS**: реализовать в `services/sse.ts` или через кастомный хук `hooks/useSSE.ts`.

## 4. Стили и тема
- **UI-библиотека**: выбрать MUI, Ant Design, Chakra UI или Tailwind CSS.
- **Global styles**: определить переменные и сброс стилей в `styles/globals.css` или `styles/theme.ts`.
- **Component styles**: CSS Modules или CSS-in-JS для изоляции.

## 5. Интернационализация
- Использовать `i18next` или аналог.
- Разместить файлы переводов в `packages/i18n/locales`.
- Подключить провайдер в корневом компоненте.

## 6. Тестирование
- **Unit**: Jest/Vitest для утилит и хуков.
- **Компонентные**: React Testing Library / Storybook.
- **E2E**: Cypress или Playwright для сквозных сценариев.

## 7. CI/CD для фронтенда
- Проверка типов (TS), линтинг (ESLint), форматирование (Prettier).
- Юнит и компонентные тесты.
- Сборка изменённых приложений (Turborepo changed files).
- Деплой на разные поддомены (`merchant.jivapay.com`, etc.). 