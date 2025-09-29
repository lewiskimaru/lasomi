# Lasomi Project Structure 🏗️

## Overview
This document outlines the organized file structure for the Lasomi telecom project lifecycle platform. The structure is designed for scalability, maintainability, and follows React best practices.

## 📁 Current Project Structure

```
src/react-app/
├── components/                    # All reusable components
│   ├── ui/                       # Generic UI components (Button, Card, etc.)
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── index.ts
│   │
│   ├── layout/                   # Layout-related components
│   │   ├── AppLayout.tsx
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── TopBar.tsx
│   │   └── index.ts
│   │
│   ├── common/                   # Shared components across features
│   │   ├── WelcomeMessage.tsx
│   │   ├── StorageStatus.tsx
│   │   └── index.ts
│   │
│   ├── dashboard/                # Dashboard-specific components
│   │   ├── AppGrid.tsx
│   │   ├── StatsCard.tsx
│   │   └── index.ts
│   │
│   ├── survey/                   # Survey feature components
│   │   └── index.ts
│   │
│   ├── designer/                 # Designer feature components
│   │   └── index.ts
│   │
│   ├── fiber/                    # Fiber (FTTH/FTTB) components
│   │   └── index.ts
│   │
│   └── index.ts                  # Main components export
│
├── pages/                        # Page components organized by feature
│   ├── dashboard/                # Dashboard pages
│   │   ├── Dashboard.tsx
│   │   ├── Home.tsx
│   │   └── index.ts
│   │
│   ├── survey/                   # Survey feature pages
│   │   ├── Survey.tsx
│   │   └── index.ts
│   │
│   ├── designer/                 # Designer feature pages
│   │   ├── Designer.tsx
│   │   ├── FeatureExtraction.tsx
│   │   └── index.ts
│   │
│   ├── fiber/                    # Fiber network pages
│   │   ├── FTTB.tsx
│   │   ├── FTTH.tsx
│   │   ├── Accessories.tsx
│   │   └── index.ts
│   │
│   └── projects/                 # Project management pages
│       ├── Projects.tsx
│       └── index.ts
│
├── context/                      # React contexts
│   └── StorageContext.tsx
│
├── hooks/                        # Custom React hooks
│   └── useStorage.ts
│
├── lib/                         # Utility libraries
│   └── storage/
│       ├── database.ts
│       └── localStorage.ts
│
├── App.tsx                      # Main app component
├── main.tsx                     # App entry point
├── index.css                    # Global styles
└── vite-env.d.ts               # Vite type definitions
```

## 🎯 Organization Principles

### 1. **Feature-Based Structure**
- Components and pages are grouped by business feature/module
- Each feature has its own folder with related components
- Promotes separation of concerns and easier navigation

### 2. **Index Files for Clean Imports**
- Each folder contains an `index.ts` file for clean exports
- Enables importing multiple components from a single path
- Simplifies refactoring and moving components

### 3. **Component Hierarchy**
```
components/
├── ui/           # Generic, reusable UI components
├── layout/       # Layout and navigation components  
├── common/       # Shared business components
└── {feature}/    # Feature-specific components
```

### 4. **Import Patterns**

#### ✅ Recommended Import Styles:
```typescript
// Feature imports
import Dashboard from '@/react-app/pages/dashboard';
import { AppGrid, StatsCard } from '@/react-app/components/dashboard';

// UI component imports
import { Button, Card, LoadingSpinner } from '@/react-app/components/ui';

// Layout imports
import { AppLayout, Sidebar } from '@/react-app/components/layout';
```

#### ❌ Avoid These Imports:
```typescript
// Don't import from deep paths
import Dashboard from '@/react-app/pages/dashboard/Dashboard';

// Don't import everything from index
import * as Components from '@/react-app/components';
```

## 🚀 Benefits of This Structure

### 1. **Maintainability**
- Easy to locate components related to specific features
- Clear separation between generic UI and business logic
- Reduced coupling between different parts of the application

### 2. **Scalability**
- New features can be added as separate folders
- Components can be moved between folders without breaking imports
- Team members can work on different features independently

### 3. **Reusability**
- UI components are clearly separated and reusable
- Feature components can be easily identified and reused
- Common patterns are abstracted into shared components

### 4. **Developer Experience**
- Intuitive file organization
- Clean import statements
- Easy code navigation with modern IDEs
- Clear ownership of components

## 📝 Adding New Features

### When Adding a New Feature Module:

1. **Create the folder structure:**
```bash
mkdir src/react-app/pages/new-feature
mkdir src/react-app/components/new-feature
```

2. **Create the main page component:**
```typescript
// src/react-app/pages/new-feature/NewFeature.tsx
export default function NewFeature() {
  return <div>New Feature Page</div>;
}
```

3. **Create the index file:**
```typescript
// src/react-app/pages/new-feature/index.ts
export { default } from './NewFeature';
```

4. **Add to App.tsx routing:**
```typescript
import NewFeature from '@/react-app/pages/new-feature';
// Add route...
```

### When Adding Reusable Components:

- **Generic UI components** → `src/react-app/components/ui/`
- **Feature-specific components** → `src/react-app/components/{feature}/`
- **Shared business components** → `src/react-app/components/common/`

## 🔧 Development Tips

1. **Use absolute imports** with the `@/` alias for consistency
2. **Always create index files** for folders with multiple exports
3. **Group related components** in the same feature folder
4. **Keep UI components generic** and feature-agnostic
5. **Use TypeScript interfaces** for component props consistently

## 🎨 Styling Organization

- **Global styles**: `src/react-app/index.css`
- **Component styles**: Use Tailwind CSS classes directly in components
- **Theme configuration**: `tailwind.config.js`

This structure provides a solid foundation for the Lasomi project to grow and scale efficiently! 🚀