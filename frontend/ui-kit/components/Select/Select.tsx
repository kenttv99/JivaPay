import React, { useState, useRef, useEffect } from 'react';

interface Option {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SelectProps {
  options: Option[];
  value?: string;
  placeholder?: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  placeholder = 'Выберите опцию',
  onChange,
  disabled = false,
  error,
  className = '',
  size = 'md'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);

  const getSizeClasses = (size: string) => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1.5 text-sm';
      case 'lg':
        return 'px-4 py-3 text-lg';
      default:
        return 'px-3 py-2 text-sm';
    }
  };

  const selectedOption = options.find(option => option.value === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleOptionClick = (optionValue: string) => {
    if (!disabled) {
      onChange(optionValue);
      setIsOpen(false);
    }
  };

  return (
    <div className={`relative ${className}`} ref={selectRef}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          w-full text-left bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md 
          focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent 
          transition-colors ${getSizeClasses(size)}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-[var(--color-accent)]'}
          ${error ? 'border-[var(--color-error)]' : ''}
        `}
      >
        <span className={`block truncate ${selectedOption ? 'text-[var(--color-primary)]' : 'text-[var(--color-secondary)]'}`}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <svg
            className={`w-5 h-5 text-[var(--color-secondary)] transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md shadow-lg max-h-60 overflow-auto">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleOptionClick(option.value)}
              disabled={option.disabled}
              className={`
                w-full text-left px-3 py-2 text-sm transition-colors
                ${option.disabled 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:bg-[var(--color-bg)] focus:bg-[var(--color-bg)]'
                }
                ${option.value === value 
                  ? 'bg-[var(--color-accent)] bg-opacity-10 text-[var(--color-accent)]' 
                  : 'text-[var(--color-primary)]'
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}

      {error && (
        <p className="mt-1 text-sm text-[var(--color-error)]">
          {error}
        </p>
      )}
    </div>
  );
}; 