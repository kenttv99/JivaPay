import React, { useState } from 'react';

interface UserProfile {
  name: string;
  avatar?: string;
  initials?: string;
}

interface HeaderProps {
  sidebarOpen?: boolean;
  setSidebarOpen?: (open: boolean) => void;
  userProfile?: UserProfile;
  showSearch?: boolean;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  showNotifications?: boolean;
  notificationCount?: number;
  onNotificationClick?: () => void;
  onProfileClick?: () => void;
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({
  sidebarOpen = true,
  setSidebarOpen,
  userProfile,
  showSearch = true,
  searchPlaceholder = 'Поиск...',
  onSearch,
  showNotifications = true,
  notificationCount = 0,
  onNotificationClick,
  onProfileClick,
  className = ''
}) => {
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch?.(query);
  };

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header className={`sticky top-0 z-10 flex h-14 items-center border-b border-gray-200 bg-white px-4 md:px-6 ${className}`}>
      <div className="flex flex-1 items-center gap-4 md:gap-6">
        {/* Поиск */}
        {showSearch && (
          <div className="relative w-full max-w-sm lg:max-w-md">
            <svg className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="search"
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={handleSearch}
              className="w-full bg-gray-50 border border-gray-200 rounded-md pl-8 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}
        
        <div className="ml-auto flex items-center gap-2">
          {/* Переключатель темы */}
          <button
            className="rounded-full p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
            onClick={toggleTheme}
          >
            {theme === "dark" ? (
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>

          {/* Уведомления */}
          {showNotifications && (
            <button className="rounded-full p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors relative">
              <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zm-8-3.5a5.5 5.5 0 1111 0 5.5 5.5 0 01-11 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.73 21a2 2 0 01-3.46 0" />
              </svg>
              {notificationCount > 0 && (
                <span className="absolute top-1 right-1 flex h-2 w-2 rounded-full" style={{ backgroundColor: 'var(--color-info)' }} />
              )}
            </button>
          )}

          {/* Профиль */}
          {userProfile && (
            <button className="rounded-full p-1 hover:bg-gray-100 transition-colors">
              <div className="h-8 w-8 rounded-full text-white flex items-center justify-center text-sm font-medium" style={{ backgroundColor: 'var(--color-info)' }}>
                {userProfile.avatar ? (
                  <img src={userProfile.avatar} alt={userProfile.name} className="w-full h-full rounded-full object-cover" />
                ) : (
                  userProfile.initials || userProfile.name.charAt(0).toUpperCase()
                )}
              </div>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}; 