'use client';

import React, { useState } from 'react';
import { MerchantSidebar } from '../components/widgets/MerchantSidebar';
import { MerchantHeader } from '../components/widgets/MerchantHeader';

interface MerchantLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const MerchantLayout: React.FC<MerchantLayoutProps> = ({
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
        <MerchantSidebar 
          isOpen={sidebarOpen} 
          onToggle={toggleSidebar}
        />
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <MerchantHeader onSidebarToggle={toggleSidebar} />
        
        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6 animate-fadeIn">
          {children}
        </main>
      </div>
    </div>
  );
}; 