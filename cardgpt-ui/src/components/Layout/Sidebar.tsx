import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';
import SettingsPanel from '../Settings/SettingsPanel';
import { ModelInfo, QueryMode, CardFilter } from '../../types';

interface SidebarProps {
  models: ModelInfo[];
  selectedModel: string;
  onModelChange: (model: string) => void;
  queryMode: QueryMode;
  onQueryModeChange: (mode: QueryMode) => void;
  cardFilter: CardFilter;
  onCardFilterChange: (filter: CardFilter) => void;
  topK: number;
  onTopKChange: (topK: number) => void;
  isLoading?: boolean;
}

const Sidebar: React.FC<SidebarProps> = (props) => {
  const { isOpen, isMobile, closeSidebar, setMobile } = useSidebar();

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 1024; // lg breakpoint
      setMobile(mobile);
    };

    handleResize(); // Check on mount
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [setMobile]);

  // Close sidebar when clicking outside on mobile
  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (isMobile && isOpen) {
        const target = event.target as HTMLElement;
        if (!target.closest('.sidebar') && !target.closest('.sidebar-toggle')) {
          closeSidebar();
        }
      }
    };

    document.addEventListener('click', handleOutsideClick);
    return () => document.removeEventListener('click', handleOutsideClick);
  }, [isMobile, isOpen, closeSidebar]);

  // Don't render on mobile when closed
  if (isMobile && !isOpen) {
    return null;
  }

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={closeSidebar}
        />
      )}
      
      {/* Sidebar */}
      <div className={`sidebar fixed lg:relative z-50 lg:z-auto transition-transform duration-300 ease-in-out ${
        isMobile 
          ? `inset-y-0 left-0 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'}`
          : `${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`
      } ${isOpen ? 'w-80' : 'w-0 lg:w-16'}`}>
        <div className="h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Mobile close button */}
          {isMobile && (
            <div className="flex justify-between items-center p-4 lg:hidden border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Settings</h3>
              <button
                onClick={closeSidebar}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex-shrink-0"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
            </div>
          )}
          
          {/* Settings Panel */}
          <div className={`flex-1 overflow-hidden transition-opacity duration-300 ${
            isOpen ? 'opacity-100' : 'opacity-0 lg:opacity-100'
          }`}>
            {isOpen && (
              <SettingsPanel
                models={props.models}
                selectedModel={props.selectedModel}
                onModelChange={props.onModelChange}
                queryMode={props.queryMode}
                onQueryModeChange={props.onQueryModeChange}
                cardFilter={props.cardFilter}
                onCardFilterChange={props.onCardFilterChange}
                topK={props.topK}
                onTopKChange={props.onTopKChange}
                isLoading={props.isLoading}
              />
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;