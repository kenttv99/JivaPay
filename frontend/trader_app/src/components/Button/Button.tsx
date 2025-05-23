import React from 'react';
import classNames from 'classnames';
import styles from './Button.module.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  ...props
}) => (
  <button
    className={classNames(
      styles.button, 
      styles[variant === 'outline' ? 'ghost' : variant], 
      styles[size], 
      className
    )}
    {...props}
  >
    {children}
  </button>
); 