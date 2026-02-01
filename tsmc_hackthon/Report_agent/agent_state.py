"""
AgentState Definition for Multi-Agent System

This module defines the shared state structure that all agents use to communicate.
Based on the architecture document's Data Contract specification.
"""

from typing import TypedDict, Dict, List, Optional


class AgentState(TypedDict):
    """
    Shared state for the Multi-Agent System.
    All agents read from and write to this state.
    """
    # Input
    query: str                          # User's original question
    company_id: str                     # Target company ID (e.g., "2330")
    
    # Intermediate results from each agent
    basic_info: Optional[Dict]          # Company basic profile
    finance_results: Optional[Dict]     # Financial data (from Financial Analyst)
    earnings_call_summary: Optional[str] # Earnings call summary (from Earnings Call Analyst)
    news_summary: Optional[str]         # News summary (from News Agent)
    supply_chain_analysis: Optional[Dict] # Supply chain analysis (from Supply Chain Expert)
    
    # Quality control
    validation_status: Optional[bool]   # Whether passed quality check
    
    # Final output
    final_report: Optional[str]         # Final rendered Markdown report
