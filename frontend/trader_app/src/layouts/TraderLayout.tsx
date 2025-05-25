'use client';

import React, { useState } from 'react';
import { TraderSidebar } from '../components/widgets/TraderSidebar';
import { TraderHeader } from '../components/widgets/TraderHeader';

interface TraderLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const TraderLayout: React.FC<TraderLayoutProps> = ({
  children,
  className = ''
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className={`min-h-screen bg-background flex ${className}`}>
      {/* Sidebar */}
      <aside className="flex-shrink-0 h-screen sticky top-0">
        <TraderSidebar 
          isOpen={sidebarOpen} 
          onToggle={toggleSidebar}
        />
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <TraderHeader onSidebarToggle={toggleSidebar} />
        
        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6 animate-fadeIn">
          {children}
        </main>
      </div>
    </div>
  );
}; 