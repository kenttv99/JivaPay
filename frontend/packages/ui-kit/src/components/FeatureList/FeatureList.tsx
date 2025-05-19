import React from 'react';
import styles from './FeatureList.module.css';

export interface FeatureItem {
  id: string | number;
  title: string;
  description: string;
  icon?: React.ReactNode;
}

interface FeatureListProps {
  title?: string;
  subtitle?: string;
  features: FeatureItem[];
  variant?: 'grid' | 'list';
  dark?: boolean;
}

export const FeatureList: React.FC<FeatureListProps> = ({
  title,
  subtitle,
  features,
  variant = 'grid',
  dark = false,
}) => {
  return (
    <div className={`${styles.featureList} ${dark ? styles.dark : ''}`}>
      {title && <h2 className={styles.title}>{title}</h2>}
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      
      <div className={`${styles.featuresContainer} ${styles[variant]}`}>
        {features.map((feature) => (
          <div key={feature.id} className={styles.featureItem}>
            {feature.icon && <div className={styles.iconContainer}>{feature.icon}</div>}
            <div className={styles.featureContent}>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDescription}>{feature.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 