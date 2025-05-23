import React from 'react';

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
  LinkComponent?: React.ComponentType<{ href: string; className?: string; children: React.ReactNode }>;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen = true,
  setIsOpen,
  navigation,
  userProfile,
  logo = 'JivaPay',
  shortLogo = 'J',
  onLogout,
  LinkComponent = 'a' as any
}) => {
  return (
    <div className={`relative flex flex-col bg-gray-900 transition-all duration-300 ease-in-out h-full ${isOpen ? 'w-64' : 'w-16'}`}>
      {/* Логотип */}
      <div className="flex h-14 items-center px-4 border-b border-gray-700">
        {isOpen ? (
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-white text-gray-900">
              <span className="font-bold text-lg">{shortLogo}</span>
            </div>
            <span className="font-semibold text-lg text-white">{logo}</span>
            <span className="text-sm text-gray-400">Админ</span>
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-white text-gray-900 mx-auto">
            <span className="font-bold text-lg">{shortLogo}</span>
          </div>
        )}
      </div>

      {/* Кнопка переключения */}
      <button
        className="absolute right-[-12px] top-6 h-6 w-6 rounded-full border border-gray-300 bg-white shadow-md hover:bg-gray-50 transition-colors flex items-center justify-center"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? (
          <svg className="h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        ) : (
          <svg className="h-4 w-4 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        )}
      </button>

      {/* Навигация */}
      <div className="flex flex-col flex-1 py-4">
        <nav className="grid gap-1 px-2">
          {navigation.map((item) => (
            <LinkComponent
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 rounded-lg px-3 py-3 text-sm transition-colors ${
                item.isActive
                  ? "bg-white text-gray-900"
                  : "text-gray-300 hover:bg-gray-700 hover:text-white"
              }`}
            >
              {item.icon}
              {isOpen && <span className="font-medium">{item.name}</span>}
            </LinkComponent>
          ))}
        </nav>
      </div>

      {/* Кнопка выхода */}
      {onLogout && (
        <div className="p-2 mt-auto border-t border-gray-700">
          <button 
            onClick={onLogout}
            className="flex w-full items-center justify-start space-x-3 rounded-lg px-3 py-3 text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
          >
            <svg className="h-5 w-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            {isOpen && <span className="font-medium">Выйти</span>}
          </button>
        </div>
      )}
    </div>
  );
}; 