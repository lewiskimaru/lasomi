# API Integration Guide

## Overview

This guide provides comprehensive documentation for integrating the React frontend with the Atlas GIS API, including TypeScript types, service functions, error handling, and real-time updates.

## API Structure

### Base Configuration
```typescript
// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || '/api/v2',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

export const ENDPOINTS = {
  // Core endpoints
  EXTRACT_DATA: '/extract-data',
  VALIDATE_AOI: '/validate-aoi',
  DATA_SOURCES: '/data-sources',
  DOWNLOAD: '/download',
  
  // Design upload endpoints
  UPLOAD_DESIGN: '/design/upload',
  RENDER_DESIGN: '/design/render',
  
  // Health and status
  HEALTH: '/health',
  JOB_STATUS: '/job/{jobId}/status',
} as const;
```

## TypeScript Type Definitions

### Core API Types
```typescript
// src/types/api.ts

// Geometric types
export interface Coordinates {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface BoundingBox {
  north: number;
  south: number;
  east: number;
  west: number;
}

// Data source types
export enum DataSourceType {
  MICROSOFT_BUILDINGS = 'microsoft_buildings',
  GOOGLE_BUILDINGS = 'google_buildings',
  OSM_BUILDINGS = 'osm_buildings',
  OSM_ROADS = 'osm_roads',
  OSM_RAILWAYS = 'osm_railways',
  OSM_LANDMARKS = 'osm_landmarks',
  OSM_NATURAL = 'osm_natural',
}

export interface DataSourceSelection {
  enabled: boolean;
  timeout?: number;
}

export interface DataSourcesConfig {
  [DataSourceType.MICROSOFT_BUILDINGS]?: DataSourceSelection;
  [DataSourceType.GOOGLE_BUILDINGS]?: DataSourceSelection;
  [DataSourceType.OSM_BUILDINGS]?: DataSourceSelection;
  [DataSourceType.OSM_ROADS]?: DataSourceSelection;
  [DataSourceType.OSM_RAILWAYS]?: DataSourceSelection;
  [DataSourceType.OSM_LANDMARKS]?: DataSourceSelection;
  [DataSourceType.OSM_NATURAL]?: DataSourceSelection;
}

// Request/Response types
export interface ExtractDataRequest {
  aoi_boundary: Coordinates;
  data_sources: DataSourcesConfig;
  output_format?: 'geojson' | 'kml' | 'kmz' | 'csv';
  raw?: boolean;
  filters?: {
    min_building_area?: number;
    road_types?: string[];
    simplification_tolerance?: number;
    google_confidence?: number;
    osm_min_area?: number;
    min_width?: number;
    min_compactness?: number;
    max_elongation?: number;
  };
}

export interface ExtractDataResponse {
  job_id: string;
  status: 'processing' | 'completed' | 'failed' | 'partial';
  total_features: number;
  processing_time?: number;
  output_format?: string;
  data?: string; // Base64 encoded data when raw=true
  export_urls: {
    geojson?: string;
    kml?: string;
    kmz?: string;
    csv?: string;
  };
  results: {
    [key in DataSourceType]?: {
      status: 'success' | 'failed' | 'timeout';
      feature_count: number;
      error_message?: string;
      processing_time: number;
    };
  };
  metadata?: {
    aoi_area_km2: number;
    processing_started: string;
    processing_completed: string;
  };
}

// Design upload types
export interface DesignUploadResponse {
  design_id: string;
  status: 'processed' | 'failed';
  metadata: {
    filename: string;
    file_size: number;
    feature_count: number;
    layer_count: number;
    center: [number, number];
    bounds: BoundingBox;
  };
  map_center: [number, number];
  map_zoom: number;
  layers: DesignLayer[];
  processing_time: number;
}

export interface DesignLayer {
  id: string;
  name: string;
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon';
  feature_count: number;
  style?: {
    color?: string;
    fillColor?: string;
    opacity?: number;
    weight?: number;
  };
}

// Job status types
export interface JobStatus {
  job_id: string;
  status: 'processing' | 'completed' | 'failed' | 'partial';
  progress?: number;
  current_step?: string;
  total_steps?: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

// Data sources info
export interface DataSourceInfo {
  id: DataSourceType;
  name: string;
  description: string;
  available: boolean;
  supported_features: string[];
  rate_limit?: {
    requests_per_minute: number;
    requests_per_hour: number;
  };
  capabilities: {
    buildings: boolean;
    roads: boolean;
    landmarks: boolean;
    natural: boolean;
  };
}

// Error types
export interface APIError {
  detail: string;
  error_code?: string;
  validation_errors?: Record<string, string[]>;
}
```

## API Service Implementation

### Base API Client
```typescript
// src/services/apiClient.ts
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { API_CONFIG } from '@/config/api';

export class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add timestamp for debugging
        config.metadata = { startTime: new Date() };
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log response time for debugging
        const endTime = new Date();
        const duration = endTime.getTime() - response.config.metadata.startTime.getTime();
        console.debug(`API call ${response.config.url} took ${duration}ms`);
        return response;
      },
      (error: AxiosError) => {
        return Promise.reject(this.handleAPIError(error));
      }
    );
  }

  private handleAPIError(error: AxiosError): APIError {
    if (error.response?.data) {
      return error.response.data as APIError;
    }
    
    if (error.code === 'ECONNABORTED') {
      return { detail: 'Request timeout. Please try again.' };
    }
    
    if (!error.response) {
      return { detail: 'Network error. Please check your connection.' };
    }
    
    return { detail: 'An unexpected error occurred.' };
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const apiClient = new APIClient();
```

### Atlas API Service
```typescript
// src/services/atlasAPI.ts
import { apiClient } from './apiClient';
import { ENDPOINTS } from '@/config/api';
import type {
  ExtractDataRequest,
  ExtractDataResponse,
  JobStatus,
  DataSourceInfo,
  DesignUploadResponse,
  BoundingBox,
} from '@/types/api';

export class AtlasAPIService {
  // Extract geospatial data
  async extractData(request: ExtractDataRequest): Promise<ExtractDataResponse> {
    return apiClient.post<ExtractDataResponse>(ENDPOINTS.EXTRACT_DATA, request);
  }

  // Validate Area of Interest
  async validateAOI(coordinates: any): Promise<{ valid: boolean; area_km2?: number; message?: string }> {
    return apiClient.post(ENDPOINTS.VALIDATE_AOI, { aoi_boundary: coordinates });
  }

  // Get available data sources
  async getDataSources(): Promise<DataSourceInfo[]> {
    return apiClient.get<DataSourceInfo[]>(ENDPOINTS.DATA_SOURCES);
  }

  // Get job status
  async getJobStatus(jobId: string): Promise<JobStatus> {
    const url = ENDPOINTS.JOB_STATUS.replace('{jobId}', jobId);
    return apiClient.get<JobStatus>(url);
  }

  // Download results
  async downloadResults(jobId: string, format: string): Promise<Blob> {
    const url = `${ENDPOINTS.DOWNLOAD}/${jobId}/${format}`;
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });
    return response as unknown as Blob;
  }

  // Upload design file
  async uploadDesign(file: File): Promise<DesignUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient.post<DesignUploadResponse>(ENDPOINTS.UPLOAD_DESIGN, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  // Render design layers
  async renderDesign(designId: string, layerIds?: string[]): Promise<any> {
    return apiClient.post(`${ENDPOINTS.RENDER_DESIGN}/${designId}`, {
      layer_ids: layerIds,
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return apiClient.get(ENDPOINTS.HEALTH);
  }
}

export const atlasAPI = new AtlasAPIService();
```

## React Query Integration

### Query Keys
```typescript
// src/hooks/queryKeys.ts
export const queryKeys = {
  // Data sources
  dataSources: ['dataSources'] as const,
  
  // Jobs
  job: (jobId: string) => ['job', jobId] as const,
  jobStatus: (jobId: string) => ['jobStatus', jobId] as const,
  
  // Design
  design: (designId: string) => ['design', designId] as const,
  
  // Health
  health: ['health'] as const,
} as const;
```

### Custom Hooks
```typescript
// src/hooks/useAtlasAPI.ts
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { atlasAPI } from '@/services/atlasAPI';
import { queryKeys } from './queryKeys';
import type { ExtractDataRequest } from '@/types/api';

// Data sources query
export const useDataSources = () => {
  return useQuery(
    queryKeys.dataSources,
    () => atlasAPI.getDataSources(),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );
};

// Extract data mutation
export const useExtractData = () => {
  const queryClient = useQueryClient();

  return useMutation(
    (request: ExtractDataRequest) => atlasAPI.extractData(request),
    {
      onSuccess: (data) => {
        // Cache the job status
        queryClient.setQueryData(
          queryKeys.jobStatus(data.job_id),
          {
            job_id: data.job_id,
            status: data.status,
            started_at: new Date().toISOString(),
          }
        );
      },
    }
  );
};

// Job status query with polling
export const useJobStatus = (jobId: string | null, enabled: boolean = true) => {
  return useQuery(
    queryKeys.jobStatus(jobId!),
    () => atlasAPI.getJobStatus(jobId!),
    {
      enabled: enabled && !!jobId,
      refetchInterval: (data) => {
        // Stop polling when job is complete
        if (data?.status === 'completed' || data?.status === 'failed') {
          return false;
        }
        return 2000; // Poll every 2 seconds
      },
      refetchIntervalInBackground: false,
    }
  );
};

// Design upload mutation
export const useUploadDesign = () => {
  return useMutation(
    (file: File) => atlasAPI.uploadDesign(file),
    {
      onError: (error) => {
        console.error('Design upload failed:', error);
      },
    }
  );
};

// Download results mutation
export const useDownloadResults = () => {
  return useMutation(
    ({ jobId, format }: { jobId: string; format: string }) =>
      atlasAPI.downloadResults(jobId, format),
    {
      onSuccess: (blob, { format }) => {
        // Trigger download
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `atlas_results.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      },
    }
  );
};
```

### Error Handling Hook
```typescript
// src/hooks/useErrorHandler.ts
import { useCallback } from 'react';
import { toast } from 'react-hot-toast';
import type { APIError } from '@/types/api';

export const useErrorHandler = () => {
  const handleError = useCallback((error: APIError | Error) => {
    if ('detail' in error) {
      // API error
      toast.error(error.detail);
      
      if (error.validation_errors) {
        Object.entries(error.validation_errors).forEach(([field, messages]) => {
          messages.forEach(message => {
            toast.error(`${field}: ${message}`);
          });
        });
      }
    } else {
      // Generic error
      toast.error(error.message || 'An unexpected error occurred');
    }
  }, []);

  return { handleError };
};
```

## Real-time Updates

### WebSocket Integration (if implemented)
```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from 'react-query';
import { queryKeys } from './queryKeys';

interface WebSocketMessage {
  type: 'job_status_update' | 'job_completed' | 'job_failed';
  job_id: string;
  data: any;
}

export const useWebSocket = (jobId: string | null) => {
  const [connected, setConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!jobId) return;

    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/job/${jobId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Update React Query cache
      queryClient.setQueryData(
        queryKeys.jobStatus(message.job_id),
        message.data
      );
    };

    ws.current.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [jobId, queryClient]);

  return { connected };
};
```

## Usage Examples

### Complete Data Extraction Flow
```typescript
// src/components/features/DataExtraction.tsx
import { useState } from 'react';
import { useExtractData, useJobStatus, useDownloadResults } from '@/hooks/useAtlasAPI';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import type { ExtractDataRequest } from '@/types/api';

export const DataExtraction = () => {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const { handleError } = useErrorHandler();

  const extractMutation = useExtractData();
  const { data: jobStatus } = useJobStatus(currentJobId, !!currentJobId);
  const downloadMutation = useDownloadResults();

  const handleExtractData = async (request: ExtractDataRequest) => {
    try {
      const result = await extractMutation.mutateAsync(request);
      setCurrentJobId(result.job_id);
    } catch (error) {
      handleError(error as any);
    }
  };

  const handleDownload = async (format: string) => {
    if (!currentJobId) return;
    
    try {
      await downloadMutation.mutateAsync({
        jobId: currentJobId,
        format,
      });
    } catch (error) {
      handleError(error as any);
    }
  };

  return (
    <div>
      {/* Extract button */}
      <button
        onClick={() => handleExtractData(/* your request */)}
        disabled={extractMutation.isLoading}
      >
        {extractMutation.isLoading ? 'Processing...' : 'Extract Data'}
      </button>

      {/* Job status display */}
      {jobStatus && (
        <div>
          <p>Status: {jobStatus.status}</p>
          {jobStatus.progress && (
            <progress value={jobStatus.progress} max={100} />
          )}
        </div>
      )}

      {/* Download button */}
      {jobStatus?.status === 'completed' && (
        <button
          onClick={() => handleDownload('kmz')}
          disabled={downloadMutation.isLoading}
        >
          Download KMZ
        </button>
      )}
    </div>
  );
};
```

### Design Upload Flow
```typescript
// src/components/features/DesignUpload.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useUploadDesign } from '@/hooks/useAtlasAPI';
import { useErrorHandler } from '@/hooks/useErrorHandler';

export const DesignUpload = () => {
  const uploadMutation = useUploadDesign();
  const { handleError } = useErrorHandler();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    try {
      const result = await uploadMutation.mutateAsync(acceptedFiles[0]);
      // Handle successful upload
      console.log('Design uploaded:', result);
    } catch (error) {
      handleError(error as any);
    }
  }, [uploadMutation, handleError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.geojson'],
      'application/vnd.google-earth.kml+xml': ['.kml'],
      'application/vnd.google-earth.kmz': ['.kmz'],
    },
    multiple: false,
  });

  return (
    <div {...getRootProps()} className="dropzone">
      <input {...getInputProps()} />
      {uploadMutation.isLoading ? (
        <p>Uploading...</p>
      ) : isDragActive ? (
        <p>Drop the file here...</p>
      ) : (
        <p>Drag and drop a design file, or click to select</p>
      )}
    </div>
  );
};
```

## Testing API Integration

### Mock API Responses
```typescript
// src/__mocks__/atlasAPI.ts
import type { ExtractDataResponse, DataSourceInfo } from '@/types/api';

export const mockExtractDataResponse: ExtractDataResponse = {
  job_id: 'test-job-123',
  status: 'completed',
  total_features: 1500,
  processing_time: 45.2,
  export_urls: {
    geojson: '/download/test-job-123/geojson',
    kmz: '/download/test-job-123/kmz',
  },
  results: {
    google_buildings: {
      status: 'success',
      feature_count: 850,
      processing_time: 25.1,
    },
    osm_roads: {
      status: 'success',
      feature_count: 650,
      processing_time: 20.1,
    },
  },
  metadata: {
    aoi_area_km2: 2.5,
    processing_started: '2023-01-01T10:00:00Z',
    processing_completed: '2023-01-01T10:00:45Z',
  },
};

export const mockDataSources: DataSourceInfo[] = [
  {
    id: 'google_buildings',
    name: 'Google Buildings',
    description: 'Google Open Buildings dataset',
    available: true,
    supported_features: ['buildings'],
    capabilities: {
      buildings: true,
      roads: false,
      landmarks: false,
      natural: false,
    },
  },
  // ... more mock data sources
];
```

### Testing Hook Usage
```typescript
// src/hooks/__tests__/useAtlasAPI.test.ts
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { useDataSources } from '../useAtlasAPI';
import { atlasAPI } from '@/services/atlasAPI';

// Mock the API
jest.mock('@/services/atlasAPI');
const mockedAtlasAPI = atlasAPI as jest.Mocked<typeof atlasAPI>;

describe('useDataSources', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  it('fetches data sources successfully', async () => {
    mockedAtlasAPI.getDataSources.mockResolvedValueOnce(mockDataSources);

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const { result, waitFor } = renderHook(() => useDataSources(), { wrapper });

    await waitFor(() => result.current.isSuccess);

    expect(result.current.data).toEqual(mockDataSources);
    expect(mockedAtlasAPI.getDataSources).toHaveBeenCalledTimes(1);
  });
});
```

## Best Practices

### 1. **Error Boundaries**
```typescript
// src/components/ErrorBoundary.tsx
import React from 'react';

interface Props {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error }>;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('API Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return <FallbackComponent error={this.state.error!} />;
    }

    return this.props.children;
  }
}
```

### 2. **Request Caching Strategy**
```typescript
// src/config/queryClient.ts
import { QueryClient } from 'react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Default cache time
      cacheTime: 5 * 60 * 1000, // 5 minutes
      staleTime: 2 * 60 * 1000,  // 2 minutes
      
      // Retry configuration
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      
      // Background refetch
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

### 3. **Request Cancellation**
```typescript
// src/hooks/useAbortController.ts
import { useEffect, useRef } from 'react';

export const useAbortController = () => {
  const abortControllerRef = useRef<AbortController>();

  useEffect(() => {
    abortControllerRef.current = new AbortController();
    
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const getSignal = () => abortControllerRef.current?.signal;

  return { getSignal };
};
```

This comprehensive API integration guide provides everything needed to connect the React frontend with the Atlas API, including proper error handling, caching strategies, and real-time updates.
