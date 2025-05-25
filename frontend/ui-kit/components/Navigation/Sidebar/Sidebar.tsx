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
    <div 
      className={`relative flex flex-col transition-all duration-300 ease-in-out h-full ${isOpen ? 'w-64' : 'w-16'}`}
      style={{ 
        backgroundColor: 'var(--sidebar-background)',
        borderRight: '1px solid #475569'
      }}
    >
      {/* Логотип */}
      <div className="flex h-14 items-center px-4">
        {isOpen ? (
          <div className="flex items-center space-x-2">
            <div 
              className="flex h-6 w-6 items-center justify-center rounded-md font-bold"
              style={{ 
                backgroundColor: 'var(--primary)',
                color: 'white'
              }}
            >
              <span className="text-sm">{shortLogo}</span>
            </div>
            <span 
              className="font-semibold text-lg text-white"
            >
              {logo}
            </span>
          </div>
        ) : (
          <div 
            className="flex h-8 w-8 items-center justify-center rounded-md mx-auto font-bold"
            style={{ 
              backgroundColor: 'var(--primary)',
              color: 'white'
            }}
          >
            <span>{shortLogo}</span>
          </div>
        )}
      </div>

      {/* Кнопка переключения */}
      <button
        className="absolute right-[-12px] top-6 h-6 w-6 rounded-full border bg-white shadow-md hover:bg-gray-50 transition-colors flex items-center justify-center z-10"
        style={{ borderColor: '#e5e7eb' }}
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

      {/* Навигация с прокруткой */}
      <div className="flex flex-col flex-1 py-4 overflow-y-auto">
        <nav className="grid gap-1 px-2">
          {navigation.map((item) => (
            <LinkComponent
              key={item.name}
              href={item.href}
              className="flex items-center space-x-2 rounded-lg px-3 py-2 text-sm transition-colors font-medium"
              style={{
                backgroundColor: item.isActive ? 'var(--primary)' : 'transparent',
                color: item.isActive ? 'white' : '#cbd5e1'
              }}
              onMouseEnter={(e: any) => {
                if (!item.isActive) {
                  e.target.style.backgroundColor = '#334155';
                  e.target.style.color = 'white';
                }
              }}
              onMouseLeave={(e: any) => {
                if (!item.isActive) {
                  e.target.style.backgroundColor = 'transparent';
                  e.target.style.color = '#cbd5e1';
                }
              }}
            >
              <span className="h-5 w-5 flex-shrink-0">{item.icon}</span>
              {isOpen && <span>{item.name}</span>}
            </LinkComponent>
          ))}
        </nav>
      </div>

      {/* Разделитель */}
      {onLogout && (
        <div 
          className="mx-2 my-2 h-px"
          style={{ backgroundColor: '#475569' }}
        />
      )}

      {/* Кнопка выхода */}
      {onLogout && (
        <div className="p-2">
          <button 
            onClick={onLogout}
            className="flex w-full items-center justify-start space-x-2 rounded-lg px-3 py-2 text-sm transition-colors font-medium"
            style={{ color: '#cbd5e1' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#334155';
              e.currentTarget.style.color = 'white';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#cbd5e1';
            }}
          >
            <svg className="h-5 w-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            {isOpen && <span>Выйти</span>}
          </button>
        </div>
      )}
    </div>
  );
}; 