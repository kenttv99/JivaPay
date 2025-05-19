"use client";

import React from 'react';
import MainLayout from '../../layouts/MainLayout';
import { Button } from '@jivapay/ui-kit';
import styles from './DashboardPage.module.css';

const DashboardPage = () => {
  return (
    <MainLayout>
      <div className={styles.dashboardHeader}>
        <h1 className={styles.pageTitle}>Дашборд JivaPay</h1>
        <p className={styles.pageSubtitle}>Обзор платформы, статистика и активность</p>
      </div>

      <div className={styles.metricsSection}>
        <div className={styles.metricsCards}>
          <div className={styles.metricCard}>
            <div className={styles.metricHeader}>Общий баланс USDT</div>
            <div className={styles.metricValue}>1,234,500</div>
            <div className={styles.metricDelta}>+12.5% с прошлого месяца</div>
          </div>

          <div className={styles.metricRow}>
            <div className={styles.metricCard}>
              <div className={styles.metricHeader}>Трейдеры</div>
              <div className={styles.metricValue}>48</div>
              <div className={styles.metricDelta}>+3 за неделю</div>
            </div>
            
            <div className={styles.metricCard}>
              <div className={styles.metricHeader}>Мерчанты</div>
              <div className={styles.metricValue}>124</div>
              <div className={styles.metricDelta}>+5 за неделю</div>
            </div>
          </div>

          <div className={styles.metricRow}>
            <div className={styles.metricCard}>
              <div className={styles.metricHeader}>Магазины</div>
              <div className={styles.metricValue}>196</div>
              <div className={styles.metricDelta}>+8 за неделю</div>
            </div>
            
            <div className={styles.metricCard}>
              <div className={styles.metricHeader}>Саппорт</div>
              <div className={styles.metricValue}>12</div>
              <div className={styles.metricDelta}>+1 за неделю</div>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.chartsSection}>
        <div className={styles.chart}>
          <div className={styles.chartHeader}>
            <h3>Доход и активность</h3>
            <div className={styles.selector}>За 7 дней</div>
          </div>
          <div className={styles.chartPlaceholder}>
            {/* Здесь будет график дохода */}
          </div>
        </div>

        <div className={styles.chart}>
          <div className={styles.chartHeader}>
            <h3>Конверсия ордеров</h3>
            <div className={styles.tabs}>
              <span className={styles.activeTab}>Все</span>
              <span>По мерчантам</span>
              <span>По магазинам</span>
            </div>
          </div>
          <div className={styles.chartPlaceholder}>
            {/* Здесь будет график конверсии */}
          </div>
        </div>
      </div>

      <div className={styles.statsSection}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>
            {/* Иконка для ордеров */}
          </div>
          <div className={styles.statHeader}>Ордеры в обработке</div>
          <div className={styles.statValue}>42</div>
          <div className={styles.statSubtext}>18 в процессе оплаты</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon}>
            {/* Иконка для реквизитов */}
          </div>
          <div className={styles.statHeader}>Реквизиты онлайн</div>
          <div className={styles.statValue}>156</div>
          <div className={styles.statSubtext}>83% доступность</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon}>
            {/* Иконка для конверсии */}
          </div>
          <div className={styles.statHeader}>Конверсия</div>
          <div className={styles.statValue}>89%</div>
          <div className={styles.statSubtext}>+4.2% за месяц</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon}>
            {/* Иконка для времени */}
          </div>
          <div className={styles.statHeader}>Среднее время</div>
          <div className={styles.statValue}>12m 30s</div>
          <div className={styles.statSubtext}>Обработка ордера</div>
        </div>
      </div>

      <div className={styles.ordersSection}>
        <div className={styles.sectionHeader}>
          <h3>История ордеров</h3>
          <Button variant="secondary">Смотреть все</Button>
        </div>
        <div className={styles.ordersTable}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Дата</th>
                <th>Пользователь</th>
                <th>Сумма Фиат</th>
                <th>Сумма Крипто</th>
                <th>Тип</th>
                <th>Статус</th>
                <th>Трейдер</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>ORD-2305001</td>
                <td>15.05.2023 12:30</td>
                <td>Иван Петров</td>
                <td>₽12,500</td>
                <td>250 USDT</td>
                <td>Pay In</td>
                <td><span className={styles.statusDone}>Выполнен</span></td>
                <td>Максим Иванов</td>
              </tr>
              <tr>
                <td>ORD-2305002</td>
                <td>15.05.2023 13:45</td>
                <td>Елена Сидорова</td>
                <td>₽8,300</td>
                <td>166 USDT</td>
                <td>Pay In</td>
                <td><span className={styles.statusProcessing}>В обработке</span></td>
                <td>Не назначен</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage; 