import React from 'react';
import { 
  MagnifyingGlassIcon, 
  Cog8ToothIcon, 
  BellIcon,
  UserCircleIcon 
} from '@heroicons/react/24/outline';

interface TopBarProps {
  projectName?: string;
  onSearch?: (query: string) => void;
  onSettingsClick?: () => void;
  onNotificationsClick?: () => void;
  onProfileClick?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  projectName = "Lasomi",
  onSearch,
  onSettingsClick,
  onNotificationsClick,
  onProfileClick
}) => {
  return (
    <header className="top-bar">
      {/* Left section - Logo and project name */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-md flex items-center justify-center">
            <img 
              src="/lasomi-logo.svg" 
              alt="Lasomi" 
              className="w-8 h-8"
            />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-text-primary">Lasomi</h1>
            {projectName !== "Lasomi" && (
              <p className="text-xs text-text-secondary">{projectName}</p>
            )}
          </div>
        </div>
      </div>

      {/* Center section - Search */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            placeholder="Search projects, AOIs, or locations..."
            className="form-input pl-10 w-full"
            onChange={(e) => onSearch?.(e.target.value)}
          />
        </div>
      </div>

      {/* Right section - Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onNotificationsClick}
          className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-md transition-colors relative"
          title="Notifications"
        >
          <BellIcon className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
        </button>

        <button
          onClick={onSettingsClick}
          className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-md transition-colors"
          title="Settings"
        >
          <Cog8ToothIcon className="w-5 h-5" />
        </button>

        <button
          onClick={onProfileClick}
          className="p-2 text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary rounded-md transition-colors"
          title="Profile"
        >
          <UserCircleIcon className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};
