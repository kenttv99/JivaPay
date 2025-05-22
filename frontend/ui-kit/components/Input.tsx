import React from 'react';
import classNames from 'classnames';
import styles from './Input.module.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Input: React.FC<InputProps> = ({ label, className, ...props }) => (
  <label className={styles.wrapper}>
    {label && <span className={styles.label}>{label}</span>}
    <input className={classNames(styles.input, className)} {...props} />
  </label>
); 