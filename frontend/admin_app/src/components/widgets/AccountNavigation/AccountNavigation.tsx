import React from 'react';
import styles from './AccountNavigation.module.css';

const AccountNavigation = () => {
  return (
    <div className={styles.leftNavPanel}>
      <div className={styles.navHeader}>
        <h2>Счета</h2>
        <span>—</span>
      </div>
      <div className={styles.navSection}>
        <div className={styles.navSectionHeader}>
          <h3>Выбор электронной коммерции</h3>
        </div>
        <p className={styles.navSectionDescription}>
          Этот способ подходит для оплаты товаров или услуг. Вы можете установить цену в фиатной валюте, чтобы плательщик выбрал криптовалюту и заплатил соответствующую сумму, или сразу указать предпочтительную криптовалюту, а адрес криптовалюты будет сгенерирован после выбора сети.
        </p>
      </div>
      <div className={styles.navItem}>
        <span>Регулярные платежи</span>
        <span>+</span>
      </div>
      <div className={styles.navItem}>
        <span>Хост</span>
        <span>+</span>
      </div>
      <div className={styles.navItem}>
        <span>Платежные ссылки</span>
        <span>+</span>
      </div>
    </div>
  );
};

export default AccountNavigation; 