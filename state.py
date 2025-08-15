from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class PropertyValuationState(TypedDict):
    """State for property valuation workflow"""
    
    # Input property data
    property_address: str
    property_type: str  # "single_family", "condo", "townhouse", "multi_family"
    square_footage: Optional[int]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    year_built: Optional[int]
    lot_size: Optional[float]
    
    # Market data
    comparable_properties: List[Dict[str, Any]]
    market_trends: Dict[str, Any]
    neighborhood_data: Dict[str, Any]
    
    # Valuation results
    estimated_value: Optional[float]
    confidence_level: Optional[str]  # "HIGH", "MEDIUM", "LOW"
    valuation_range: Optional[Dict[str, float]]  # min/max values
    
    # Analysis details
    comparable_analysis: Dict[str, Any]
    market_adjustment: Dict[str, Any]
    final_assessment: Dict[str, Any]
    
    # Processing status
    current_step: str
    errors: List[str]
    warnings: List[str]
    
    # A2A Communication fields
    request_id: Optional[str]  # For tracking requests from other agents
    requesting_agent: Optional[str]  # Which agent made the request
    response_data: Optional[Dict[str, Any]]  # Data to send back to requesting agent