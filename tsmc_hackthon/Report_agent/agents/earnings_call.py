"""
Earnings Call Analyst Agent

This agent retrieves and summarizes earnings call transcripts for the target company.
"""

from typing import Dict
import sys
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from tools.mock_rag import query_earnings_calls, format_earnings_call_summary


def earnings_call_analyst_node(state: AgentState) -> Dict:
    """
    Earnings Call Analyst Agent node function.
    
    Queries earnings call data and formats it into a summary.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state dict with earnings_call_summary
    """
    company_id = state.get("company_id", "2330")
    
    # Query earnings calls
    calls = query_earnings_calls(company_id, limit=2)
    
    if calls:
        summary = format_earnings_call_summary(calls)
        return {
            "earnings_call_summary": summary
        }
    else:
        return {
            "earnings_call_summary": f"No earnings call data available for company {company_id}."
        }
