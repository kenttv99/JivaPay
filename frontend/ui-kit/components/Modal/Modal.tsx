import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showCloseButton?: boolean;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  footer?: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  className = '',
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  footer
}) => {
  const [mounted, setMounted] = useState(false);
  const [animationClass, setAnimationClass] = useState('');

  // Монтирование компонента
  useEffect(() => {
    setMounted(true);
  }, []);

  // Обработка ESC и блокировка скролла
  useEffect(() => {
    if (!isOpen) return;

    // Блокировка скролла body
    const originalStyle = window.getComputedStyle(document.body).overflow;
    document.body.style.overflow = 'hidden';

    // Обработка ESC
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closeOnEscape) {
        onClose();
      }
    };

    if (closeOnEscape) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.body.style.overflow = originalStyle;
      if (closeOnEscape) {
        document.removeEventListener('keydown', handleEscape);
      }
    };
  }, [isOpen, onClose, closeOnEscape]);

  // Анимации появления/исчезновения
  useEffect(() => {
    if (isOpen) {
      setAnimationClass('animate-fadeIn');
    }
  }, [isOpen]);

  const getSizeClasses = (size: string) => {
    switch (size) {
      case 'sm':
        return 'max-w-sm';
      case 'lg':
        return 'max-w-2xl';
      case 'xl':
        return 'max-w-4xl';
      default:
        return 'max-w-lg';
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (closeOnBackdropClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!mounted || !isOpen) return null;

  const modalContent = (
    <div 
      className={`fixed inset-0 z-50 overflow-y-auto ${animationClass}`}
      style={{ animation: 'fadeIn 0.2s ease-out' }}
    >
      {/* Backdrop с blur эффектом */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-all duration-300"
        onClick={handleBackdropClick}
        style={{ animation: 'fadeIn 0.2s ease-out' }}
      />

      {/* Modal Container */}
      <div 
        className="flex min-h-full items-center justify-center p-4"
        onClick={handleBackdropClick}
      >
        <div
          className={`
            relative w-full ${getSizeClasses(size)} 
            bg-background rounded-lg shadow-2xl border border-border
            transform transition-all duration-300 animated-transition
            ${className}
          `}
          onClick={(e) => e.stopPropagation()}
          style={{ 
            animation: 'slideInLeft 0.3s ease-out, fadeIn 0.3s ease-out'
          }}
        >
          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-border">
              {title && (
                <h3 className="text-lg font-semibold text-primary pr-4">
                  {title}
                </h3>
              )}
              
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="
                    flex-shrink-0 p-2 rounded-full transition-all duration-200 
                    text-muted hover:text-primary hover:bg-surface
                    focus:outline-none focus:ring-2 focus:ring-secondary/20
                    animated-transition
                  "
                  aria-label="Закрыть модальное окно"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="px-6 py-4 max-h-[calc(100vh-200px)] overflow-y-auto">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="px-6 py-4 border-t border-border bg-surface/50">
              {footer}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Используем портал для рендера в body
  return createPortal(modalContent, document.body);
}; 