"""
Mock version of nodes.py that doesn't require LLM API calls
Used for testing and demonstration purposes
"""

from typing import Dict, Any, List
import random
import json
from .state import PropertyValuationState

def mock_property_data_collection_node(state: PropertyValuationState) -> PropertyValuationState:
    """Mock Node 1: Collect and validate property data"""
    
    # Basic validation logic without LLM
    missing_fields = []
    required_fields = ['square_footage', 'bedrooms', 'bathrooms', 'year_built']
    
    for field in required_fields:
        if not state.get(field):
            missing_fields.append(field)
    
    data_quality_score = max(0, 100 - (len(missing_fields) * 20))
    
    if len(missing_fields) == 0:
        data_completeness = "COMPLETE"
    elif len(missing_fields) <= 2:
        data_completeness = "PARTIAL"
    else:
        data_completeness = "INCOMPLETE"
    
    # Update state
    state['current_step'] = "property_data_collected"
    if data_completeness == "INCOMPLETE":
        state['errors'].append(f"Insufficient property data: missing {missing_fields}")
    elif data_completeness == "PARTIAL":
        state['warnings'].append(f"Some property data missing: {missing_fields}")
    
    return state

def mock_comparable_properties_node(state: PropertyValuationState) -> PropertyValuationState:
    """Mock Node 2: Find and analyze comparable properties"""
    
    # Generate mock comparable properties
    base_sqft = state.get('square_footage', 2000)
    comparable_properties = [
        {
            "address": f"123 Similar St, Same City",
            "sold_price": 450000 + random.randint(-50000, 50000),
            "square_footage": base_sqft + random.randint(-200, 200),
            "bedrooms": state.get('bedrooms', 3),
            "bathrooms": state.get('bathrooms', 2),
            "sale_date": "2024-10-15",
            "days_on_market": random.randint(15, 60)
        },
        {
            "address": f"456 Nearby Ave, Same City",
            "sold_price": 475000 + random.randint(-50000, 50000),
            "square_footage": base_sqft + random.randint(-300, 300),
            "bedrooms": state.get('bedrooms', 3) + random.randint(-1, 1),
            "bathrooms": state.get('bathrooms', 2),
            "sale_date": "2024-11-02",
            "days_on_market": random.randint(10, 45)
        },
        {
            "address": f"789 Close Blvd, Same City",
            "sold_price": 435000 + random.randint(-40000, 40000),
            "square_footage": base_sqft + random.randint(-250, 250),
            "bedrooms": state.get('bedrooms', 3),
            "bathrooms": state.get('bathrooms', 2) + 0.5,
            "sale_date": "2024-09-28",
            "days_on_market": random.randint(20, 80)
        }
    ]
    
    # Calculate average price and price per sq ft
    avg_price = sum(comp['sold_price'] for comp in comparable_properties) / len(comparable_properties)
    
    if state.get('square_footage'):
        avg_price_per_sqft = avg_price / state['square_footage']
    else:
        avg_price_per_sqft = avg_price / 2000  # Assume 2000 sq ft if missing
    
    comparable_analysis = {
        "number_of_comparables": len(comparable_properties),
        "average_sale_price": avg_price,
        "price_per_square_foot": avg_price_per_sqft,
        "comparable_quality": "GOOD",
        "price_range_low": avg_price * 0.9,
        "price_range_high": avg_price * 1.1
    }
    
    state['comparable_properties'] = comparable_properties
    state['comparable_analysis'] = comparable_analysis
    state['current_step'] = "comparables_analyzed"
    
    return state

def mock_market_analysis_node(state: PropertyValuationState) -> PropertyValuationState:
    """Mock Node 3: Analyze market trends and neighborhood data"""
    
    # Generate mock market data
    market_trends = {
        "market_direction": random.choice(["RISING", "STABLE", "DECLINING"]),
        "price_change_6_months": round(random.uniform(-5.0, 8.0), 2),
        "average_days_on_market": random.randint(25, 65),
        "inventory_level": random.choice(["LOW", "MODERATE", "HIGH"]),
        "buyer_demand": random.choice(["HIGH", "MODERATE", "LOW"])
    }
    
    neighborhood_data = {
        "school_rating": random.randint(6, 10),
        "crime_rate": random.choice(["LOW", "MODERATE", "HIGH"]),
        "walkability_score": random.randint(40, 95),
        "nearby_amenities": ["shopping", "parks", "restaurants"],
        "transportation_access": random.choice(["EXCELLENT", "GOOD", "FAIR"])
    }
    
    # Calculate market adjustment
    market_adjustment_factors = {
        "trend_adjustment": 2 if market_trends["market_direction"] == "RISING" else -2 if market_trends["market_direction"] == "DECLINING" else 0,
        "demand_adjustment": 3 if market_trends["buyer_demand"] == "HIGH" else -3 if market_trends["buyer_demand"] == "LOW" else 0,
        "inventory_adjustment": -2 if market_trends["inventory_level"] == "HIGH" else 2 if market_trends["inventory_level"] == "LOW" else 0,
        "neighborhood_adjustment": 5 if neighborhood_data["school_rating"] >= 9 else 2 if neighborhood_data["school_rating"] >= 7 else -2
    }
    
    total_market_adjustment = sum(market_adjustment_factors.values())
    
    market_adjustment = {
        "adjustment_factors": market_adjustment_factors,
        "total_adjustment_percent": max(-20, min(20, total_market_adjustment)),
        "market_confidence": "HIGH" if abs(total_market_adjustment) <= 5 else "MEDIUM" if abs(total_market_adjustment) <= 10 else "LOW"
    }
    
    state['market_trends'] = market_trends
    state['neighborhood_data'] = neighborhood_data
    state['market_adjustment'] = market_adjustment
    state['current_step'] = "market_analyzed"
    
    return state

def mock_final_valuation_node(state: PropertyValuationState) -> PropertyValuationState:
    """Mock Node 4: Calculate final property valuation"""
    
    base_value = state['comparable_analysis']['average_sale_price']
    market_adjustment_percent = state['market_adjustment']['total_adjustment_percent']
    
    # Apply market adjustments
    market_adjusted_value = base_value * (1 + market_adjustment_percent / 100)
    
    # Calculate confidence level
    data_quality_factors = []
    if not state.get('square_footage'):
        data_quality_factors.append("Missing square footage")
    if len(state['comparable_properties']) < 3:
        data_quality_factors.append("Limited comparables")
    if abs(market_adjustment_percent) > 10:
        data_quality_factors.append("High market volatility")
    
    if len(data_quality_factors) == 0:
        confidence_level = "HIGH"
        confidence_score = 85
    elif len(data_quality_factors) <= 1:
        confidence_level = "MEDIUM"
        confidence_score = 70
    else:
        confidence_level = "LOW"
        confidence_score = 55
    
    # Create valuation range
    range_factor = 0.05 if confidence_level == "HIGH" else 0.10 if confidence_level == "MEDIUM" else 0.15
    valuation_range = {
        "min_value": market_adjusted_value * (1 - range_factor),
        "max_value": market_adjusted_value * (1 + range_factor)
    }
    
    final_assessment = {
        "base_value": base_value,
        "market_adjustment_percent": market_adjustment_percent,
        "estimated_value": market_adjusted_value,
        "confidence_score": confidence_score,
        "valuation_method": "SALES_COMPARISON_APPROACH",
        "key_value_drivers": [
            "Comparable sales analysis",
            "Current market conditions",
            "Neighborhood characteristics"
        ],
        "limitations": data_quality_factors
    }
    
    # Prepare response data for A2A communication
    response_data = {
        "property_address": state['property_address'],
        "estimated_value": market_adjusted_value,
        "valuation_range": valuation_range,
        "confidence_level": confidence_level,
        "confidence_score": confidence_score,
        "valuation_date": "2024-12-15",  # Current date
        "appraiser_notes": f"Mock valuation based on {len(state['comparable_properties'])} comparable sales with {market_adjustment_percent:+.1f}% market adjustment"
    }
    
    state['estimated_value'] = market_adjusted_value
    state['confidence_level'] = confidence_level
    state['valuation_range'] = valuation_range
    state['final_assessment'] = final_assessment
    state['response_data'] = response_data
    state['current_step'] = "valuation_completed"
    
    return state

def mock_a2a_communication_node(state: PropertyValuationState) -> PropertyValuationState:
    """Mock Node 5: Handle agent-to-agent communication response"""
    
    if state.get('requesting_agent') and state.get('response_data'):
        # Mock LLM response formatting
        mock_llm_response = f"""
        Property Valuation Response for {state['requesting_agent']}:
        
        Summary: Professional valuation completed for {state['property_address']}
        Estimated Value: ${state['response_data']['estimated_value']:,.0f}
        Confidence: {state['response_data']['confidence_level']} ({state['response_data']['confidence_score']}%)
        
        Key Findings:
        - Based on comparable sales analysis
        - Market conditions considered
        - {state['response_data']['appraiser_notes']}
        
        Recommendation: Valuation suitable for mortgage lending purposes
        """
        
        # Log the communication
        state['current_step'] = "a2a_response_sent"
        if 'warnings' not in state:
            state['warnings'] = []
        state['warnings'].append(f"Mock response sent to {state['requesting_agent']} for request {state.get('request_id', 'N/A')}")
    else:
        state['current_step'] = "valuation_ready_for_use"
    
    return state