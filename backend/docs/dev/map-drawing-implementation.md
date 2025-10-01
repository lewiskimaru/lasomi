# Map Drawing Features Implementation Guide

## Overview

The Features page (`/features`) implements an advanced map drawing system that allows users to define Areas of Interest (AOI) using polygon and rectangle drawing tools. The system provides sophisticated visual feedback, interactive vertex editing, and a seamless user experience for geographic area selection.

## Core Features

### 1. Interactive Drawing Tools

The map provides two primary drawing modes:

#### Polygon Drawing
- **Activation**: Click the polygon tool button to enter polygon drawing mode
- **Drawing Process**: 
  - Click anywhere on the map to place the first vertex (start point)
  - Continue clicking to add additional vertices
  - Complete the polygon by clicking on the start vertex or when vertices are close enough
- **Minimum Requirements**: Polygons must have at least 3 vertices to be valid
- **Cancellation**: Press ESC key to cancel drawing at any time

#### Rectangle Drawing  
- **Activation**: Click the rectangle tool button to enter rectangle drawing mode
- **Drawing Process**:
  - Click and drag on the map to define the rectangle bounds
  - Release mouse to complete the rectangle
- **Immediate Completion**: Rectangles are completed as soon as the mouse is released

### 2. Visual Feedback System

The drawing system provides rich visual feedback through multiple indicator types:

#### Start Vertex Indicator
- **Appearance**: Circular marker with a "+" symbol inside
- **Purpose**: Marks the first vertex of a polygon and serves as the completion target
- **Behavior**: 
  - Always displays a "+" symbol by default
  - Shows a "✓" symbol when hovering (only when polygon has 3+ vertices)
  - Clicking completes the polygon when it has sufficient vertices

#### Regular Vertex Indicators
- **Appearance**: Smaller circular markers with "+" symbols
- **Purpose**: Shows placed vertices during polygon drawing
- **Color Scheme**: Orange border with white background
- **Interactive**: Non-interactive during drawing phase

#### Ghost Vertex Indicator
- **Appearance**: Dashed circular marker that follows the mouse cursor
- **Purpose**: Shows where the next vertex would be placed
- **Behavior**:
  - Appears only during active polygon drawing
  - Follows mouse movement across the map
  - Updates the temporary drawing line in real-time
  - Helps users visualize the polygon shape before placing vertices

#### Temporary Drawing Lines
- **Polygon Mode**: Dashed orange line connecting all placed vertices plus the ghost vertex
- **Rectangle Mode**: Solid orange rectangle outline that updates as the mouse moves
- **Purpose**: Provides real-time preview of the shape being drawn

### 3. Shape Editing System

Once a shape is completed, it becomes editable through vertex manipulation:

#### Draggable Vertices
- **Activation**: Automatically enabled when a shape is completed
- **Appearance**: Small circular markers at each vertex/corner
- **Functionality**:
  - Click and drag to reposition vertices
  - Real-time shape updates as vertices are moved
  - Hover effects to indicate interactivity
  - State preservation during editing

#### Visual States
- **Default State**: Small orange-bordered circles with white centers
- **Hover State**: Larger markers with light orange background
- **Drag State**: Active visual feedback during dragging operations

### 4. Map Layer Management

The system includes comprehensive map layer switching:

#### Available Map Types
- **Satellite Views**: Google Satellite, Google Hybrid, Esri World Imagery  
- **Street Maps**: OpenStreetMap, Google Streets, CartoDB Light
- **Terrain Maps**: OpenTopoMap, Google Terrain

#### Layer Selector
- **Location**: Top-right corner of the map
- **Activation**: Click the layers icon to open the selector
- **Organization**: Grouped by map type (satellite, street, terrain)
- **Persistence**: Selected layer is maintained across drawing operations

### 5. State Management

The drawing system maintains comprehensive state:

#### Drawing State
- **Active Tool**: Tracks which drawing tool is currently active
- **Drawing Progress**: Monitors current drawing operation status
- **Shape Data**: Stores coordinates and geometric properties of completed shapes

#### Area Information
- **Coordinates**: Displays center point of the defined area
- **Bounds**: Calculates and stores geographic boundaries
- **Area Calculation**: Computes area measurements for completed shapes

### 6. User Interface Integration

#### Control Layout
- **Drawing Tools**: Horizontal toolbar in top-left corner
- **Layer Selector**: Icon button in top-right corner  
- **Shape Information**: Displayed in the side panel
- **Status Feedback**: Toast notifications for user actions

#### Visual Hierarchy
- **Primary Actions**: Drawing tools prominently displayed
- **Secondary Actions**: Layer switching accessible but not prominent
- **Information Display**: Clear presentation of area details
- **Status Updates**: Non-intrusive notifications

## Technical Architecture

### Drawing Implementation Approach

The system uses a custom drawing implementation rather than relying solely on mapping library defaults:

#### Custom Polygon Drawing
- **Event Handling**: Direct map click event management
- **State Tracking**: Manual vertex collection and validation
- **Visual Updates**: Real-time polyline and marker updates
- **Completion Logic**: Custom logic for detecting shape completion

#### Enhanced Rectangle Drawing
- **Mouse Events**: Coordinated mousedown/mousemove/mouseup handling  
- **Real-time Preview**: Dynamic rectangle bounds updates
- **Instant Completion**: Immediate finalization on mouse release

### Visual Component Strategy

#### Marker Customization
- **Custom Icons**: HTML-based markers for precise visual control
- **State-Driven Styling**: Dynamic styling based on interaction state
- **Consistent Design**: Unified visual language across all markers

#### Drawing Layers
- **Separation of Concerns**: Temporary vs. permanent shape layers
- **Z-Index Management**: Proper layering for interactive elements
- **Performance Optimization**: Efficient adding/removing of temporary elements

### Interaction Design Principles

#### Progressive Disclosure
- **Tool Activation**: Clear indication of active drawing mode
- **Visual Feedback**: Immediate response to user actions
- **Completion Guidance**: Clear indicators for finishing shapes

#### Error Prevention
- **Minimum Requirements**: Enforcement of shape validity rules
- **Visual Cues**: Clear indication of required actions
- **Cancellation Options**: ESC key support for operation cancellation

#### Intuitive Controls
- **Familiar Patterns**: Standard drawing interaction patterns
- **Visual Affordances**: Clear indication of interactive elements  
- **Immediate Feedback**: Real-time response to user input

## Usage Patterns

### Typical Workflow

1. **Tool Selection**: User selects polygon or rectangle drawing tool
2. **Area Definition**: User draws the desired area on the map
3. **Shape Completion**: System detects completion and finalizes the shape
4. **Fine-tuning**: User adjusts vertices as needed through dragging
5. **Analysis Preparation**: System captures area data for processing

### Best Practices

#### For Users
- **Precise Placement**: Use the ghost vertex indicator for accurate placement
- **Efficient Completion**: Click the start vertex to quickly finish polygons
- **Post-Draw Editing**: Use vertex dragging for fine adjustments
- **Layer Selection**: Choose appropriate map layer for better visibility

#### For Implementation
- **Visual Consistency**: Maintain consistent styling across all drawing elements
- **Performance Awareness**: Clean up temporary elements promptly
- **State Management**: Ensure drawing state is properly maintained
- **User Feedback**: Provide clear indication of system status

## Integration Points

### External Systems
- **Backend Communication**: Area data formatted for analysis services
- **Data Sources**: Integration with multiple geographic data providers
- **File Upload**: Coordination with design file upload functionality

### Component Architecture  
- **Map Component**: Reusable map drawing functionality
- **Features Page**: Specific implementation with AOI requirements
- **State Management**: Session-based state persistence
- **Activity Logging**: Comprehensive user action tracking

This implementation provides a robust, user-friendly system for defining geographic areas with sophisticated visual feedback and editing capabilities, suitable for professional GIS applications and analysis workflows.