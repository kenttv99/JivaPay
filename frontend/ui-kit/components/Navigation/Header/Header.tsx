import React, { useState, useRef, useEffect } from 'react';

interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
  initials?: string;
  role?: string;
}

interface SearchResult {
  id: string;
  title: string;
  description?: string;
  type: 'user' | 'order' | 'store' | 'page';
  href: string;
}

interface HeaderProps {
  sidebarOpen?: boolean;
  setSidebarOpen?: (open: boolean) => void;
  userProfile?: UserProfile;
  showSearch?: boolean;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  searchResults?: SearchResult[];
  showNotifications?: boolean;
  notificationCount?: number;
  onNotificationClick?: () => void;
  onProfileClick?: () => void;
  onThemeToggle?: (theme: 'light' | 'dark') => void;
  currentTheme?: 'light' | 'dark';
  isLoading?: boolean;
  className?: string;
}

// Skeleton компонент для Header
const HeaderSkeleton: React.FC = () => (
  <header className="sticky top-0 z-10 flex h-14 items-center px-4 md:px-6 bg-background border-b border-border shadow-sm">
    <div className="flex flex-1 items-center gap-4 md:gap-6">
      <div className="relative w-full max-w-sm lg:max-w-md">
        <div className="w-full h-9 bg-muted rounded-md animate-pulse" />
      </div>
      <div className="ml-auto flex items-center gap-2">
        <div className="h-9 w-9 bg-muted rounded-full animate-pulse" />
        <div className="h-9 w-9 bg-muted rounded-full animate-pulse" />
        <div className="h-9 w-9 bg-muted rounded-full animate-pulse" />
      </div>
    </div>
  </header>
);

export const Header: React.FC<HeaderProps> = ({
  sidebarOpen = true,
  setSidebarOpen,
  userProfile,
  showSearch = true,
  searchPlaceholder = 'Поиск пользователей, заказов, магазинов...',
  onSearch,
  searchResults = [],
  showNotifications = true,
  notificationCount = 0,
  onNotificationClick,
  onProfileClick,
  onThemeToggle,
  currentTheme = 'light',
  isLoading = false,
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  // Закрытие dropdown при клике вне
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchDropdown(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setShowProfileDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    setShowSearchDropdown(query.length > 0);
    onSearch?.(query);
  };

  const toggleTheme = () => {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    onThemeToggle?.(newTheme);
  };

  // Показываем skeleton при загрузке
  if (isLoading) {
    return <HeaderSkeleton />;
  }

  return (
    <header 
      className={`sticky top-0 z-50 flex h-14 items-center px-4 md:px-6 bg-background border-b border-border shadow-sm backdrop-blur-sm animate-fadeIn ${className}`}
    >
      <div className="flex flex-1 items-center gap-4 md:gap-6">
        {/* Поиск с dropdown */}
        {showSearch && (
          <div ref={searchRef} className="relative w-full max-w-sm lg:max-w-md">
            <svg 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted transition-colors"
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="search"
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={handleSearch}
              onFocus={() => searchQuery && setShowSearchDropdown(true)}
              className="w-full rounded-lg pl-10 pr-4 py-2 text-sm bg-surface border border-border text-primary placeholder-muted transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary animated-transition"
            />
            
            {/* Search Dropdown */}
            {showSearchDropdown && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-lg shadow-lg max-h-64 overflow-y-auto animate-fadeIn z-50">
                {searchResults.map((result) => (
                  <a
                    key={result.id}
                    href={result.href}
                    className="flex items-center gap-3 px-4 py-3 hover:bg-surface transition-colors animated-transition"
                    onClick={() => setShowSearchDropdown(false)}
                  >
                    <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-medium ${
                      result.type === 'user' ? 'bg-info/10 text-info' :
                      result.type === 'order' ? 'bg-warning/10 text-warning' :
                      result.type === 'store' ? 'bg-success/10 text-success' :
                      'bg-neutral/10 text-neutral'
                    }`}>
                      {result.type === 'user' ? 'У' : 
                       result.type === 'order' ? 'З' :
                       result.type === 'store' ? 'М' : 'С'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-primary truncate">{result.title}</div>
                      {result.description && (
                        <div className="text-sm text-muted truncate">{result.description}</div>
                      )}
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
        
        <div className="ml-auto flex items-center gap-2">
          {/* Переключатель темы с анимацией */}
          <button
            className="relative rounded-full p-2 text-muted hover:text-primary hover:bg-surface transition-all duration-200 animated-transition"
            onClick={toggleTheme}
            aria-label={`Переключить на ${currentTheme === 'dark' ? 'светлую' : 'темную'} тему`}
          >
            <div className="relative h-5 w-5">
              {/* Солнце */}
              <svg 
                className={`absolute inset-0 h-5 w-5 transition-all duration-300 ${
                  currentTheme === 'light' ? 'rotate-0 opacity-100' : 'rotate-180 opacity-0'
                }`}
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              {/* Луна */}
              <svg 
                className={`absolute inset-0 h-5 w-5 transition-all duration-300 ${
                  currentTheme === 'dark' ? 'rotate-0 opacity-100' : '-rotate-180 opacity-0'
                }`}
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </div>
          </button>

          {/* Уведомления с анимированным badge */}
          {showNotifications && (
            <button 
              className="relative rounded-full p-2 text-muted hover:text-primary hover:bg-surface transition-all duration-200 animated-transition"
              onClick={onNotificationClick}
              aria-label={`Уведомления${notificationCount > 0 ? ` (${notificationCount})` : ''}`}
            >
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zm-8-3.5a5.5 5.5 0 1111 0 5.5 5.5 0 01-11 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.73 21a2 2 0 01-3.46 0" />
              </svg>
              {notificationCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center text-xs font-medium text-white bg-error rounded-full animate-pulse">
                  {notificationCount > 99 ? '99+' : notificationCount}
                </span>
              )}
            </button>
          )}

          {/* Профиль с dropdown */}
          {userProfile && (
            <div ref={profileRef} className="relative">
              <button 
                className="rounded-full p-1 hover:bg-surface transition-all duration-200 animated-transition"
                onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                aria-label="Меню профиля"
              >
                <div className="h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium text-white bg-primary">
                  {userProfile.avatar ? (
                    <img 
                      src={userProfile.avatar} 
                      alt={userProfile.name} 
                      className="w-full h-full rounded-full object-cover" 
                    />
                  ) : (
                    userProfile.initials || userProfile.name.charAt(0).toUpperCase()
                  )}
                </div>
              </button>

              {/* Profile Dropdown */}
              {showProfileDropdown && (
                <div className="absolute top-full right-0 mt-2 w-64 bg-background border border-border rounded-lg shadow-lg animate-fadeIn z-50">
                  <div className="p-4 border-b border-border">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full flex items-center justify-center text-sm font-medium text-white bg-primary">
                        {userProfile.avatar ? (
                          <img 
                            src={userProfile.avatar} 
                            alt={userProfile.name} 
                            className="w-full h-full rounded-full object-cover" 
                          />
                        ) : (
                          userProfile.initials || userProfile.name.charAt(0).toUpperCase()
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-primary truncate">{userProfile.name}</div>
                        <div className="text-sm text-muted truncate">{userProfile.email}</div>
                        {userProfile.role && (
                          <div className="text-xs text-secondary font-medium">{userProfile.role}</div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-2">
                    <button
                      onClick={() => {
                        onProfileClick?.();
                        setShowProfileDropdown(false);
                      }}
                      className="flex w-full items-center gap-3 px-3 py-2 text-sm font-medium text-primary hover:bg-surface rounded-lg transition-colors animated-transition"
                    >
                      <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Настройки профиля
                    </button>
                    
                    <button
                      className="flex w-full items-center gap-3 px-3 py-2 text-sm font-medium text-error hover:bg-error-light rounded-lg transition-colors animated-transition"
                    >
                      <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Выйти
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}; 