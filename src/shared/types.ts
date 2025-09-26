import z from "zod";

/**
 * Core data types for Lasomi telecom project lifecycle platform
 */

// Project management schemas
export const ProjectSchema = z.object({
  id: z.number(),
  name: z.string(),
  owner: z.string().optional(),
  meta: z.string().optional(), // JSON metadata
  status: z.enum(['active', 'archived', 'draft']).default('active'),
  created_at: z.string(),
  updated_at: z.string(),
});

export const AOISchema = z.object({
  id: z.number(),
  project_id: z.number(),
  name: z.string().optional(),
  polygon: z.string(), // GeoJSON polygon
  status: z.enum(['draft', 'processing', 'completed', 'error']).default('draft'),
  source_kmz: z.string().optional(),
  area_km2: z.number().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

// Geospatial feature schemas
export const BuildingSchema = z.object({
  id: z.number(),
  aoi_id: z.number(),
  geom: z.string(), // GeoJSON polygon
  centroid: z.string().optional(), // GeoJSON point
  source: z.enum(['microsoft', 'google', 'osm']),
  source_id: z.string().optional(),
  confidence: z.number().min(0).max(1).default(0),
  building_type: z.string().optional(),
  tenants: z.number().default(1),
  height_m: z.number().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const RoadSchema = z.object({
  id: z.number(),
  aoi_id: z.number(),
  geom: z.string(), // GeoJSON linestring
  name: z.string().optional(),
  road_type: z.string().optional(),
  source: z.string(),
  source_id: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const PoleSchema = z.object({
  id: z.number(),
  aoi_id: z.number(),
  geom: z.string(), // GeoJSON point
  height_m: z.number().default(10.0),
  pole_type: z.enum(['utility', 'fiber', 'distribution']).default('utility'),
  equipment_json: z.string().optional(), // JSON equipment details
  status: z.enum(['planned', 'installed', 'active']).default('planned'),
  created_at: z.string(),
  updated_at: z.string(),
});

export const AccessorySchema = z.object({
  id: z.number(),
  pole_id: z.number(),
  code: z.string(),
  description: z.string().optional(),
  quantity: z.number().default(1),
  rule_id: z.number().optional(),
  reason: z.string().optional(),
  unit_cost: z.number().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

// Infrastructure schemas
export const ClusterSchema = z.object({
  id: z.number(),
  aoi_id: z.number(),
  dp_location: z.string(), // GeoJSON point for distribution point
  member_buildings: z.string(), // JSON array of building IDs
  total_tenants: z.number().default(0),
  recommended_split: z.boolean().default(false),
  cluster_type: z.enum(['FTTH', 'FTTB', 'FTTS']).default('FTTH'),
  created_at: z.string(),
  updated_at: z.string(),
});

export const AttachmentSchema = z.object({
  id: z.number(),
  entity_type: z.string(),
  entity_id: z.number(),
  url: z.string(),
  file_type: z.string().optional(),
  metadata: z.string().optional(), // JSON metadata
  size_bytes: z.number().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

// Rule engine schemas
export const RuleProfileSchema = z.object({
  id: z.number(),
  name: z.string(),
  rules_json: z.string(), // JSON rules configuration
  project_id: z.number().optional(),
  is_default: z.boolean().default(false),
  created_at: z.string(),
  updated_at: z.string(),
});

// Export schemas
export const ExportSchema = z.object({
  id: z.number(),
  aoi_id: z.number(),
  export_type: z.enum(['kmz', 'geojson', 'csv', 'pdf', 'excel']),
  file_url: z.string().optional(),
  meta: z.string().optional(), // JSON metadata
  status: z.enum(['pending', 'processing', 'completed', 'error']).default('pending'),
  created_at: z.string(),
  updated_at: z.string(),
});

// Audit schema
export const AuditLogSchema = z.object({
  id: z.number(),
  user_id: z.string().optional(),
  action: z.string(),
  entity_type: z.string().optional(),
  entity_id: z.number().optional(),
  details: z.string().optional(), // JSON details
  timestamp: z.string(),
});

// Derived TypeScript types
export type Project = z.infer<typeof ProjectSchema>;
export type AOI = z.infer<typeof AOISchema>;
export type Building = z.infer<typeof BuildingSchema>;
export type Road = z.infer<typeof RoadSchema>;
export type Pole = z.infer<typeof PoleSchema>;
export type Accessory = z.infer<typeof AccessorySchema>;
export type Cluster = z.infer<typeof ClusterSchema>;
export type Attachment = z.infer<typeof AttachmentSchema>;
export type RuleProfile = z.infer<typeof RuleProfileSchema>;
export type Export = z.infer<typeof ExportSchema>;
export type AuditLog = z.infer<typeof AuditLogSchema>;

// UI-specific types
export interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface MapState {
  center: [number, number];
  zoom: number;
  bounds?: MapBounds;
}

export interface AOIDrawingState {
  isDrawing: boolean;
  drawingMode: 'polygon' | 'rectangle' | null;
  currentAOI?: {
    polygon: string;
    area: number;
    bounds: MapBounds;
  };
}

export interface DataSource {
  id: string;
  name: string;
  enabled: boolean;
  description?: string;
}

export interface ProcessingSettings {
  dataSources: {
    microsoft_buildings: DataSource;
    google_buildings: DataSource;
    osm_buildings: DataSource;
    osm_roads: DataSource;
    osm_railways: DataSource;
    osm_landmarks: DataSource;
    osm_natural: DataSource;
  };
  filters: {
    minBuildingArea: number;
    simplificationTolerance: number;
    confidenceThreshold: number;
  };
  outputFormat: 'kmz' | 'geojson' | 'csv';
}

export interface JobStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
  result?: any;
  error?: string;
}

// GeoJSON types for map data
export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Point' | 'LineString' | 'Polygon' | 'MultiPolygon';
    coordinates: number[] | number[][] | number[][][];
  };
  properties: {
    [key: string]: any;
  };
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

// API response types
export interface APIResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// Navigation types
export interface NavigationItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  active?: boolean;
  badge?: string | number;
}

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'file' | 'textarea';
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: string | number }[];
  validation?: z.ZodSchema;
}
