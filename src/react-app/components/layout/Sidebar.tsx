import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  MapIcon,
  FolderIcon,
  DocumentChartBarIcon,
  WrenchScrewdriverIcon,
  ClipboardDocumentListIcon,
  CogIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import type { NavigationItem } from '@/shared/types';

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'projects',
    label: 'Projects',
    icon: FolderIcon,
    href: '/projects',
  },
  {
    id: 'designer',
    label: 'Designer',
    icon: MapIcon,
    href: '/designer',
  },
  {
    id: 'survey',
    label: 'Survey',
    icon: ClipboardDocumentListIcon,
    href: '/survey',
  },
  {
    id: 'construction',
    label: 'Construction',
    icon: WrenchScrewdriverIcon,
    href: '/construction',
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: DocumentChartBarIcon,
    href: '/reports',
  },
];

const bottomNavItems: NavigationItem[] = [
  {
    id: 'settings',
    label: 'Settings',
    icon: CogIcon,
    href: '/settings',
  },
  {
    id: 'help',
    label: 'Help',
    icon: QuestionMarkCircleIcon,
    href: '/help',
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed = false, 
  onToggle 
}) => {
  const location = useLocation();

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  const NavItem: React.FC<{ item: NavigationItem }> = ({ item }) => (
    <Link
      to={item.href}
      className={`
        group relative flex items-center gap-3 px-3 py-2 mx-2 rounded-md transition-colors
        ${isActive(item.href) 
          ? 'bg-lasomi-primary text-text-primary' 
          : 'text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary'
        }
        ${collapsed ? 'justify-center' : ''}
      `}
      title={collapsed ? item.label : undefined}
    >
      <item.icon className="w-5 h-5 flex-shrink-0" />
      {!collapsed && (
        <span className="text-sm font-medium">{item.label}</span>
      )}
      {item.badge && !collapsed && (
        <span className="ml-auto bg-danger text-white text-xs px-2 py-0.5 rounded-full">
          {item.badge}
        </span>
      )}

      {/* Tooltip for collapsed state */}
      {collapsed && (
        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap">
          {item.label}
        </div>
      )}
    </Link>
  );

  return (
    <aside className={`sidebar transition-all duration-300 ${collapsed ? 'w-16' : 'w-280'}`}>
      {/* Navigation */}
      <nav className="flex-1 py-4 space-y-1">
        {navigationItems.map((item) => (
          <NavItem key={item.id} item={item} />
        ))}
      </nav>

      {/* Bottom navigation */}
      <div className="border-t border-border py-4 space-y-1">
        {bottomNavItems.map((item) => (
          <NavItem key={item.id} item={item} />
        ))}
      </div>

      {/* Collapse toggle */}
      {!collapsed && (
        <div className="p-4 border-t border-border">
          <button
            onClick={onToggle}
            className="w-full text-xs text-text-secondary hover:text-text-primary transition-colors"
          >
            Collapse sidebar
          </button>
        </div>
      )}
    </aside>
  );
};
