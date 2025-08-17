"""
Main entry point for Property Valuation Agent
Supports both standalone operation and A2A communication
"""

import json
import sys
from typing import Dict, Any
from .state import PropertyValuationState
from .graph import create_property_valuation_workflow
from .a2a_client import A2APropertyValuationClient, A2ACommunicationHandler

def run_standalone_valuation(property_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run property valuation as standalone agent"""
    
    print("🏠 Property Valuation Agent - Standalone Mode")
    print("=" * 50)
    
    # Create workflow
    workflow = create_property_valuation_workflow()
    
    # Create initial state
    initial_state = PropertyValuationState(
        property_address=property_data.get('property_address', ''),
        property_type=property_data.get('property_type', 'single_family'),
        square_footage=property_data.get('square_footage'),
        bedrooms=property_data.get('bedrooms'),
        bathrooms=property_data.get('bathrooms'),
        year_built=property_data.get('year_built'),
        lot_size=property_data.get('lot_size'),
        
        # Initialize empty collections
        comparable_properties=[],
        market_trends={},
        neighborhood_data={},
        
        # Initialize results
        estimated_value=None,
        confidence_level=None,
        valuation_range=None,
        comparable_analysis={},
        market_adjustment={},
        final_assessment={},
        
        # Status
        current_step="initialized",
        errors=[],
        warnings=[],
        
        # No A2A fields for standalone
        request_id=None,
        requesting_agent=None,
        response_data=None
    )
    
    try:
        print(f"Processing valuation for: {property_data.get('property_address', 'Unknown Address')}")
        
        # Run the workflow
        result = workflow.invoke(initial_state)
        
        # Display results
        print("\n📊 VALUATION RESULTS")
        print("-" * 30)
        print(f"Property: {result['property_address']}")
        print(f"Estimated Value: ${result['estimated_value']:,.0f}")
        print(f"Confidence Level: {result['confidence_level']}")
        print(f"Value Range: ${result['valuation_range']['min_value']:,.0f} - ${result['valuation_range']['max_value']:,.0f}")
        
        if result.get('warnings'):
            print(f"\n⚠️  Warnings: {', '.join(result['warnings'])}")
        
        if result.get('errors'):
            print(f"\n❌ Errors: {', '.join(result['errors'])}")
        
        print(f"\nProcess completed at step: {result['current_step']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running valuation: {str(e)}")
        return {"error": str(e)}

def run_a2a_server_mode():
    """Run agent in A2A server mode (for integration testing)"""
    
    print("🔄 Property Valuation Agent - A2A Server Mode")
    print("=" * 50)
    print("Waiting for A2A requests... (Press Ctrl+C to stop)")
    
    client = A2APropertyValuationClient()
    
    # Simulate receiving A2A requests
    sample_requests = [
        {
            "property_address": "456 Oak Street, Springfield, IL 62701",
            "property_type": "single_family",
            "square_footage": 1800,
            "bedrooms": 3,
            "bathrooms": 2,
            "year_built": 2005,
            "lot_size": 0.3
        },
        {
            "property_address": "789 Pine Avenue, Metro City, CA 90210",
            "property_type": "condo",
            "square_footage": 1200,
            "bedrooms": 2,
            "bathrooms": 1,
            "year_built": 2015,
            "lot_size": None  # Condos typically don't have lot size
        }
    ]
    
    for i, request in enumerate(sample_requests):
        print(f"\n📨 Processing A2A Request #{i+1}")
        print(f"From: MortgageApproval Agent")
        print(f"Property: {request['property_address']}")
        
        response = client.process_valuation_request(request, "MortgageApproval")
        
        if response['status'] == 'SUCCESS':
            print(f"✅ Valuation completed")
            print(f"   Estimated Value: ${response['data']['estimated_value']:,.0f}")
            print(f"   Confidence: {response['data']['confidence_level']}")
            
            # Format for mortgage agent
            formatted = client.format_response_for_mortgage_agent(response['data'])
            print(f"   📤 Response sent to MortgageApproval agent")
        else:
            print(f"❌ Valuation failed: {response.get('error_message')}")

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "a2a":
            run_a2a_server_mode()
            return
        elif sys.argv[1] == "test":
            # Run test with sample data
            sample_data = {
                "property_address": "123 Test Street, Sample City, TX 75001",
                "property_type": "single_family",
                "square_footage": 2200,
                "bedrooms": 4,
                "bathrooms": 2.5,
                "year_built": 2010,
                "lot_size": 0.25
            }
            run_standalone_valuation(sample_data)
            return
    
    # Interactive mode
    print("🏠 Property Valuation Agent")
    print("=" * 50)
    print("Choose mode:")
    print("1. Standalone valuation")
    print("2. A2A server mode")
    print("3. Test with sample data")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Get property data from user
        print("\nEnter property information:")
        property_data = {
            "property_address": input("Address: "),
            "property_type": input("Type (single_family/condo/townhouse): ") or "single_family",
            "square_footage": int(input("Square footage: ") or "0") or None,
            "bedrooms": int(input("Bedrooms: ") or "0") or None,
            "bathrooms": float(input("Bathrooms: ") or "0") or None,
            "year_built": int(input("Year built: ") or "0") or None,
            "lot_size": float(input("Lot size (acres): ") or "0") or None
        }
        
        run_standalone_valuation(property_data)
        
    elif choice == "2":
        run_a2a_server_mode()
        
    elif choice == "3":
        sample_data = {
            "property_address": "123 Test Street, Sample City, TX 75001",
            "property_type": "single_family",
            "square_footage": 2200,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "year_built": 2010,
            "lot_size": 0.25
        }
        run_standalone_valuation(sample_data)
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()