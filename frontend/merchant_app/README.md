# JivaPay Merchant App

This is the Merchant application of the JivaPay platform, built with Next.js and TypeScript. It provides merchants with an interface to:

- Manage stores, API keys, and callback settings
- Track incoming orders and order history
- Monitor and configure balances and limits

## Documentation

- [Project Overview](../../README.md)
- [Frontend Architecture Plan](../../frontend/README_ARCHITECTURE_PLAN.md)
- [Frontend Structure Guide](../../frontend_structure_guide.md)

## Getting Started

Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

Start the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open http://localhost:3000 in your browser to view the application.

## Build for Production

```bash
npm run build
npm run start
```

## Contributing

Please adhere to coding standards defined in `eslint.config.mjs` and `tsconfig.json`. For testing, see the frontend testing guidelines in the architecture plan.
