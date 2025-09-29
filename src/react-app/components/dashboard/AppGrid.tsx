import React from 'react';
import { Link } from 'react-router-dom';

interface AppCard {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  color: string;
}

interface AppGridProps {
  apps: AppCard[];
  className?: string;
}

const AppGrid: React.FC<AppGridProps> = ({ apps, className = '' }) => {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${className}`}>
      {apps.map((app) => {
        const Icon = app.icon;
        return (
          <Link 
            key={app.id}
            to={app.href}
            className="group relative overflow-hidden rounded-2xl bg-white border border-gray-200 shadow-sm hover:shadow-lg transition-all duration-300 transform hover:scale-105"
          >
            <div className="p-6">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${app.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{app.title}</h3>
              <p className="text-sm text-gray-600 line-clamp-2">{app.description}</p>
            </div>
            
            {/* Hover effect overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-transparent to-black/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </Link>
        );
      })}
    </div>
  );
};

export default AppGrid;