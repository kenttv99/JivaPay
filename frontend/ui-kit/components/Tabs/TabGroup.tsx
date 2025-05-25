import React, { useState } from 'react';

interface Tab {
  key: string;
  label: string;
  count?: number;
  content: React.ReactNode;
}

interface TabGroupProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
}

export const TabGroup: React.FC<TabGroupProps> = ({ 
  tabs, 
  defaultTab, 
  className = '' 
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.key);

  return (
    <div className={className}>
      {/* Tab Navigation */}
      <div className="border-b border-border mb-6">
        <div className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-accent text-accent'
                  : 'border-transparent text-secondary hover:text-primary hover:border-neutral'
              }`}
            >
              {tab.label}
              {tab.count !== undefined && (
                <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                  activeTab === tab.key
                    ? 'bg-accent text-white'
                    : 'bg-background text-secondary'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {tabs.map((tab) => (
          <div
            key={tab.key}
            className={activeTab === tab.key ? 'block' : 'hidden'}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
}; 