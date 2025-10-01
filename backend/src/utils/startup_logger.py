"""
Professional startup logging system for Atlas GIS API
Provides Linux-style, machine-readable startup logs with security awareness
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from contextlib import contextmanager

from src.core.config import Settings


class LogLevel(Enum):
    """Log levels for startup logging"""
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "~"
    INFO = "-"
    ADDED = "+"


class StartupLogger:
    """
    Professional startup logger with Linux-style formatting
    Features:
    - Tree-style ASCII characters for hierarchical display
    - Security-aware logging (truncates sensitive data)
    - Conditional detail level (minimal on success, detailed on failure)
    - Machine-readable format similar to systemd/nala
    """
    
    def __init__(self, service_name: str = "atlas-gis-api", version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self.start_time = time.time()
        self.steps: List[Dict[str, Any]] = []
        self.current_step = 0
        self.failed = False
        self.debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
        
        # Configure standard logging to be minimal during startup
        if not self.debug_mode:
            logging.getLogger().setLevel(logging.WARNING)
            # Suppress verbose Google/urllib3 logging
            for logger_name in [
                "urllib3.connectionpool", "google.auth.transport.requests",
                "google.auth.transport.urllib3", "google.auth._default",
                "google.oauth2.service_account", "googleapiclient.discovery"
            ]:
                logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def start(self) -> None:
        """Start the startup logging sequence"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {self.service_name} v{self.version} starting...")
        
    def add_step(self, name: str, description: str = "", level: LogLevel = LogLevel.INFO) -> 'StartupStep':
        """Add a new step to the startup sequence"""
        step = StartupStep(self, name, description, level)
        self.steps.append({
            'name': name,
            'description': description,
            'level': level,
            'status': 'pending',
            'start_time': time.time(),
            'end_time': None,
            'details': [],
            'error': None
        })
        self.current_step = len(self.steps) - 1
        return step
    
    def complete_step(self, success: bool, details: Optional[str] = None, error: Optional[str] = None) -> None:
        """Complete the current step"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step['status'] = 'success' if success else 'failed'
            step['end_time'] = time.time()
            if details:
                step['details'].append(details)
            if error:
                step['error'] = error
                self.failed = True
    
    def log_step_success(self, summary: str) -> None:
        """Log successful completion of current step"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            symbol = "├─" if self.current_step < len(self.steps) - 1 else "└─"
            print(f"{symbol} {step['name']}: {summary}")
            self.complete_step(True, summary)
    
    def log_step_error(self, error_msg: str, details: Optional[str] = None) -> None:
        """Log error for current step"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            symbol = "├─" if self.current_step < len(self.steps) - 1 else "└─"
            print(f"{symbol} {step['name']}: ✗ {error_msg}")
            self.complete_step(False, details, error_msg)
    
    def finish(self) -> None:
        """Complete the startup sequence and display results"""
        total_time = time.time() - self.start_time
        
        if self.failed:
            self._display_failure_details()
        else:
            print(f"└─ server: ready on :{os.environ.get('PORT', '7860')}")
            print(f"\n[startup completed in {total_time:.1f}s]")
        
        # Re-enable normal logging levels
        if not self.debug_mode:
            logging.getLogger().setLevel(logging.INFO)
    
    def _display_failure_details(self) -> None:
        """Display detailed failure information"""
        print("\n" + "=" * 60)
        print("STARTUP FAILURE - Diagnostic Information")
        print("=" * 60)
        
        for i, step in enumerate(self.steps):
            if step['status'] == 'failed':
                print(f"\n✗ FAILED: {step['name']}")
                if step['error']:
                    print(f"  Error: {step['error']}")
                if step['details']:
                    for detail in step['details']:
                        print(f"  Details: {detail}")
                
                # Provide troubleshooting guidance
                self._provide_troubleshooting(step['name'], step['error'])
        
        print("\n" + "=" * 60)
        print("For additional help, check the documentation or enable DEBUG=true")
        print("=" * 60)
    
    def _provide_troubleshooting(self, step_name: str, error: Optional[str]) -> None:
        """Provide step-specific troubleshooting guidance"""
        guidance = {
            "platform": [
                "Verify environment variables are set correctly",
                "Check HuggingFace Spaces configuration"
            ],
            "config": [
                "Review .env file or environment variables",
                "Ensure numeric values are properly formatted",
                "Check for trailing whitespace in variables"
            ],
            "static": [
                "Verify src/web/static directory exists",
                "Check file permissions"
            ],
            "gee-auth": [
                "Verify Google Earth Engine credentials",
                "Check service account has required roles",
                "Ensure project is registered for Earth Engine"
            ],
            "gee-conn": [
                "Check internet connectivity",
                "Verify Google Earth Engine API is enabled",
                "Confirm service account permissions"
            ]
        }
        
        if step_name in guidance:
            print("  Troubleshooting:")
            for tip in guidance[step_name]:
                print(f"    • {tip}")
    
    @staticmethod
    def truncate_sensitive(value: str, prefix_len: int = 8) -> str:
        """Truncate sensitive information for secure logging"""
        if not value or len(value) <= prefix_len:
            return value
        return f"{value[:prefix_len]}..."
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            return f"{seconds / 60:.1f}m"


class StartupStep:
    """Context manager for individual startup steps"""
    
    def __init__(self, logger: StartupLogger, name: str, description: str, level: LogLevel):
        self.logger = logger
        self.name = name
        self.description = description
        self.level = level
        self.start_time = time.time()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Exception occurred
            error_msg = str(exc_val) if exc_val else "Unknown error"
            self.logger.log_step_error(error_msg)
            return False  # Don't suppress the exception
        return True
    
    def success(self, summary: str) -> None:
        """Mark step as successful with summary"""
        self.logger.log_step_success(summary)
    
    def error(self, error_msg: str, details: Optional[str] = None) -> None:
        """Mark step as failed with error message"""
        self.logger.log_step_error(error_msg, details)


class ConfigurationDisplay:
    """Professional configuration display for startup"""
    
    @staticmethod
    def show_minimal(settings: Settings, env_status: Dict[str, Any]) -> None:
        """Show minimal configuration information for successful startup"""
        platform = env_status.get('platform_detected', 'unknown')
        services = ConfigurationDisplay._get_configured_services(settings)
        
        print(f"├─ platform: {platform}")
        print(f"├─ config: loaded ({', '.join(services)})")
    
    @staticmethod
    def show_detailed_failure(settings: Settings, env_status: Dict[str, Any], 
                            config_validation: Dict[str, Any]) -> None:
        """Show detailed configuration for failure diagnosis"""
        print("\nCONFIGURATION DETAILS:")
        print("-" * 40)
        
        # Platform information
        platform = env_status.get('platform_detected', 'unknown')
        print(f"Platform: {platform}")
        if platform == 'huggingface_spaces':
            print(f"Space ID: {env_status.get('space_id', 'unknown')}")
            print(f"Author: {env_status.get('space_author', 'unknown')}")
        
        # Service configuration
        print(f"\nService: {settings.service_name} v{settings.version}")
        print(f"Debug mode: {settings.debug}")
        print(f"Log level: {settings.log_level}")
        print(f"Max AOI area: {settings.max_aoi_area_km2} km²")
        print(f"Request timeout: {settings.request_timeout}s")
        print(f"Overpass rate limit: {settings.overpass_rate_limit} req/s")
        
        # Google credentials (secure)
        if settings.google_cloud_project:
            print(f"\nGoogle Earth Engine:")
            print(f"  Project: {settings.google_cloud_project}")
            print(f"  Service Account: {settings.google_service_account_email}")
            if settings.google_private_key_id:
                print(f"  Key ID: {StartupLogger.truncate_sensitive(settings.google_private_key_id)}")
        
        # Validation results
        if config_validation.get('errors'):
            print("\nCONFIGURATION ERRORS:")
            for error in config_validation['errors']:
                print(f"  ✗ {error}")
        
        if config_validation.get('warnings'):
            print("\nCONFIGURATION WARNINGS:")
            for warning in config_validation['warnings']:
                print(f"  ~ {warning}")
        
        if env_status.get('issues'):
            print("\nENVIRONMENT ISSUES:")
            for issue in env_status['issues']:
                print(f"  ~ {issue}")
    
    @staticmethod
    def _get_configured_services(settings: Settings) -> List[str]:
        """Get list of configured services"""
        services = []
        
        # Core API service
        services.append("api")
        
        # Google Earth Engine
        if settings.google_cloud_project and settings.google_service_account_email:
            services.append("gee")
        
        # OpenStreetMap (always available)
        services.append("osm")
        
        # Static web interface
        services.append("web")
        
        # Export formats
        services.append("export")
        
        return services


class GoogleEarthEngineLogger:
    """Specialized logger for Google Earth Engine authentication"""
    
    def __init__(self, startup_logger: StartupLogger, debug_mode: bool = False):
        self.startup_logger = startup_logger
        self.debug_mode = debug_mode
        self.step = None
    
    def start_auth(self) -> None:
        """Start authentication process"""
        self.step = self.startup_logger.add_step("gee-auth", "Google Earth Engine authentication")
    
    def log_credentials_created(self, project_id: str, email: str, key_id: str) -> None:
        """Log successful credential creation (security-aware)"""
        if self.debug_mode:
            print(f"  Project: {project_id}")
            print(f"  Email: {email}")
            print(f"  Key ID: {StartupLogger.truncate_sensitive(key_id)}")
    
    def log_auth_success(self, method: str) -> None:
        """Log successful authentication"""
        if self.step:
            self.step.success("credentials ok")
    
    def log_auth_failure(self, error: str, method: str) -> None:
        """Log authentication failure"""
        if self.step:
            error_summary = self._categorize_auth_error(error)
            self.step.error(error_summary, error if self.debug_mode else None)
    
    def start_connection_test(self) -> None:
        """Start connection test"""
        self.step = self.startup_logger.add_step("gee-conn", "Google Earth Engine connection test")
    
    def log_test_success(self) -> None:
        """Log successful connection test"""
        if self.step:
            self.step.success("test passed")
    
    def log_test_failure(self, error: str) -> None:
        """Log connection test failure"""
        if self.step:
            error_summary = self._categorize_connection_error(error)
            self.step.error(error_summary, error if self.debug_mode else None)
    
    def _categorize_auth_error(self, error: str) -> str:
        """Categorize authentication errors for user-friendly display"""
        error_lower = error.lower()
        
        if 'serviceusage.serviceusageconsumer' in error_lower:
            return "missing service usage role"
        elif 'oauth' in error_lower or 'scope' in error_lower:
            return "oauth scope error"
        elif 'permission' in error_lower or 'forbidden' in error_lower:
            return "insufficient permissions"
        elif 'project' in error_lower:
            return "project configuration error"
        elif 'credentials' in error_lower:
            return "invalid credentials"
        else:
            return "authentication failed"
    
    def _categorize_connection_error(self, error: str) -> str:
        """Categorize connection errors for user-friendly display"""
        error_lower = error.lower()
        
        if 'network' in error_lower or 'connection' in error_lower:
            return "network connectivity issue"
        elif 'timeout' in error_lower:
            return "request timeout"
        elif 'api' in error_lower:
            return "api access error"
        else:
            return "connection test failed"


# Global startup logger instance
_startup_logger: Optional[StartupLogger] = None
_startup_completed: bool = False


def get_startup_logger() -> StartupLogger:
    """Get the global startup logger instance"""
    global _startup_logger, _startup_completed
    if _startup_logger is None and not _startup_completed:
        _startup_logger = StartupLogger()
    return _startup_logger


def reset_startup_logger() -> None:
    """Reset the global startup logger (for testing)"""
    global _startup_logger, _startup_completed
    _startup_logger = None
    _startup_completed = False


def mark_startup_completed() -> None:
    """Mark startup as completed to prevent duplicate sequences"""
    global _startup_completed
    _startup_completed = True