"""
Mock version of graph.py that uses mock nodes instead of LLM-based nodes
Used for testing and demonstration without requiring API credentials
"""

from langgraph.graph import StateGraph, END

# Import with fallback for platform deployment
try:
    from .state import PropertyValuationState
except ImportError:
    from state import PropertyValuationState

try:
    from .mock_nodes import (
        mock_property_data_collection_node,
        mock_comparable_properties_node,
        mock_market_analysis_node,
        mock_final_valuation_node,
        mock_a2a_communication_node
    )
except ImportError:
    from mock_nodes import (
        mock_property_data_collection_node,
        mock_comparable_properties_node,
        mock_market_analysis_node,
        mock_final_valuation_node,
        mock_a2a_communication_node
    )

def create_mock_property_valuation_workflow():
    """Create the property valuation workflow using mock nodes"""
    
    # Create the state graph
    workflow = StateGraph(PropertyValuationState)
    
    # Add mock nodes
    workflow.add_node("data_collection", mock_property_data_collection_node)
    workflow.add_node("comparables", mock_comparable_properties_node)
    workflow.add_node("market_analysis", mock_market_analysis_node)
    workflow.add_node("final_valuation", mock_final_valuation_node)
    workflow.add_node("a2a_communication", mock_a2a_communication_node)
    
    # Define the flow
    workflow.set_entry_point("data_collection")
    
    # Sequential flow through all nodes
    workflow.add_edge("data_collection", "comparables")
    workflow.add_edge("comparables", "market_analysis")
    workflow.add_edge("market_analysis", "final_valuation")
    workflow.add_edge("final_valuation", "a2a_communication")
    workflow.add_edge("a2a_communication", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

def create_mock_conditional_property_valuation_workflow():
    """Create property valuation workflow with conditional routing using mock nodes"""
    
    def should_continue_after_data_collection(state: PropertyValuationState):
        """Route based on data collection results"""
        if len(state.get('errors', [])) > 0:
            return "a2a_communication"  # Skip to response if critical errors
        return "comparables"
    
    def should_continue_after_comparables(state: PropertyValuationState):
        """Route based on comparable analysis"""
        if state['comparable_analysis']['comparable_quality'] == 'POOR':
            # Still continue but add warning
            if 'warnings' not in state:
                state['warnings'] = []
            state['warnings'].append("Limited comparable data available")
        return "market_analysis"
    
    workflow = StateGraph(PropertyValuationState)
    
    # Add mock nodes
    workflow.add_node("data_collection", mock_property_data_collection_node)
    workflow.add_node("comparables", mock_comparable_properties_node)
    workflow.add_node("market_analysis", mock_market_analysis_node)
    workflow.add_node("final_valuation", mock_final_valuation_node)
    workflow.add_node("a2a_communication", mock_a2a_communication_node)
    
    # Define conditional flow
    workflow.set_entry_point("data_collection")
    
    workflow.add_conditional_edges(
        "data_collection",
        should_continue_after_data_collection,
        {
            "comparables": "comparables",
            "a2a_communication": "a2a_communication"
        }
    )
    
    workflow.add_conditional_edges(
        "comparables",
        should_continue_after_comparables,
        {
            "market_analysis": "market_analysis"
        }
    )
    
    workflow.add_edge("market_analysis", "final_valuation")
    workflow.add_edge("final_valuation", "a2a_communication")
    workflow.add_edge("a2a_communication", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app