import React from 'react';
import { Card, Button } from '@jivapay/ui-kit';
import styles from './dashboard.module.css';
import '@jivapay/ui-kit/animations/fadeIn.css';

export default function DashboardPage() {
  return (
    <main className={styles.dashboardRoot + ' fadeIn'}>
      <header className={styles.header}>
        <h1>Криптоплатежный шлюз JivaPay</h1>
        <Button size="lg" variant="primary">Начать</Button>
      </header>
      <section className={styles.cardsSection}>
        <Card>
          <h2>Надежный контроль, удобство, безопасность</h2>
          <p>Платформа JivaPay — ваш универсальный инструмент для цифровых платежей.</p>
          <Button variant="secondary">Подробнее</Button>
        </Card>
        <Card variant="glass">
          <h2>Быстрый старт</h2>
          <p>Интеграция за 5 минут, поддержка популярных монет и блокчейнов.</p>
          <Button variant="primary">Документация</Button>
        </Card>
      </section>
    </main>
  );
} 