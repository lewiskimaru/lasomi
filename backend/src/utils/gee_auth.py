"""
Google Earth Engine authentication utility for local and cloud deployments
"""

import os
import ee
import json
import logging
import traceback
from typing import Optional, Dict, Any
from src.core.config import get_settings
from src.utils.startup_logger import get_startup_logger, GoogleEarthEngineLogger

# Set up detailed logging for Google API responses
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Enable detailed HTTP logging for Google API calls
import google.auth.transport.requests
import google.auth.transport.urllib3
import urllib3

# Enable urllib3 debug logging to capture raw HTTP responses
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
logging.getLogger("google.auth.transport.requests").setLevel(logging.DEBUG)
logging.getLogger("google.auth.transport.urllib3").setLevel(logging.DEBUG)
logging.getLogger("google.auth._default").setLevel(logging.DEBUG)


def create_service_account_credentials_from_env(gee_logger: Optional[GoogleEarthEngineLogger] = None) -> Optional[str]:
    """
    Create service account credentials from individual environment variables
    This is the proper way to handle secrets in HuggingFace Spaces
    """
    settings = get_settings()

    # Check if we have all required individual environment variables
    required_fields = {
        'type': 'service_account',
        'project_id': settings.google_cloud_project,
        'private_key_id': settings.google_private_key_id,
        'private_key': settings.google_private_key,
        'client_email': settings.google_service_account_email,
        'client_id': settings.google_client_id,
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'universe_domain': 'googleapis.com'
    }

    # Validate all required fields are present
    missing_fields = []
    for key, value in required_fields.items():
        if key in ['type', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'universe_domain']:
            continue  # These are constants
        if not value or not str(value).strip():
            missing_fields.append(key)

    if missing_fields:
        error_msg = f"Missing required Google service account fields: {missing_fields}"
        if gee_logger:
            gee_logger.log_auth_failure(error_msg, "environment_variables")
        return None

    # Add the client_x509_cert_url
    required_fields['client_x509_cert_url'] = f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.google_service_account_email.replace('@', '%40')}"

    try:
        # Create temporary credentials file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)

        # Log credentials creation (security-aware)
        if gee_logger:
            gee_logger.log_credentials_created(
                required_fields['project_id'],
                required_fields['client_email'],
                required_fields['private_key_id']
            )

        # Write credentials to temporary file
        json.dump(required_fields, temp_file, indent=2)
        temp_file.close()

        return temp_file.name

    except Exception as e:
        error_msg = f"Failed to create service account credentials: {e}"
        if gee_logger:
            gee_logger.log_auth_failure(error_msg, "file_creation")
        return None


def log_google_api_response(response_data: Any, context: str = "API Response", debug_mode: bool = False):
    """Log Google API response for debugging (only in debug mode)"""
    if debug_mode:
        logger.debug(f"{context}: {type(response_data)}")
        if hasattr(response_data, '__dict__'):
            logger.debug(f"Attributes: {response_data.__dict__}")


def initialize_earth_engine() -> bool:
    """
    Initialize Google Earth Engine with professional startup logging

    Returns:
        bool: True if initialization successful, False otherwise
    """
    settings = get_settings()
    startup_logger = get_startup_logger()
    gee_logger = GoogleEarthEngineLogger(startup_logger, debug_mode=settings.debug)
    
    gee_logger.start_auth()

    try:
        # Method 1: Try creating credentials from individual environment variables (HF Spaces)
        credentials_path = create_service_account_credentials_from_env(gee_logger)

        if not credentials_path:
            # Method 2: Try existing credentials file
            credentials_path = settings.get_google_credentials_path()

        if credentials_path and os.path.exists(credentials_path):
            # Set the credentials path in environment
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

            try:
                # Read and validate the credentials file
                with open(credentials_path, 'r') as f:
                    key_data = json.load(f)

                log_google_api_response(key_data, "Service Account Key Data", settings.debug)

                # Use the correct scopes for Earth Engine
                scopes = [
                    'https://www.googleapis.com/auth/earthengine',
                    'https://www.googleapis.com/auth/earthengine.readonly',
                    'https://www.googleapis.com/auth/devstorage.full_control',
                    'https://www.googleapis.com/auth/cloud-platform'
                ]

                # Method A: Try with explicit scopes using google.auth
                try:
                    from google.oauth2 import service_account
                    import google.auth

                    credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=scopes
                    )

                    log_google_api_response(credentials, "Google Auth Credentials Object", settings.debug)

                    # Initialize Earth Engine with the credentials
                    ee.Initialize(credentials, project=settings.google_cloud_project)

                    gee_logger.log_auth_success("google.oauth2.service_account")
                    return True

                except Exception as google_auth_error:
                    log_google_api_response(google_auth_error, "Google Auth Error", settings.debug)

                    # Method B: Try with ee.ServiceAccountCredentials (legacy method)
                    try:
                        credentials = ee.ServiceAccountCredentials(
                            key_data['client_email'],
                            credentials_path
                        )

                        log_google_api_response(credentials, "EE Credentials Object", settings.debug)

                        # Initialize with explicit credentials and project
                        ee.Initialize(credentials, project=settings.google_cloud_project)

                        gee_logger.log_auth_success("ee.ServiceAccountCredentials")
                        return True

                    except Exception as ee_auth_error:
                        log_google_api_response(ee_auth_error, "EE Auth Error", settings.debug)
                        raise ee_auth_error

            except Exception as credentials_error:
                log_google_api_response(credentials_error, "Credentials Error", settings.debug)

                # Method 3: Try default authentication (fallback)
                try:
                    ee.Initialize(project=settings.google_cloud_project)
                    gee_logger.log_auth_success("default_credentials")
                    return True

                except Exception as default_error:
                    log_google_api_response(default_error, "Default Auth Error", settings.debug)
                    raise default_error

        else:
            gee_logger.log_auth_failure("No Google Earth Engine credentials found", "missing_credentials")
            return False

    except Exception as e:
        log_google_api_response(e, "Critical Error", settings.debug)
        gee_logger.log_auth_failure(str(e), "critical_error")
        return False


def validate_service_account_setup() -> dict:
    """
    Validate Google service account setup for Earth Engine

    Returns:
        dict: Validation results with detailed information
    """
    settings = get_settings()
    validation_results = {
        'valid': False,
        'issues': [],
        'recommendations': [],
        'service_account_info': {}
    }

    try:
        credentials_path = settings.get_google_credentials_path()

        if not credentials_path:
            validation_results['issues'].append("No credentials file found")
            validation_results['recommendations'].append("Set up Google service account credentials")
            return validation_results

        # Read and validate service account file
        import json
        with open(credentials_path, 'r') as f:
            key_data = json.load(f)

        # Check required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if field not in key_data]

        if missing_fields:
            validation_results['issues'].append(f"Missing required fields: {missing_fields}")

        validation_results['service_account_info'] = {
            'email': key_data.get('client_email', 'unknown'),
            'project_id': key_data.get('project_id', 'unknown'),
            'type': key_data.get('type', 'unknown')
        }

        # Check if it's a service account
        if key_data.get('type') != 'service_account':
            validation_results['issues'].append(f"Expected service account, got: {key_data.get('type')}")
            validation_results['recommendations'].append("Use a service account key, not user credentials")

        # Validate project ID matches
        if key_data.get('project_id') != settings.google_cloud_project:
            validation_results['issues'].append(
                f"Project ID mismatch: credentials={key_data.get('project_id')}, config={settings.google_cloud_project}"
            )

        if not validation_results['issues']:
            validation_results['valid'] = True
            validation_results['recommendations'].extend([
                "Service account file appears valid",
                "Ensure the service account has Earth Engine access enabled",
                "Check that the project is registered for Earth Engine"
            ])
        else:
            validation_results['recommendations'].extend([
                "Fix the issues above",
                "Regenerate service account key if necessary",
                "Ensure service account has 'Earth Engine Resource Viewer' role"
            ])

    except Exception as e:
        validation_results['issues'].append(f"Error reading credentials: {e}")
        validation_results['recommendations'].append("Check credentials file format and permissions")

    return validation_results


def test_earth_engine_connection() -> bool:
    """
    Test Google Earth Engine connection with professional logging

    Returns:
        bool: True if connection successful, False otherwise
    """
    startup_logger = get_startup_logger()
    gee_logger = GoogleEarthEngineLogger(startup_logger, debug_mode=os.environ.get("DEBUG", "false").lower() == "true")
    
    gee_logger.start_connection_test()
    
    try:
        # Validate service account setup first
        validation = validate_service_account_setup()
        if not validation['valid']:
            error_msg = "; ".join(validation['issues'])
            gee_logger.log_test_failure(f"Service account validation failed: {error_msg}")
            return False

        # Simple test to verify Earth Engine is working
        try:
            # Test 1: Basic image access
            test_image = ee.Image("USGS/SRTMGL1_003")

            # Test 2: Get image info (this triggers actual API call)
            test_info = test_image.getInfo()
            
            log_google_api_response(test_info, "Test Image Info", gee_logger.debug_mode)
            gee_logger.log_test_success()
            return True

        except Exception as api_error:
            log_google_api_response(api_error, "API Call Error", gee_logger.debug_mode)

            # Try a simpler test
            try:
                ee.Number(1).getInfo()
                gee_logger.log_test_success()
                return True
            except Exception as simple_error:
                log_google_api_response(simple_error, "Simple Test Error", gee_logger.debug_mode)
                raise simple_error

    except Exception as e:
        log_google_api_response(e, "Connection Test Error", gee_logger.debug_mode)
        gee_logger.log_test_failure(str(e))
        return False