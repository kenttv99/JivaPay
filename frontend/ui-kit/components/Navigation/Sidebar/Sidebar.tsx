import React, { useState, useEffect } from 'react';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ReactNode;
  isActive?: boolean;
}

interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
  initials?: string;
}

interface SidebarProps {
  isOpen?: boolean;
  setIsOpen: (open: boolean) => void;
  navigation: NavigationItem[];
  userProfile?: UserProfile;
  logo?: string;
  shortLogo?: string;
  onLogout?: () => void;
  isLoading?: boolean;
  LinkComponent?: React.ComponentType<{ href: string; className?: string; children: React.ReactNode }>;
}

// Skeleton компонент для loading состояния
const SidebarSkeleton: React.FC<{ isOpen: boolean }> = ({ isOpen }) => (
  <div className={`relative flex flex-col h-full bg-background border-r border-border transition-all duration-300 ${isOpen ? 'w-64' : 'w-16'}`}>
    {/* Skeleton логотипа */}
    <div className="flex h-14 items-center px-4">
      {isOpen ? (
        <div className="flex items-center space-x-2">
          <div className="h-6 w-6 bg-muted rounded-md animate-pulse" />
          <div className="h-5 w-20 bg-muted rounded animate-pulse" />
        </div>
      ) : (
        <div className="h-8 w-8 bg-muted rounded-md mx-auto animate-pulse" />
      )}
    </div>

    {/* Skeleton навигации */}
    <div className="flex flex-col flex-1 py-4 px-2 space-y-2">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="flex items-center space-x-2 px-3 py-2">
          <div className="h-5 w-5 bg-muted rounded animate-pulse" />
          {isOpen && <div className="h-4 w-24 bg-muted rounded animate-pulse" />}
        </div>
      ))}
    </div>
  </div>
);

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen = true,
  setIsOpen,
  navigation,
  userProfile,
  logo = 'JivaPay',
  shortLogo = 'J',
  onLogout,
  isLoading = false,
  LinkComponent = 'a' as any
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Показываем skeleton при загрузке
  if (isLoading || !mounted) {
    return <SidebarSkeleton isOpen={isOpen} />;
  }

  return (
    <div 
      className={`relative flex flex-col h-full bg-background border-r border-border transition-all duration-300 ease-in-out animate-fadeIn ${isOpen ? 'w-64' : 'w-16'}`}
      style={{ animation: isOpen ? 'slideInLeft 0.3s ease-out' : 'none' }}
    >
      {/* Логотип */}
      <div className="flex h-14 items-center px-4 border-b border-border">
        {isOpen ? (
          <div className="flex items-center space-x-2 animate-fadeIn">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-white font-bold">
              <span className="text-sm">{shortLogo}</span>
            </div>
            <span className="font-semibold text-lg text-primary">
              {logo}
            </span>
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-white mx-auto font-bold">
            <span>{shortLogo}</span>
          </div>
        )}
      </div>

      {/* Кнопка переключения */}
      <button
        className="absolute right-[-12px] top-6 h-6 w-6 rounded-full border border-border bg-background shadow-md hover:bg-surface transition-all duration-200 flex items-center justify-center z-10 animated-transition"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Свернуть sidebar' : 'Развернуть sidebar'}
      >
        {isOpen ? (
          <svg className="h-4 w-4 text-muted" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        ) : (
          <svg className="h-4 w-4 text-muted" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        )}
      </button>

      {/* Навигация с прокруткой */}
      <div className="flex flex-col flex-1 py-4 overflow-y-auto">
        <nav className="grid gap-1 px-2">
          {navigation.map((item, index) => (
            <LinkComponent
              key={item.name}
              href={item.href}
              className={`
                flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 animated-transition
                ${item.isActive 
                  ? 'bg-primary text-white shadow-sm' 
                  : 'text-muted hover:bg-surface hover:text-primary'
                }
              `}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <span className="h-5 w-5 flex-shrink-0">{item.icon}</span>
              {isOpen && (
                <span className="animate-fadeIn" style={{ animationDelay: '100ms' }}>
                  {item.name}
                </span>
              )}
            </LinkComponent>
          ))}
        </nav>
      </div>

      {/* Разделитель */}
      {onLogout && (
        <div className="mx-2 my-2 h-px bg-border" />
      )}

      {/* Кнопка выхода */}
      {onLogout && (
        <div className="p-2">
          <button 
            onClick={onLogout}
            className="flex w-full items-center justify-start space-x-2 rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface hover:text-primary transition-all duration-200 animated-transition"
            aria-label="Выйти из системы"
          >
            <svg className="h-5 w-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            {isOpen && (
              <span className="animate-fadeIn" style={{ animationDelay: '100ms' }}>
                Выйти
              </span>
            )}
          </button>
        </div>
      )}

      {/* Мобильный режим - скрыто на desktop, показано на mobile как BottomNav */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-background border-t border-border z-50">
        <nav className="flex justify-around py-2">
          {navigation.slice(0, 4).map((item) => (
            <LinkComponent
              key={item.name}
              href={item.href}
              className={`
                flex flex-col items-center space-y-1 px-3 py-2 text-xs font-medium transition-colors animated-transition
                ${item.isActive 
                  ? 'text-primary' 
                  : 'text-muted hover:text-primary'
                }
              `}
            >
              <span className="h-5 w-5">{item.icon}</span>
              <span className="truncate max-w-[50px]">{item.name}</span>
            </LinkComponent>
          ))}
        </nav>
      </div>
    </div>
  );
}; 