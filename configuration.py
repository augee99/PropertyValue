"""
Configuration schema for PropertyValuation Agent
Defines configurable parameters for LangGraph SaaS deployment
"""

from typing import Optional
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables import ConfigurableField


class PropertyValuationConfiguration(TypedDict):
    """Configuration for Property Valuation Agent"""
    
    # LLM Configuration
    model: Annotated[str, ConfigurableField(
        id="model",
        name="LLM Model",
        description="The language model to use for property valuation analysis"
    )] = "gemini-2.5-flash"
    
    temperature: Annotated[float, ConfigurableField(
        id="temperature",
        name="Temperature",
        description="Controls randomness in LLM responses (0.0-1.0)"
    )] = 0.1
    
    # Property Valuation Parameters
    confidence_threshold: Annotated[str, ConfigurableField(
        id="confidence_threshold",
        name="Minimum Confidence Level",
        description="Minimum confidence level required for valuations"
    )] = "MEDIUM"
    
    max_comparables: Annotated[int, ConfigurableField(
        id="max_comparables",
        name="Maximum Comparables",
        description="Maximum number of comparable properties to analyze"
    )] = 5
    
    market_adjustment_limit: Annotated[float, ConfigurableField(
        id="market_adjustment_limit",
        name="Market Adjustment Limit",
        description="Maximum market adjustment percentage (±)"
    )] = 20.0
    
    # A2A Communication Settings
    enable_a2a_communication: Annotated[bool, ConfigurableField(
        id="enable_a2a_communication",
        name="Enable A2A Communication",
        description="Allow agent-to-agent communication requests"
    )] = True
    
    a2a_timeout_seconds: Annotated[int, ConfigurableField(
        id="a2a_timeout_seconds",
        name="A2A Timeout (seconds)",
        description="Timeout for A2A communication requests"
    )] = 120