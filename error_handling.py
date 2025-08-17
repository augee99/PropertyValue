"""
Error handling utilities for PropertyValuation Agent
Provides robust error handling for LangGraph SaaS deployment
"""

import logging
import traceback
from typing import Dict, Any, Optional

# Import with fallback for platform deployment
try:
    from .state import PropertyValuationState
except ImportError:
    from state import PropertyValuationState

# Configure logging for SaaS platform
logger = logging.getLogger(__name__)

class PropertyValuationError(Exception):
    """Custom exception for property valuation errors"""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def handle_node_error(state: PropertyValuationState, node_name: str, error: Exception) -> PropertyValuationState:
    """Handle errors that occur in workflow nodes"""
    
    error_message = f"Error in {node_name}: {str(error)}"
    logger.error(error_message, exc_info=True)
    
    # Add error to state
    if 'errors' not in state:
        state['errors'] = []
    state['errors'].append(error_message)
    
    # Set current step to indicate failure
    state['current_step'] = f"{node_name}_failed"
    
    # For critical errors, set overall status
    if isinstance(error, PropertyValuationError):
        if error.error_code in ['INVALID_PROPERTY', 'API_FAILURE', 'CONFIGURATION_ERROR']:
            # These are non-recoverable errors
            state['current_step'] = 'workflow_failed'
    
    return state

def handle_a2a_error(error: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle A2A communication errors"""
    
    error_response = {
        "status": "ERROR",
        "error_code": "A2A_COMMUNICATION_ERROR",
        "error_message": str(error),
        "request_id": request_id,
        "agent": "PropertyValuation",
        "data": None
    }
    
    # Log the error
    logger.error(f"A2A Communication Error (Request ID: {request_id}): {str(error)}", exc_info=True)
    
    # Categorize error types
    if "timeout" in str(error).lower():
        error_response["error_code"] = "A2A_TIMEOUT"
    elif "authentication" in str(error).lower() or "credentials" in str(error).lower():
        error_response["error_code"] = "A2A_AUTH_ERROR"
    elif "network" in str(error).lower() or "connection" in str(error).lower():
        error_response["error_code"] = "A2A_NETWORK_ERROR"
    
    return error_response

def validate_environment() -> Dict[str, Any]:
    """Validate environment for SaaS deployment"""
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    import os
    
    # Check required environment variables
    required_vars = ['GOOGLE_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required environment variable: {var}")
    
    # Check optional environment variables
    optional_vars = {
        'LANGCHAIN_TRACING_V2': 'Tracing not enabled',
        'LANGCHAIN_API_KEY': 'LangSmith integration not available'
    }
    
    for var, warning in optional_vars.items():
        if not os.getenv(var):
            validation_result["warnings"].append(warning)
    
    return validation_result

def create_safe_response(state: PropertyValuationState) -> Dict[str, Any]:
    """Create a safe response even when workflow fails"""
    
    # Extract what data we can from the state
    response_data = {
        "property_address": state.get('property_address', 'Unknown'),
        "estimated_value": None,
        "confidence_level": "LOW",
        "confidence_score": 0,
        "valuation_range": None,
        "valuation_date": None,
        "appraiser_notes": "Valuation could not be completed due to system error"
    }
    
    # If we have some partial results, include them
    if state.get('estimated_value'):
        response_data["estimated_value"] = state['estimated_value']
        response_data["confidence_level"] = state.get('confidence_level', 'LOW')
        response_data["confidence_score"] = state.get('confidence_score', 0)
        response_data["valuation_range"] = state.get('valuation_range')
    
    return {
        "status": "PARTIAL_SUCCESS" if response_data["estimated_value"] else "ERROR",
        "agent": "PropertyValuation",
        "data": response_data,
        "errors": state.get('errors', []),
        "warnings": state.get('warnings', [])
    }