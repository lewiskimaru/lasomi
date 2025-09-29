import React, { useState } from 'react';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  FolderIcon,
  CalendarIcon,
  UserIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';
import type { Project } from '@/shared/types';

interface ProjectCardProps {
  project: Project;
  onSelect: (project: Project) => void;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  onSelect, 
  onEdit, 
  onDelete 
}) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="card hover:shadow-lasomi-lg transition-shadow cursor-pointer group">
      <div className="p-6" onClick={() => onSelect(project)}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-lasomi-primary rounded-md flex items-center justify-center">
              <FolderIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-text-primary">{project.name}</h3>
              <p className="text-sm text-text-secondary">
                {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
              </p>
            </div>
          </div>
          
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-1 text-text-secondary hover:text-text-primary rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <EllipsisVerticalIcon className="w-5 h-5" />
            </button>
            
            {showMenu && (
              <div className="absolute right-0 top-8 w-32 bg-lasomi-card border border-border rounded-md shadow-lasomi-lg z-10">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(project);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-text-secondary hover:text-text-primary hover:bg-lasomi-secondary"
                >
                  Edit
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(project);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-danger hover:bg-red-600 hover:text-white"
                >
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2 text-text-secondary">
            <UserIcon className="w-4 h-4" />
            <span>{project.owner || 'Unassigned'}</span>
          </div>
          <div className="flex items-center gap-2 text-text-secondary">
            <CalendarIcon className="w-4 h-4" />
            <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function Projects() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);

  // Mock data - replace with actual API call
  const [projects] = useState<Project[]>([
    {
      id: 1,
      name: 'Downtown Fiber Network',
      owner: 'John Smith',
      status: 'active',
      meta: JSON.stringify({ region: 'downtown', priority: 'high' }),
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-20T15:30:00Z',
    },
    {
      id: 2,
      name: 'Residential FTTH Phase 1',
      owner: 'Sarah Johnson',
      status: 'active',
      meta: JSON.stringify({ region: 'suburbs', priority: 'medium' }),
      created_at: '2024-01-10T08:00:00Z',
      updated_at: '2024-01-18T12:00:00Z',
    },
    {
      id: 3,
      name: 'Industrial Park Network',
      owner: 'Mike Wilson',
      status: 'draft',
      meta: JSON.stringify({ region: 'industrial', priority: 'low' }),
      created_at: '2024-01-05T14:00:00Z',
      updated_at: '2024-01-05T14:00:00Z',
    },
  ]);

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (project.owner && project.owner.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleSelectProject = (project: Project) => {
    console.log('Selected project:', project);
    // TODO: Navigate to project dashboard
  };

  const handleEditProject = (project: Project) => {
    console.log('Edit project:', project);
    // TODO: Open edit modal
  };

  const handleDeleteProject = (project: Project) => {
    console.log('Delete project:', project);
    // TODO: Show confirmation dialog
  };

  const handleNewProject = () => {
    setShowNewProjectModal(true);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Projects</h1>
          <p className="text-text-secondary">Manage your telecom infrastructure projects</p>
        </div>
        
        <button
          onClick={handleNewProject}
          className="btn btn-primary"
        >
          <PlusIcon className="w-4 h-4" />
          New Project
        </button>
      </div>

      {/* Search and filters */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1 max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-secondary" />
          <input
            type="text"
            placeholder="Search projects..."
            className="form-input pl-10 w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <select className="form-input">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="draft">Draft</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Projects grid */}
      {filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onSelect={handleSelectProject}
              onEdit={handleEditProject}
              onDelete={handleDeleteProject}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <FolderIcon className="w-12 h-12 text-text-secondary mx-auto mb-4" />
          <h3 className="text-lg font-medium text-text-primary mb-2">No projects found</h3>
          <p className="text-text-secondary mb-4">
            {searchQuery ? 'Try adjusting your search criteria' : 'Get started by creating your first project'}
          </p>
          {!searchQuery && (
            <button
              onClick={handleNewProject}
              className="btn btn-primary"
            >
              <PlusIcon className="w-4 h-4" />
              Create Project
            </button>
          )}
        </div>
      )}

      {/* TODO: Add New Project Modal */}
      {showNewProjectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-lasomi-card border border-border rounded-lg shadow-lasomi-lg w-full max-w-md">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-text-primary mb-4">Create New Project</h2>
              {/* Add form fields here */}
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowNewProjectModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button className="btn btn-primary">
                  Create Project
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
