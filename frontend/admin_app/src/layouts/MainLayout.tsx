import React from 'react';
import styles from './MainLayout.module.css';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className={styles.container}>
      <aside className={styles.leftPanel}>
        {/* Содержимое левой панели будет здесь */}
      </aside>
      <main className={styles.mainContent}>
        {children}
      </main>
    </div>
  );
};

export default MainLayout; 