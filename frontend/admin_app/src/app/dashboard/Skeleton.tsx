import React from 'react';
import styles from './dashboard.module.css';

export default function DashboardSkeleton() {
  return (
    <div className={styles.skeletonRoot}>
      <div className={styles.skeletonHeader} />
      <div className={styles.skeletonCard} />
      <div className={styles.skeletonCard} />
    </div>
  );
} 