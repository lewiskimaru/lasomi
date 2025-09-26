import React from 'react';
import { useStorageInfo } from '@/react-app/hooks/useStorage';
import { 
  ExclamationTriangleIcon,
  InformationCircleIcon 
} from '@heroicons/react/24/outline';

interface StorageStatusProps {
  className?: string;
}

export const StorageStatus: React.FC<StorageStatusProps> = ({ className = '' }) => {
  const { info } = useStorageInfo();

  const getStorageWarning = () => {
    if (!info.localStorage.available) {
      return {
        type: 'error' as const,
        message: 'Browser storage not available. Settings and data will not persist.'
      };
    }

    const percentage = info.localStorage.percentage || 0;

    if (percentage > 80) {
      return {
        type: 'warning' as const,
        message: `Storage is ${Math.round(percentage)}% full. Consider exporting your data.`
      };
    }

    if (percentage > 60) {
      return {
        type: 'info' as const,
        message: `Storage is ${Math.round(percentage)}% full.`
      };
    }

    return null;
  };

  const warning = getStorageWarning();

  if (!warning) return null;

  return (
    <div className={`flex items-center gap-2 p-3 rounded-md text-sm ${
      warning.type === 'error' 
        ? 'bg-red-600 bg-opacity-20 text-red-300 border border-red-600 border-opacity-30'
        : warning.type === 'warning'
        ? 'bg-yellow-600 bg-opacity-20 text-yellow-300 border border-yellow-600 border-opacity-30'
        : 'bg-blue-600 bg-opacity-20 text-blue-300 border border-blue-600 border-opacity-30'
    } ${className}`}>
      {warning.type === 'error' || warning.type === 'warning' ? (
        <ExclamationTriangleIcon className="w-4 h-4 flex-shrink-0" />
      ) : (
        <InformationCircleIcon className="w-4 h-4 flex-shrink-0" />
      )}
      <span>{warning.message}</span>
    </div>
  );
};
