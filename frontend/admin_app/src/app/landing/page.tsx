"use client";

import React from 'react';
import { Hero, Button, FeatureList, TokenGrid, StepProcess } from '@jivapay/ui-kit';
import styles from './LandingPage.module.css';

// Временные заглушки для иконок
const CardIcon = () => <div className={styles.iconPlaceholder}></div>;

const LandingPage = () => {
  // Список преимуществ
  const features = [
    {
      id: 1,
      title: 'Мгновенные платежи',
      description: 'Принимайте платежи в криптовалюте с минимальной комиссией и мгновенной обработкой',
      icon: <CardIcon />,
    },
    {
      id: 2,
      title: 'Безопасность транзакций',
      description: 'Все транзакции защищены современными технологиями шифрования и блокчейн',
      icon: <CardIcon />,
    },
    {
      id: 3,
      title: 'API для разработчиков',
      description: 'Интегрируйте криптоплатежи в любой проект с помощью нашего простого API',
      icon: <CardIcon />,
    },
    {
      id: 4,
      title: 'Мультивалютная поддержка',
      description: 'Принимайте платежи в Bitcoin, Ethereum, USDT и других популярных криптовалютах',
      icon: <CardIcon />,
    },
    {
      id: 5,
      title: 'Автоматическая конвертация',
      description: 'Мгновенная конвертация криптовалюты в фиатные деньги по выгодному курсу',
      icon: <CardIcon />,
    },
    {
      id: 6,
      title: 'Подробная аналитика',
      description: 'Получайте детальные отчеты о транзакциях и финансовых операциях',
      icon: <CardIcon />,
    },
  ];

  // Список поддерживаемых криптовалют
  const tokens = [
    { id: 1, name: 'Bitcoin', symbol: 'BTC', icon: '/icons/btc.svg', backgroundColor: '#F7931A' },
    { id: 2, name: 'Ethereum', symbol: 'ETH', icon: '/icons/eth.svg', backgroundColor: '#627EEA' },
    { id: 3, name: 'USDT', symbol: 'USDT', icon: '/icons/usdt.svg', backgroundColor: '#26A17B' },
    { id: 4, name: 'Binance Coin', symbol: 'BNB', icon: '/icons/bnb.svg', backgroundColor: '#F3BA2F' },
    { id: 5, name: 'Litecoin', symbol: 'LTC', icon: '/icons/ltc.svg', backgroundColor: '#BFBBBB' },
    { id: 6, name: 'Ripple', symbol: 'XRP', icon: '/icons/xrp.svg', backgroundColor: '#23292F' },
  ];

  // Шаги интеграции
  const steps = [
    {
      id: 1,
      title: 'Регистрация',
      description: 'Создайте бесплатный аккаунт на платформе Cryptomus',
    },
    {
      id: 2,
      title: 'Настройка',
      description: 'Подключите способы оплаты и настройте параметры',
    },
    {
      id: 3,
      title: 'Интеграция',
      description: 'Добавьте платежную форму на ваш сайт или приложение',
    },
    {
      id: 4,
      title: 'Готово!',
      description: 'Принимайте платежи и отслеживайте транзакции в личном кабинете',
    },
  ];

  // Партнеры и интеграции
  const partners = [
    { id: 1, name: 'WordPress', logo: '/logos/wordpress.svg' },
    { id: 2, name: 'Shopify', logo: '/logos/shopify.svg' },
    { id: 3, name: 'Magento', logo: '/logos/magento.svg' },
    { id: 4, name: 'Bitrix24', logo: '/logos/bitrix24.svg' },
    { id: 5, name: 'WooCommerce', logo: '/logos/woocommerce.svg' },
  ];

  return (
    <div className={styles.landingPage}>
      {/* Верхняя навигация */}
      <header className={styles.header}>
        <div className={styles.headerContainer}>
          <div className={styles.logo}>Cryptomus</div>
          <nav className={styles.navigation}>
            <a href="#" className={styles.navItem}>Возможности</a>
            <a href="#" className={styles.navItem}>Интеграции</a>
            <a href="#" className={styles.navItem}>Тарифы</a>
            <a href="#" className={styles.navItem}>Помощь</a>
          </nav>
          <div className={styles.actions}>
            <Button>Вход</Button>
            <Button>Регистрация</Button>
          </div>
        </div>
      </header>

      {/* Hero секция */}
      <section className={styles.heroSection}>
        <Hero 
          title="Криптоплатежный шлюз Cryptomus"
          subtitle="Современное решение для приема криптовалютных платежей на вашем сайте или приложении"
          buttonText="Подключить"
          backgroundVariant="dark"
          imageUrl="/images/crypto-cards.webp"
        />
      </section>

      {/* Секция "Мы упрощаем подключение" */}
      <section className={styles.simplifySection}>
        <div className={styles.sectionContainer}>
          <h2 className={styles.sectionTitle}>Мы упрощаем вам подключение и обработку платежей</h2>
          
          <div className={styles.paymentDemo}>
            <div className={styles.paymentForm}>
              <div className={styles.paymentHeader}>
                <div className={styles.cryptoAmount}>10.00 TRX</div>
                <div className={styles.cryptoNetwork}>TRON (TRC-20)</div>
              </div>
              
              <div className={styles.paymentDetails}>
                <div className={styles.paymentField}>
                  <span className={styles.fieldLabel}>Сумма к оплате:</span>
                  <span className={styles.fieldValue}>10.00 TRX</span>
                </div>
                
                <div className={styles.paymentField}>
                  <span className={styles.fieldLabel}>Сеть:</span>
                  <span className={styles.fieldValue}>TRON (TRC-20)</span>
                </div>
                
                <div className={styles.paymentField}>
                  <span className={styles.fieldLabel}>Адрес:</span>
                  <span className={styles.fieldValue}>TXe4..8jH2</span>
                  <span className={styles.copyButton}>[коп.]</span>
                </div>

                <div className={styles.paymentAction}>
                  <Button>Оплата с помощью Cryptomus</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Секция с возможностями */}
      <section className={styles.featuresSection}>
        <FeatureList 
          title="Классные функции криптоплатежного шлюза Cryptomus"
          subtitle="Все необходимое для простого и безопасного приема криптовалютных платежей"
          features={features}
          dark={true}
        />
      </section>

      {/* Секция с поддерживаемыми токенами */}
      <section className={styles.tokensSection}>
        <TokenGrid 
          title="Поддерживаемые монеты и блокчейны"
          tokens={tokens}
          showNames={true}
        />
      </section>

      {/* Секция с шагами интеграции */}
      <section className={styles.integrationSection}>
        <StepProcess 
          title="Как принимать криптовалютные платежи с Cryptomus"
          steps={steps}
          layout="horizontal"
          dark={true}
        />
      </section>

      {/* Секция со статистикой */}
      <section className={styles.statsSection}>
        <div className={styles.sectionContainer}>
          <h2 className={styles.sectionTitle}>Почему выбирают Cryptomus</h2>
          <div className={styles.statsGrid}>
            <div className={styles.statItem}>
              <div className={styles.statValue}>100+</div>
              <div className={styles.statLabel}>Поддерживаемых криптовалют</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>1000+</div>
              <div className={styles.statLabel}>Довольных клиентов</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>99.9%</div>
              <div className={styles.statLabel}>Время бесперебойной работы</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>24/7</div>
              <div className={styles.statLabel}>Техническая поддержка</div>
            </div>
          </div>
        </div>
      </section>

      {/* Секция с партнерами */}
      <section className={styles.partnersSection}>
        <div className={styles.sectionContainer}>
          <h2 className={styles.sectionTitle}>Интеграции и партнеры</h2>
          <div className={styles.partnersGrid}>
            {partners.map(partner => (
              <div key={partner.id} className={styles.partnerItem}>
                <img src={partner.logo} alt={partner.name} className={styles.partnerLogo} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Секция с CTA */}
      <section className={styles.ctaSection}>
        <div className={styles.ctaContainer}>
          <h2 className={styles.ctaTitle}>Начните принимать платежи в крипто прямо сейчас!</h2>
          <Button>Регистрация</Button>
        </div>
      </section>

      {/* Футер */}
      <footer className={styles.footer}>
        <div className={styles.footerContainer}>
          <div className={styles.footerSection}>
            <div className={styles.footerLogo}>Cryptomus</div>
            <p className={styles.footerDescription}>
              Современная платформа для приема криптовалютных платежей
            </p>
          </div>
          <div className={styles.footerLinks}>
            <div className={styles.footerLinksColumn}>
              <h3 className={styles.footerLinksTitle}>Продукт</h3>
              <a href="#" className={styles.footerLink}>Возможности</a>
              <a href="#" className={styles.footerLink}>Тарифы</a>
              <a href="#" className={styles.footerLink}>API</a>
            </div>
            <div className={styles.footerLinksColumn}>
              <h3 className={styles.footerLinksTitle}>Поддержка</h3>
              <a href="#" className={styles.footerLink}>Документация</a>
              <a href="#" className={styles.footerLink}>Центр поддержки</a>
              <a href="#" className={styles.footerLink}>Контакты</a>
            </div>
            <div className={styles.footerLinksColumn}>
              <h3 className={styles.footerLinksTitle}>Компания</h3>
              <a href="#" className={styles.footerLink}>О нас</a>
              <a href="#" className={styles.footerLink}>Блог</a>
              <a href="#" className={styles.footerLink}>Карьера</a>
            </div>
          </div>
        </div>
        <div className={styles.footerBottom}>
          <div className={styles.footerCopyright}>
            © {new Date().getFullYear()} Cryptomus. Все права защищены.
          </div>
          <div className={styles.footerSocials}>
            <a href="#" className={styles.socialIcon}>T</a>
            <a href="#" className={styles.socialIcon}>F</a>
            <a href="#" className={styles.socialIcon}>I</a>
            <a href="#" className={styles.socialIcon}>L</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 