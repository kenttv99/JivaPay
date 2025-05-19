import React from 'react';
import styles from './TokenGrid.module.css';

export interface Token {
  id: string | number;
  name: string;
  symbol: string;
  icon: string;
  backgroundColor?: string;
}

interface TokenGridProps {
  title?: string;
  subtitle?: string;
  tokens: Token[];
  showNames?: boolean;
  dark?: boolean;
}

export const TokenGrid: React.FC<TokenGridProps> = ({
  title,
  subtitle,
  tokens,
  showNames = false,
  dark = false,
}) => {
  return (
    <div className={`${styles.tokenGrid} ${dark ? styles.dark : ''}`}>
      {title && <h2 className={styles.title}>{title}</h2>}
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      
      <div className={styles.tokensContainer}>
        {tokens.map((token) => (
          <div 
            key={token.id} 
            className={styles.tokenItem}
            style={{ backgroundColor: token.backgroundColor }}
          >
            <img src={token.icon} alt={token.name} className={styles.tokenIcon} />
            {showNames && <span className={styles.tokenName}>{token.name}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}; 