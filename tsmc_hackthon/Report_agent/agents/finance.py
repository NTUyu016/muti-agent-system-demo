"""
Financial Analyst Agent

This agent retrieves and summarizes financial data for the target company.
"""

from typing import Dict
import sys
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from tools.mock_bigquery import query_financial_data, format_financial_summary


def financial_analyst_node(state: AgentState) -> Dict:
    """
    Financial Analyst Agent node function.
    
    Queries financial data and formats it into a summary.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state dict with finance_results
    """
    company_id = state.get("company_id", "2330")
    
    # Query financial data
    financial_data = query_financial_data(company_id)
    
    if financial_data:
        summary = format_financial_summary(financial_data)
        return {
            "finance_results": {
                "raw_data": financial_data,
                "summary": summary
            }
        }
    else:
        return {
            "finance_results": {
                "raw_data": None,
                "summary": f"No financial data available for company {company_id}."
            }
        }
