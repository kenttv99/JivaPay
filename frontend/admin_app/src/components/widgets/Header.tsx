import { useState } from 'react';

interface HeaderProps {
  sidebarOpen?: boolean;
  setSidebarOpen?: (open: boolean) => void;
}

const Header = ({ sidebarOpen = true, setSidebarOpen }: HeaderProps) => {
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  return (
    <header className="sticky top-0 bg-[var(--jiva-background-header)] border-b border-[var(--jiva-border)] px-4 h-16 flex items-center justify-between z-10">
      <div className="flex items-center">
        <button 
          type="button"
          className="text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text)] p-2"
          onClick={() => setSidebarOpen && setSidebarOpen(!sidebarOpen)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
      </div>

      <div className="flex items-center gap-4">
        {/* Поиск */}
        <div className="hidden md:flex relative">
          <input
            type="text"
            placeholder="Поиск..."
            className="pl-10 pr-4 py-2 rounded-full border border-[var(--jiva-border)] focus:outline-none focus:ring-2 focus:ring-[var(--jiva-primary-light)] w-64"
          />
          <svg
            className="absolute left-3 top-2.5 text-[var(--jiva-text-secondary)]"
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </div>

        {/* Уведомления */}
        <div className="relative">
          <button 
            className="p-2 text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text)]"
            onClick={() => setNotificationsOpen(!notificationsOpen)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span className="absolute top-1 right-1 w-4 h-4 bg-[var(--jiva-error)] text-white text-xs flex items-center justify-center rounded-full">3</span>
          </button>
        </div>

        {/* Профиль */}
        <div className="relative">
          <button 
            className="flex items-center gap-2"
            onClick={() => setProfileOpen(!profileOpen)}
          >
            <div className="w-8 h-8 rounded-full bg-[var(--jiva-primary)] text-white flex items-center justify-center">
              АА
            </div>
            <span className="hidden md:block font-medium">Админ</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 