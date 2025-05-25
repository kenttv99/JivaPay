'use client';

import React, { useState } from 'react';
import { TeamleadSidebar } from '../components/widgets/TeamleadSidebar';
import { TeamleadHeader } from '../components/widgets/TeamleadHeader';

interface TeamleadLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const TeamleadLayout: React.FC<TeamleadLayoutProps> = ({
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
      <TeamleadSidebar 
        isOpen={sidebarOpen} 
        onToggle={toggleSidebar}
        className="flex-shrink-0"
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <TeamleadHeader 
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