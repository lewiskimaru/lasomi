# TreeView Component

A flexible, animated tree view component for displaying hierarchical data structures with full keyboard and mouse support.

## Features

- 🎨 Smooth animations with Framer Motion
- 🎯 Single and multi-selection support
- 🎪 Customizable icons and styling
- 📱 Keyboard navigation support
- 🔄 Controlled and uncontrolled modes
- 🎭 Tree lines and visual hierarchy
- ⚡ High performance with large datasets

## Installation

The TreeView component is already installed and available in the UI components. It requires:

- `framer-motion` - For animations
- `lucide-react` - For default icons
- `tailwind-merge` & `clsx` - For className utilities

## Basic Usage

```tsx
import { TreeView, TreeNode } from '@/react-app/components/ui';

const treeData: TreeNode[] = [
  {
    id: 'network-design',
    label: 'Network Design Project',
    children: [
      {
        id: 'poles',
        label: 'Poles',
        children: [
          { id: 'poles-new', label: 'New Poles' },
          { id: 'poles-existing', label: 'Existing Poles' }
        ]
      },
      {
        id: 'cables',
        label: 'Fiber Cables',
        children: [
          { id: 'cables-48c', label: '48C ADSS' },
          { id: 'cables-96c', label: '96C ADSS' }
        ]
      }
    ]
  }
];

function MyComponent() {
  return (
    <TreeView
      data={treeData}
      onNodeClick={(node) => console.log('Clicked:', node.label)}
      defaultExpandedIds={['network-design']}
    />
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `TreeNode[]` | - | **Required.** Array of tree nodes |
| `onNodeClick` | `(node: TreeNode) => void` | - | Callback when a node is clicked |
| `onNodeExpand` | `(nodeId: string, expanded: boolean) => void` | - | Callback when node expand state changes |
| `defaultExpandedIds` | `string[]` | `[]` | IDs of nodes that should be expanded by default |
| `showLines` | `boolean` | `true` | Whether to show connecting lines |
| `showIcons` | `boolean` | `true` | Whether to show folder/file icons |
| `selectable` | `boolean` | `true` | Whether nodes can be selected |
| `multiSelect` | `boolean` | `false` | Allow multiple node selection |
| `selectedIds` | `string[]` | `[]` | Controlled selected node IDs |
| `onSelectionChange` | `(ids: string[]) => void` | - | Callback for selection changes (controlled mode) |
| `indent` | `number` | `20` | Indentation per level in pixels |
| `animateExpand` | `boolean` | `true` | Whether to animate expand/collapse |
| `className` | `string` | - | Additional CSS classes |

## TreeNode Interface

```tsx
type TreeNode = {
  id: string;           // Unique identifier
  label: string;        // Display text
  icon?: React.ReactNode; // Custom icon (optional)
  children?: TreeNode[]; // Child nodes (optional)
  data?: any;           // Additional data (optional)
};
```

## Examples

### Custom Icons

```tsx
import { Building, Cable, Zap } from 'lucide-react';

const dataWithIcons: TreeNode[] = [
  {
    id: 'infrastructure',
    label: 'Infrastructure',
    icon: <Building className="w-4 h-4" />,
    children: [
      {
        id: 'power',
        label: 'Power Systems',
        icon: <Zap className="w-4 h-4" />
      },
      {
        id: 'network',
        label: 'Network Cables', 
        icon: <Cable className="w-4 h-4" />
      }
    ]
  }
];
```

### Controlled Selection

```tsx
function ControlledTreeView() {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  
  return (
    <TreeView
      data={treeData}
      selectedIds={selectedIds}
      onSelectionChange={setSelectedIds}
      multiSelect={true}
    />
  );
}
```

### Compact Style

```tsx
<TreeView
  data={treeData}
  showLines={false}
  indent={12}
  className="text-sm"
/>
```

## Use Cases in Lasomi

The TreeView is particularly useful for:

1. **HLD Upload**: Displaying uploaded design file structure
2. **Layer Management**: Managing map layers and visibility
3. **Project Structure**: Showing project hierarchies  
4. **Network Topology**: Displaying network component trees
5. **File Browsers**: Any hierarchical file/data structure

## Styling

The component uses Tailwind CSS and respects the Lasomi theme colors. It automatically adapts to dark/light mode and uses semantic color variables.

## Performance

- Virtualization is not built-in, but the component handles up to ~1000 nodes efficiently
- For very large datasets, consider implementing pagination or search filtering
- Animations can be disabled for better performance with `animateExpand={false}`