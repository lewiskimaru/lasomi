import React from 'react';
import { useStorage } from '@/react-app/context/StorageContext';
import { 
  SparklesIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

export const WelcomeMessage: React.FC = () => {
  const { firstVisit, markFirstVisitComplete } = useStorage();

  if (!firstVisit) return null;

  return (
    <div className="bg-gradient-to-r from-lasomi-primary to-blue-600 border border-border rounded-lg p-6 mb-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20"></div>
      
      <div className="relative flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center flex-shrink-0">
          <SparklesIcon className="w-6 h-6 text-white" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white mb-2">
            Welcome to Lasomi!
          </h3>
          <p className="text-blue-100 text-sm mb-4">
            Your telecom infrastructure platform is ready. All your work will be automatically saved to your browser - 
            no account required. Choose an app below to get started with your project.
          </p>
          
          <div className="flex flex-wrap gap-2 text-xs text-blue-100">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span>Auto-save enabled</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
              <span>Activity tracking</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
              <span>Local storage</span>
            </div>
          </div>
        </div>
        
        <button
          onClick={markFirstVisitComplete}
          className="p-1 text-white/70 hover:text-white hover:bg-white/10 rounded-md transition-colors"
          title="Dismiss welcome message"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
