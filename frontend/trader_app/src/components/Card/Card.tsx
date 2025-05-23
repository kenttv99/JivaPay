import React from 'react';
import classNames from 'classnames';
import styles from './Card.module.css';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'dark';
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = 'default',
  ...props
}) => (
  <div className={classNames(styles.card, styles[variant], className)} {...props}>
    {children}
  </div>
); 