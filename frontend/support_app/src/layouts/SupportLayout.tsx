'use client';

import React, { useState } from 'react';
import { SupportSidebar } from '../components/widgets/SupportSidebar';
import { SupportHeader } from '../components/widgets/SupportHeader';

interface SupportLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const SupportLayout: React.FC<SupportLayoutProps> = ({
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
      <SupportSidebar 
        isOpen={sidebarOpen} 
        onToggle={toggleSidebar}
        className="flex-shrink-0"
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <SupportHeader 
          onSidebarToggle={toggleSidebar}
          className="flex-shrink-0"
        />
        
        {/* Content */}
        <main className="flex-1 p-6 overflow-auto bg-surface">
          <div className="max-w-7xl mx-auto animate-fadeIn">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}; 