import React from 'react';
import { 
  BookOpenIcon, 
  PlayIcon, 
  DocumentTextIcon,
  AcademicCapIcon,
  ClockIcon,
  UserGroupIcon 
} from '@heroicons/react/24/outline';

const Learn: React.FC = () => {
  const learningResources = [
    {
      id: 1,
      title: 'Getting Started with Lasomi',
      description: 'Learn the basics of using the Lasomi platform for telecom projects',
      type: 'tutorial',
      duration: '15 min',
      icon: PlayIcon,
      color: 'bg-blue-500'
    },
    {
      id: 2,
      title: 'Feature Extraction Guide',
      description: 'Master automatic building and road extraction from satellite imagery',
      type: 'guide',
      duration: '30 min',
      icon: DocumentTextIcon,
      color: 'bg-green-500'
    },
    {
      id: 3,
      title: 'FTTH Network Design',
      description: 'Complete course on fiber-to-the-home network planning',
      type: 'course',
      duration: '2 hrs',
      icon: AcademicCapIcon,
      color: 'bg-purple-500'
    },
    {
      id: 4,
      title: 'Survey Best Practices',
      description: 'Field survey techniques and data collection standards',
      type: 'best-practices',
      duration: '45 min',
      icon: BookOpenIcon,
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Learn</h1>
          <p className="text-lg text-gray-600">
            Training materials and documentation to master the Lasomi platform
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpenIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Resources</p>
                <p className="text-2xl font-bold text-gray-900">24</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Hours</p>
                <p className="text-2xl font-bold text-gray-900">12</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Learners</p>
                <p className="text-2xl font-bold text-gray-900">156</p>
              </div>
            </div>
          </div>
        </div>

        {/* Learning Resources */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {learningResources.map((resource) => {
            const Icon = resource.icon;
            return (
              <div 
                key={resource.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200 cursor-pointer"
              >
                <div className="p-6">
                  <div className="flex items-center mb-4">
                    <div className={`flex-shrink-0 p-2 rounded-lg ${resource.color}`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                        {resource.type.replace('-', ' ')}
                      </span>
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {resource.title}
                  </h3>
                  
                  <p className="text-gray-600 text-sm mb-4">
                    {resource.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      {resource.duration}
                    </span>
                    <button className="text-blue-600 text-sm font-medium hover:text-blue-500">
                      Start Learning →
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Coming Soon Section */}
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8 text-center">
          <AcademicCapIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">More Learning Content Coming Soon</h3>
          <p className="text-gray-600 mb-4">
            We're continuously adding new tutorials, guides, and courses to help you master telecom infrastructure planning.
          </p>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Request a Topic
          </button>
        </div>
      </div>
    </div>
  );
};

export default Learn;