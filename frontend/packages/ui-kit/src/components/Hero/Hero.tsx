import React from 'react';
import styles from './Hero.module.css';
import { Button } from '../Button/Button';

interface HeroProps {
  title: string;
  subtitle?: string;
  buttonText?: string;
  buttonLink?: string;
  backgroundVariant?: 'light' | 'dark';
  onButtonClick?: () => void;
  imageUrl?: string;
}

export const Hero: React.FC<HeroProps> = ({
  title,
  subtitle,
  buttonText,
  buttonLink,
  backgroundVariant = 'dark',
  onButtonClick,
  imageUrl,
}) => {
  return (
    <div className={`${styles.hero} ${styles[backgroundVariant]}`}>
      <div className={styles.heroContent}>
        <h1 className={styles.title}>{title}</h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        {buttonText && (
          <div className={styles.buttonWrapper}>
            <Button 
              onClick={onButtonClick}
              variant="primary"
            >
              {buttonText}
            </Button>
          </div>
        )}
      </div>
      {imageUrl && (
        <div className={styles.imageContainer}>
          <img src={imageUrl} alt="Hero" className={styles.image} />
        </div>
      )}
    </div>
  );
}; 