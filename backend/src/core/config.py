"""
Application configuration management using Pydantic Settings
"""

import os
import json
import base64
import tempfile
from functools import lru_cache
from typing import List, Optional, Union
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support

    Handles HuggingFace Spaces environment variable injection with robust validation
    and error handling to prevent runtime failures from malformed environment variables.
    """
    
    # Application Info
    service_name: str = Field(default="atlas-geospatial-api", description="Service name")
    version: str = Field(default="1.0.0", description="API version")
    debug: bool = Field(default=False, description="Debug mode")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator('service_name', 'version', 'log_level', 'overpass_api_url', mode='before')
    @classmethod
    def strip_string_fields(cls, v) -> str:
        """Strip whitespace from string fields that may come from environment variables"""
        if isinstance(v, str):
            return v.strip()
        return str(v) if v is not None else ""

    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug_flag(cls, v) -> bool:
        """Parse debug flag, handling string values from environment variables"""
        if isinstance(v, str):
            v = v.strip().lower()
            return v in ('true', '1', 'yes', 'on')
        elif isinstance(v, bool):
            return v
        else:
            return bool(v)
    
    # CORS settings
    allowed_origins: Union[str, List[str]] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Handle comma-separated string from environment variables
            if v.strip():
                return [origin.strip() for origin in v.split(',')]
            else:
                return ["*"]  # Default to allow all if empty
        elif isinstance(v, list):
            return v
        else:
            # Fallback for any other type
            return [str(v)] if v else ["*"]
    
    # Google Earth Engine Configuration - Method 1: Local file
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path to Google Earth Engine service account JSON"
    )
    
    # Google Earth Engine Configuration - Method 2: Individual environment variables
    google_cloud_project: Optional[str] = Field(
        default=None,
        description="Google Cloud Project ID"
    )
    google_service_account_email: Optional[str] = Field(
        default=None,
        description="Google service account email"
    )
    google_private_key: Optional[str] = Field(
        default=None,
        description="Google service account private key"
    )
    google_private_key_id: Optional[str] = Field(
        default=None,
        description="Google service account private key ID"
    )
    google_client_id: Optional[str] = Field(
        default=None,
        description="Google service account client ID"
    )

    @field_validator('google_application_credentials', 'google_cloud_project', 'google_service_account_email',
                     'google_private_key_id', 'google_client_id', mode='before')
    @classmethod
    def strip_google_credentials(cls, v) -> Optional[str]:
        """Strip whitespace from Google credential fields that may come from environment variables"""
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator('google_private_key', mode='before')
    @classmethod
    def parse_google_private_key(cls, v) -> Optional[str]:
        """Parse Google private key, handling whitespace but preserving internal structure"""
        if isinstance(v, str):
            # Only strip leading/trailing whitespace, preserve internal newlines
            stripped = v.strip()
            return stripped if stripped else None
        return v
    
    # Processing Constraints (essential only)
    max_aoi_area_km2: float = Field(
        default=100.0,
        description="Maximum AOI area in square kilometers"
    )
    request_timeout: int = Field(
        default=300,
        description="Request timeout in seconds"
    )
    
    # Google Earth Engine Configuration
    gee_max_features: int = Field(
        default=100000,
        description="Maximum features to extract from Google Earth Engine per source"
    )
    gee_simplification_threshold: int = Field(
        default=25000,
        description="Feature count threshold above which geometry simplification is applied"
    )
    gee_sampling_threshold: int = Field(
        default=50000,
        description="Feature count threshold above which systematic sampling is applied"
    )

    @field_validator('max_aoi_area_km2', mode='before')
    @classmethod
    def parse_max_aoi_area(cls, v) -> float:
        """Parse max AOI area, handling string values with whitespace from environment variables"""
        if isinstance(v, str):
            # Strip whitespace and newlines that may come from HuggingFace Spaces
            v = v.strip()
            if v:
                try:
                    return float(v)
                except ValueError:
                    raise ValueError(f"Cannot parse max_aoi_area_km2 as float: {repr(v)}")
            else:
                return 100.0  # Default value
        elif isinstance(v, (int, float)):
            return float(v)
        else:
            raise ValueError(f"max_aoi_area_km2 must be a number, got {type(v)}: {repr(v)}")

    @field_validator('gee_max_features', 'gee_simplification_threshold', 'gee_sampling_threshold', mode='before')
    @classmethod
    def parse_gee_thresholds(cls, v) -> int:
        """Parse Google Earth Engine threshold values"""
        if isinstance(v, str):
            v = v.strip()
            if v:
                try:
                    return int(float(v))
                except ValueError:
                    raise ValueError(f"Cannot parse GEE threshold as int: {repr(v)}")
            else:
                return 100000  # Default value
        elif isinstance(v, (int, float)):
            return int(v)
        else:
            raise ValueError(f"GEE threshold must be a number, got {type(v)}: {repr(v)}")
    
    @field_validator('request_timeout', mode='before')
    @classmethod
    def parse_request_timeout(cls, v) -> int:
        """Parse request timeout, handling string values with whitespace from environment variables"""
        if isinstance(v, str):
            # Strip whitespace and newlines that may come from HuggingFace Spaces
            v = v.strip()
            if v:
                try:
                    return int(float(v))  # Allow float strings like "300.0"
                except ValueError:
                    raise ValueError(f"Cannot parse request_timeout as int: {repr(v)}")
            else:
                return 300  # Default value
        elif isinstance(v, (int, float)):
            return int(v)
        else:
            raise ValueError(f"request_timeout must be a number, got {type(v)}: {repr(v)}")
    
    # OpenStreetMap Configuration
    overpass_api_url: str = Field(
        default="https://overpass-api.de/api/interpreter",
        description="Overpass API endpoint URL"
    )
    overpass_rate_limit: float = Field(
        default=0.5,
        description="Overpass API rate limit (requests per second)"
    )
    overpass_timeout: int = Field(
        default=25,
        description="Overpass API request timeout in seconds"
    )
    
    # Export and Job Management
    export_temp_dir: str = Field(
        default="./temp/exports",
        description="Temporary directory for export files"
    )
    job_ttl_seconds: int = Field(
        default=3600,
        description="Job result time-to-live in seconds (1 hour)"
    )
    max_concurrent_jobs: int = Field(
        default=10,
        description="Maximum concurrent processing jobs"
    )
    
    # Export Service Configuration
    supported_export_formats: List[str] = Field(
        default=["geojson", "kml", "kmz", "csv"],
        description="List of supported export formats"
    )
    max_export_size_mb: float = Field(
        default=100.0,
        description="Maximum export file size in megabytes"
    )
    
    # Design Upload Configuration
    max_design_file_size_mb: float = Field(
        default=50.0,
        description="Maximum design file upload size in megabytes"
    )
    supported_design_formats: List[str] = Field(
        default=["geojson", "kml", "kmz"],
        description="List of supported design file formats"
    )
    design_storage_ttl_days: int = Field(
        default=7,
        description="Design file storage time-to-live in days"
    )

    @field_validator('overpass_rate_limit', mode='before')
    @classmethod
    def parse_overpass_rate_limit(cls, v) -> float:
        """Parse overpass rate limit, handling string values with whitespace from environment variables"""
        if isinstance(v, str):
            # Strip whitespace and newlines that may come from HuggingFace Spaces
            v = v.strip()
            if v:
                try:
                    return float(v)
                except ValueError:
                    raise ValueError(f"Cannot parse overpass_rate_limit as float: {repr(v)}")
            else:
                return 0.5  # Default value
        elif isinstance(v, (int, float)):
            return float(v)
        else:
            raise ValueError(f"overpass_rate_limit must be a number, got {type(v)}: {repr(v)}")

    @field_validator('overpass_timeout', mode='before')
    @classmethod
    def parse_overpass_timeout(cls, v) -> int:
        """Parse overpass timeout, handling string values with whitespace from environment variables"""
        if isinstance(v, str):
            # Strip whitespace and newlines that may come from HuggingFace Spaces
            v = v.strip()
            if v:
                try:
                    return int(float(v))  # Allow float strings like "25.0"
                except ValueError:
                    raise ValueError(f"Cannot parse overpass_timeout as int: {repr(v)}")
            else:
                return 25  # Default value
        elif isinstance(v, (int, float)):
            return int(v)
        else:
            raise ValueError(f"overpass_timeout must be a number, got {type(v)}: {repr(v)}")
    
    model_config = SettingsConfigDict(
        # HuggingFace Spaces best practices:
        # 1. Don't rely on .env files in production (they're not included in Docker builds)
        # 2. Use environment variables directly from Space Settings
        # 3. Handle both runtime and buildtime variables appropriately
        env_file=".env" if Path(".env").exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True,
        # Allow extra fields for forward compatibility
        extra='ignore'
    )
    
    def get_google_credentials_path(self) -> Optional[str]:
        """
        Get Google Earth Engine credentials using multiple methods with priority:
        1. Local JSON file (development)
        2. Individual environment variables (secure cloud deployment)
        3. Base64 encoded key (legacy cloud deployment)
        """
        # Method 1: Local JSON file (highest priority for development)
        if self.google_application_credentials and Path(self.google_application_credentials).exists():
            print(f"✓ Using local credentials file: {self.google_application_credentials}")
            return self.google_application_credentials
        
        # Method 2: Individual environment variables (secure cloud deployment)
        if all([
            self.google_cloud_project,
            self.google_service_account_email,
            self.google_private_key,
            self.google_private_key_id,
            self.google_client_id
        ]):
            try:
                # Create service account JSON from individual components
                # Ensure proper formatting for Google Earth Engine authentication
                service_account_data = {
                    "type": "service_account",
                    "project_id": self.google_cloud_project,
                    "private_key_id": self.google_private_key_id,
                    "private_key": self.google_private_key.replace('\\n', '\n'),  # Handle escaped newlines
                    "client_email": self.google_service_account_email,
                    "client_id": self.google_client_id,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.google_service_account_email.replace('@', '%40')}",
                    "universe_domain": "googleapis.com"
                }
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(service_account_data, temp_file, indent=2)
                temp_file.close()
                
                # Set environment variable for Google libraries
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name
                print(f"✓ Using individual environment variables for authentication")
                return temp_file.name
                
            except Exception as e:
                print(f"Error creating credentials from environment variables: {e}")
        
        print("❌ No valid Google Earth Engine credentials found")
        print("   Options:")
        print("   1. Place JSON file at: ./keys/gee-service-account.json")
        print("   2. Set individual environment variables (recommended for cloud)")
        return None

    def validate_configuration(self) -> dict:
        """
        Comprehensive configuration validation
        Returns validation results with detailed error information
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }

        # Validate numeric constraints
        if self.max_aoi_area_km2 <= 0:
            validation_results['errors'].append(
                f"max_aoi_area_km2 must be positive, got: {self.max_aoi_area_km2}"
            )
            validation_results['valid'] = False
        elif self.max_aoi_area_km2 > 1000:
            validation_results['warnings'].append(
                f"max_aoi_area_km2 is very large ({self.max_aoi_area_km2} km²), consider reducing for better performance"
            )

        if self.request_timeout <= 0:
            validation_results['errors'].append(
                f"request_timeout must be positive, got: {self.request_timeout}"
            )
            validation_results['valid'] = False
        elif self.request_timeout > 600:
            validation_results['warnings'].append(
                f"request_timeout is very long ({self.request_timeout}s), consider reducing"
            )

        if self.overpass_rate_limit <= 0:
            validation_results['errors'].append(
                f"overpass_rate_limit must be positive, got: {self.overpass_rate_limit}"
            )
            validation_results['valid'] = False
        elif self.overpass_rate_limit > 2.0:
            validation_results['warnings'].append(
                f"overpass_rate_limit is high ({self.overpass_rate_limit}), may cause API throttling"
            )

        if self.overpass_timeout <= 0:
            validation_results['errors'].append(
                f"overpass_timeout must be positive, got: {self.overpass_timeout}"
            )
            validation_results['valid'] = False

        # Validate string fields
        if not self.service_name.strip():
            validation_results['errors'].append("service_name cannot be empty")
            validation_results['valid'] = False

        if not self.version.strip():
            validation_results['errors'].append("version cannot be empty")
            validation_results['valid'] = False

        if self.log_level.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            validation_results['warnings'].append(
                f"log_level '{self.log_level}' may not be recognized by logging system"
            )

        # Validate Google credentials
        google_creds_fields = [
            self.google_cloud_project, self.google_service_account_email,
            self.google_private_key, self.google_private_key_id, self.google_client_id
        ]

        google_creds_count = sum(1 for field in google_creds_fields if field)

        if google_creds_count == 0:
            validation_results['warnings'].append(
                "No Google Earth Engine credentials configured - some features will be unavailable"
            )
        elif google_creds_count < 5:
            validation_results['errors'].append(
                f"Incomplete Google credentials: {google_creds_count}/5 fields provided"
            )
            validation_results['valid'] = False
        else:
            validation_results['info'].append("Google Earth Engine credentials configured")

        # Validate URL format
        if not self.overpass_api_url.startswith(('http://', 'https://')):
            validation_results['errors'].append(
                f"overpass_api_url must be a valid URL, got: {self.overpass_api_url}"
            )
            validation_results['valid'] = False

        return validation_results


def validate_huggingface_spaces_environment() -> dict:
    """
    Validate environment for HuggingFace Spaces deployment
    Returns validation results and recommendations
    """
    import os

    validation_results = {
        'platform_detected': 'unknown',
        'environment_status': 'unknown',
        'issues': [],
        'recommendations': [],
        'google_credentials_status': 'not_configured'
    }

    # Detect if we're running in HuggingFace Spaces
    if os.environ.get('SPACE_ID') or os.environ.get('SPACE_AUTHOR_NAME'):
        validation_results['platform_detected'] = 'huggingface_spaces'
        validation_results['space_id'] = os.environ.get('SPACE_ID', 'unknown')
        validation_results['space_author'] = os.environ.get('SPACE_AUTHOR_NAME', 'unknown')
    elif os.path.exists('/.dockerenv'):
        validation_results['platform_detected'] = 'docker_container'
    else:
        validation_results['platform_detected'] = 'local_development'

    # Check for required Google credentials
    google_vars = ['GOOGLE_CLOUD_PROJECT', 'GOOGLE_SERVICE_ACCOUNT_EMAIL',
                   'GOOGLE_PRIVATE_KEY', 'GOOGLE_PRIVATE_KEY_ID', 'GOOGLE_CLIENT_ID']

    google_vars_present = [var for var in google_vars if os.environ.get(var)]

    if len(google_vars_present) == len(google_vars):
        validation_results['google_credentials_status'] = 'complete'
    elif len(google_vars_present) > 0:
        validation_results['google_credentials_status'] = 'partial'
        validation_results['issues'].append(
            f"Missing Google credentials: {set(google_vars) - set(google_vars_present)}"
        )
    else:
        validation_results['google_credentials_status'] = 'missing'
        validation_results['issues'].append("No Google Earth Engine credentials found")

    # Check for environment variable formatting issues
    numeric_vars = ['MAX_AOI_AREA_KM2', 'REQUEST_TIMEOUT', 'OVERPASS_RATE_LIMIT', 'OVERPASS_TIMEOUT']
    for var in numeric_vars:
        value = os.environ.get(var)
        if value:
            stripped = value.strip()
            if value != stripped:
                validation_results['issues'].append(
                    f"{var} has whitespace: {repr(value)} -> {repr(stripped)}"
                )

    # Platform-specific recommendations
    if validation_results['platform_detected'] == 'huggingface_spaces':
        validation_results['recommendations'].extend([
            "✅ Running on HuggingFace Spaces - environment variables are injected at runtime",
            "🔧 Use Space Settings to configure environment variables",
            "🔒 Use Secrets for sensitive data like Google credentials",
            "📝 Variables are automatically available as environment variables"
        ])
    elif validation_results['platform_detected'] == 'docker_container':
        validation_results['recommendations'].extend([
            "🐳 Running in Docker container",
            "🔧 Ensure environment variables are passed to docker run",
            "📁 Consider using .env file for local development"
        ])
    else:
        validation_results['recommendations'].extend([
            "💻 Local development detected",
            "📁 Create .env file from .env.template",
            "🔑 Place Google service account JSON in keys/ directory"
        ])

    # Set overall status
    if not validation_results['issues']:
        validation_results['environment_status'] = 'healthy'
    elif validation_results['google_credentials_status'] in ['complete', 'partial']:
        validation_results['environment_status'] = 'warning'
    else:
        validation_results['environment_status'] = 'error'

    return validation_results


def debug_environment_variables() -> dict:
    """Debug utility to inspect environment variables for troubleshooting"""
    import os

    # Environment variables we're interested in
    env_vars_of_interest = [
        'DEBUG', 'LOG_LEVEL', 'MAX_AOI_AREA_KM2', 'REQUEST_TIMEOUT',
        'OVERPASS_RATE_LIMIT', 'OVERPASS_TIMEOUT', 'OVERPASS_API_URL',
        'GOOGLE_CLOUD_PROJECT', 'GOOGLE_SERVICE_ACCOUNT_EMAIL',
        'GOOGLE_PRIVATE_KEY_ID', 'GOOGLE_CLIENT_ID', 'GOOGLE_PRIVATE_KEY',
        'ALLOWED_ORIGINS', 'SERVICE_NAME', 'VERSION'
    ]

    debug_info = {
        'environment_variables': {},
        'issues_detected': [],
        'recommendations': []
    }

    for var in env_vars_of_interest:
        value = os.environ.get(var)
        if value is not None:
            # Check for common issues
            original_value = value
            stripped_value = value.strip()

            debug_info['environment_variables'][var] = {
                'raw_value': repr(original_value),
                'stripped_value': repr(stripped_value),
                'has_whitespace': original_value != stripped_value,
                'length': len(original_value),
                'type': type(original_value).__name__
            }

            # Detect issues
            if original_value != stripped_value:
                debug_info['issues_detected'].append(
                    f"{var} has leading/trailing whitespace: {repr(original_value)}"
                )

            if var in ['MAX_AOI_AREA_KM2', 'REQUEST_TIMEOUT', 'OVERPASS_RATE_LIMIT', 'OVERPASS_TIMEOUT']:
                try:
                    float(stripped_value)
                except ValueError:
                    debug_info['issues_detected'].append(
                        f"{var} cannot be parsed as number: {repr(stripped_value)}"
                    )
        else:
            debug_info['environment_variables'][var] = None

    # Add recommendations
    if debug_info['issues_detected']:
        debug_info['recommendations'].append(
            "Environment variables with whitespace detected. The application now handles this automatically."
        )

    debug_info['recommendations'].extend([
        "Verify that Hugging Face Spaces environment variables are set correctly",
        "Check that numeric values don't have trailing newlines or spaces",
        "Ensure Google credentials are properly formatted"
    ])

    return debug_info


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings with professional startup logging"""
    try:
        settings = Settings()
    except Exception as e:
        print(f"✗ CRITICAL: Failed to load configuration: {e}")
        print("This is likely due to malformed environment variables.")
        print("Check your HuggingFace Space environment variable settings.")
        raise RuntimeError(f"Configuration loading failed: {e}") from e

    # Validate configuration
    config_validation = settings.validate_configuration()

    # Validate environment for HuggingFace Spaces
    env_validation = validate_huggingface_spaces_environment()
    
    # Import startup logger here to avoid circular imports
    from src.utils.startup_logger import get_startup_logger, ConfigurationDisplay, _startup_completed
    
    # Only show startup sequence if not already completed
    if not _startup_completed:
        startup_logger = get_startup_logger()
        
        # Add platform detection step
        platform_step = startup_logger.add_step("platform", "Platform detection")
        platform_step.success(env_validation['platform_detected'])
        
        # Add configuration loading step
        config_step = startup_logger.add_step("config", "Configuration loading")
        
        # Check for critical configuration errors
        if config_validation['errors']:
            error_summary = f"{len(config_validation['errors'])} errors found"
            config_step.error(error_summary)
            
            # Show detailed failure information
            ConfigurationDisplay.show_detailed_failure(settings, env_validation, config_validation)
            
            print("\n🚨 CRITICAL: Configuration has errors that will cause runtime failures!")
            raise RuntimeError(f"Invalid configuration: {config_validation['errors']}")
        else:
            # Show minimal successful configuration
            ConfigurationDisplay.show_minimal(settings, env_validation)
            config_step.success("loaded")

    return settings