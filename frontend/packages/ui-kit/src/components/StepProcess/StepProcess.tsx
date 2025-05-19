import React from 'react';
import styles from './StepProcess.module.css';

export interface Step {
  id: string | number;
  title: string;
  description: string;
  image?: string;
  icon?: React.ReactNode;
}

interface StepProcessProps {
  title?: string;
  subtitle?: string;
  steps: Step[];
  dark?: boolean;
  layout?: 'horizontal' | 'vertical';
}

export const StepProcess: React.FC<StepProcessProps> = ({
  title,
  subtitle,
  steps,
  dark = false,
  layout = 'vertical',
}) => {
  return (
    <div className={`${styles.stepProcess} ${dark ? styles.dark : ''}`}>
      {title && <h2 className={styles.title}>{title}</h2>}
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      
      <div className={`${styles.stepsContainer} ${styles[layout]}`}>
        {steps.map((step, index) => (
          <div key={step.id} className={styles.stepItem}>
            <div className={styles.stepNumber}>{index + 1}</div>
            
            <div className={styles.stepContent}>
              <h3 className={styles.stepTitle}>{step.title}</h3>
              <p className={styles.stepDescription}>{step.description}</p>
            </div>
            
            {step.image && (
              <div className={styles.stepImageContainer}>
                <img src={step.image} alt={step.title} className={styles.stepImage} />
              </div>
            )}
            
            {step.icon && (
              <div className={styles.stepIconContainer}>
                {step.icon}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}; 