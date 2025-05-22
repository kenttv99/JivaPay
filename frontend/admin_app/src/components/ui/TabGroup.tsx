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
      <div className="border-b border-[var(--jiva-border)] mb-6">
        <div className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-[var(--jiva-primary)] text-[var(--jiva-primary)]'
                  : 'border-transparent text-[var(--jiva-text-secondary)] hover:text-[var(--jiva-text-primary)] hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.count !== undefined && (
                <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                  activeTab === tab.key
                    ? 'bg-[var(--jiva-primary)] text-white'
                    : 'bg-[var(--jiva-background)] text-[var(--jiva-text-secondary)]'
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