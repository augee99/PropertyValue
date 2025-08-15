"""
Agent-to-Agent Communication Client for Property Valuation Agent
Handles communication between PropertyValuation agent and other agents (e.g., MortgageApproval)
"""

import json
import uuid
from typing import Dict, Any, Optional
from state import PropertyValuationState
try:
    from graph import create_property_valuation_workflow
except ImportError:
    create_property_valuation_workflow = None

# Try to import mock version as fallback
try:
    from mock_graph import create_mock_property_valuation_workflow
except ImportError:
    create_mock_property_valuation_workflow = None

class A2APropertyValuationClient:
    """Client for handling A2A communication with Property Valuation Agent"""
    
    def __init__(self, use_mock=True):
        # Use mock workflow by default to avoid API requirements
        if use_mock and create_mock_property_valuation_workflow:
            self.workflow = create_mock_property_valuation_workflow()
            self.agent_name = "PropertyValuation (Mock)"
        elif create_property_valuation_workflow:
            self.workflow = create_property_valuation_workflow()
            self.agent_name = "PropertyValuation"
        else:
            raise ImportError("No property valuation workflow available")
        self.use_mock = use_mock
    
    def process_valuation_request(self, request_data: Dict[str, Any], requesting_agent: str) -> Dict[str, Any]:
        """
        Process a property valuation request from another agent
        
        Args:
            request_data: Property information for valuation
            requesting_agent: Name of the agent making the request
            
        Returns:
            Valuation response data
        """
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Create initial state from request
        initial_state = PropertyValuationState(
            property_address=request_data.get('property_address', ''),
            property_type=request_data.get('property_type', 'single_family'),
            square_footage=request_data.get('square_footage'),
            bedrooms=request_data.get('bedrooms'),
            bathrooms=request_data.get('bathrooms'),
            year_built=request_data.get('year_built'),
            lot_size=request_data.get('lot_size'),
            
            # Initialize empty collections
            comparable_properties=[],
            market_trends={},
            neighborhood_data={},
            
            # Initialize results as None
            estimated_value=None,
            confidence_level=None,
            valuation_range=None,
            comparable_analysis={},
            market_adjustment={},
            final_assessment={},
            
            # Status tracking
            current_step="initialized",
            errors=[],
            warnings=[],
            
            # A2A Communication fields
            request_id=request_id,
            requesting_agent=requesting_agent,
            response_data=None
        )
        
        try:
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Return the response data
            response = {
                "status": "SUCCESS",
                "request_id": request_id,
                "agent": self.agent_name,
                "data": result.get('response_data', {}),
                "errors": result.get('errors', []),
                "warnings": result.get('warnings', [])
            }
            
            return response
            
        except Exception as e:
            return {
                "status": "ERROR",
                "request_id": request_id,
                "agent": self.agent_name,
                "error_message": str(e),
                "data": None
            }
    
    def format_response_for_mortgage_agent(self, valuation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format valuation response specifically for mortgage approval agent
        
        Args:
            valuation_data: Raw valuation data
            
        Returns:
            Formatted response for mortgage agent
        """
        
        return {
            "property_valuation": {
                "estimated_value": valuation_data.get('estimated_value'),
                "confidence_level": valuation_data.get('confidence_level'),
                "confidence_score": valuation_data.get('confidence_score'),
                "valuation_range": valuation_data.get('valuation_range', {}),
                "appraisal_date": valuation_data.get('valuation_date'),
                "appraiser_notes": valuation_data.get('appraiser_notes')
            },
            "loan_to_value_calculation": {
                "estimated_value": valuation_data.get('estimated_value'),
                "ltv_ready": True
            },
            "valuation_flags": {
                "high_confidence": valuation_data.get('confidence_level') == 'HIGH',
                "market_stable": valuation_data.get('confidence_score', 0) > 70,
                "comparable_data_sufficient": True  # Based on successful completion
            }
        }

class A2ACommunicationHandler:
    """Handles bidirectional A2A communication"""
    
    @staticmethod
    def create_property_valuation_request(property_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standardized property valuation request
        
        Args:
            property_info: Property information from mortgage application
            
        Returns:
            Formatted request for property valuation agent
        """
        
        return {
            "request_type": "PROPERTY_VALUATION",
            "property_address": property_info.get('property_address'),
            "property_type": property_info.get('property_type', 'single_family'),
            "square_footage": property_info.get('square_footage'),
            "bedrooms": property_info.get('bedrooms'),
            "bathrooms": property_info.get('bathrooms'),
            "year_built": property_info.get('year_built'),
            "lot_size": property_info.get('lot_size'),
            "requesting_context": "MORTGAGE_APPROVAL",
            "urgency": "STANDARD",
            "required_confidence": "MEDIUM"  # Minimum confidence level needed
        }
    
    @staticmethod
    def validate_a2a_response(response: Dict[str, Any]) -> bool:
        """
        Validate that A2A response contains required fields
        
        Args:
            response: Response from property valuation agent
            
        Returns:
            True if response is valid
        """
        
        required_fields = ['status', 'request_id', 'agent']
        
        if response.get('status') == 'SUCCESS':
            data = response.get('data', {})
            required_data_fields = ['estimated_value', 'confidence_level', 'valuation_range']
            return (all(field in response for field in required_fields) and
                    all(field in data for field in required_data_fields))
        
        return all(field in response for field in required_fields)

# Example usage functions
def example_mortgage_to_property_valuation():
    """Example of how mortgage agent would request property valuation"""
    
    # Mortgage agent has this property info
    property_info = {
        "property_address": "123 Main St, Anytown, ST 12345",
        "property_type": "single_family",
        "square_footage": 2200,
        "bedrooms": 4,
        "bathrooms": 2.5,
        "year_built": 2010,
        "lot_size": 0.25
    }
    
    # Create A2A request
    valuation_request = A2ACommunicationHandler.create_property_valuation_request(property_info)
    
    # Send to property valuation agent
    prop_val_client = A2APropertyValuationClient()
    response = prop_val_client.process_valuation_request(valuation_request, "MortgageApproval")
    
    # Validate response
    if A2ACommunicationHandler.validate_a2a_response(response):
        # Format for mortgage agent use
        formatted_response = prop_val_client.format_response_for_mortgage_agent(response['data'])
        print("Property valuation successful!")
        print(f"Estimated Value: ${response['data']['estimated_value']:,.0f}")
        print(f"Confidence: {response['data']['confidence_level']}")
        return formatted_response
    else:
        print(f"Property valuation failed: {response.get('error_message', 'Unknown error')}")
        return None

if __name__ == "__main__":
    # Run example
    result = example_mortgage_to_property_valuation()
    if result:
        print("\nFormatted response for mortgage agent:")
        print(json.dumps(result, indent=2))