import React, { useState, useRef, useEffect } from 'react';

interface DropdownItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  danger?: boolean;
  onClick: () => void;
}

interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
  className?: string;
}

export const Dropdown: React.FC<DropdownProps> = ({
  trigger,
  items,
  placement = 'bottom-start',
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  const getPlacementClasses = (placement: string) => {
    switch (placement) {
      case 'bottom-end':
        return 'top-full right-0 mt-1';
      case 'top-start':
        return 'bottom-full left-0 mb-1';
      case 'top-end':
        return 'bottom-full right-0 mb-1';
      default:
        return 'top-full left-0 mt-1';
    }
  };

  const handleItemClick = (item: DropdownItem) => {
    if (!item.disabled) {
      item.onClick();
      setIsOpen(false);
    }
  };

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      <div onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </div>

      {isOpen && (
        <div
          className={`
            absolute z-50 min-w-[160px] bg-surface border border-border
            rounded-md shadow-lg mt-1 py-1 
            ${placement === 'bottom-start' ? 'left-0' : placement === 'bottom-end' ? 'right-0' : placement === 'top-start' ? 'bottom-full left-0 mb-1' : 'bottom-full right-0 mb-1'}
          `}
        >
          {items.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => handleItemClick(item)}
              disabled={item.disabled}
              className={`
                w-full text-left px-3 py-2 text-sm transition-colors
                ${item.disabled 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:bg-background focus:bg-background'
                }
                ${item.danger ? 'text-error' : 'text-primary'}
              `}
            >
              {item.icon && (
                <span className="flex-shrink-0">
                  {item.icon}
                </span>
              )}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}; 