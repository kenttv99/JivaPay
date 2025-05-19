import React from 'react';
import styles from './PaymentCard.module.css';

// Временные заглушки для иконок. В реальном проекте это будут SVG или компоненты иконок из ui/
const CopyIcon = () => <span style={{ marginLeft: '8px', cursor: 'pointer' }}>[коп.]</span>;
const InfoIcon = () => <span style={{ marginLeft: '4px', cursor: 'pointer' }}>[?]</span>;
const WebIcon = () => <span style={{ marginLeft: '8px', cursor: 'pointer' }}>[веб]</span>;
const ChevronDownIcon = () => <span style={{ marginLeft: 'auto', cursor: 'pointer' }}>[v]</span>;
const CryptomusLogo = () => (
  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
    <div style={{ width: '40px', height: '40px', backgroundColor: '#ccc', marginRight: 'var(--spacing-sm)', borderRadius: 'var(--border-radius-md)' }} />
    <span style={{ fontSize: 'var(--font-size-lg)', fontWeight: 'var(--font-weight-semibold)' }}>cryptomus</span>
  </div>
);

const PaymentCard = () => {
  return (
    <div className={styles.paymentCard}>
      <div className={styles.cardHeader}>
        <span>Счет в фиатной валюте</span>
        <span className={styles.activeTab}>Счет в криптовалюте</span>
      </div>
      
      <div className={styles.cardContent}>
        <CryptomusLogo />
        <div className={styles.balanceInfo}>
          <span className={styles.balanceAmount}>10.00 TRX</span>
          <CopyIcon />
        </div>
        <div className={styles.networkInfo}>TRON (TRC-20)</div>

        <div className={styles.paymentChip}>
            <div style={{ display: 'flex', alignItems: 'center'}}>
                <div style={{ width: '16px', height: '16px', backgroundColor: '#ccc', borderRadius: '4px', marginRight: '4px' }} /> {/* Placeholder for chip icon */}
                <span>+ 0.001</span>
                <InfoIcon />
            </div>
            <WebIcon />
        </div>

        <div className={styles.expiryInfo}>
          <div className={styles.timerCircle}> {/* Placeholder for timer graphic */}
            <svg width="40" height="40" viewBox="0 0 40 40" style={{ transform: 'rotate(-90deg)'}}>
                <circle cx="20" cy="20" r="18" stroke="var(--color-border)" strokeWidth="3" fill="none" />
                <circle cx="20" cy="20" r="18" stroke="var(--color-success)" strokeWidth="3" fill="none" strokeDasharray="113.097" strokeDashoffset="28.274" /> {/* 25% filled */}
            </svg>
          </div>
          <div>
            <div>Время истечения</div>
            <div className={styles.timerText}>02:34:54</div>
          </div>
        </div>

        <div className={styles.networkSelector}>
          <span>TRON (TRC-20)</span>
          <ChevronDownIcon />
        </div>

        <button className={styles.payButton}>
          <div style={{ width: '20px', height: '20px', backgroundColor: '#fff', borderRadius: '4px', marginRight: '8px' }} /> {/* Placeholder for button icon */}
          Оплата с помощью Cryptomus
        </button>
      </div>
    </div>
  );
};

export default PaymentCard; 