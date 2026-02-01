"""
News Agent

This agent retrieves and summarizes recent news for the target company.
"""

from typing import Dict
import sys
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from tools.mock_rag import query_news, format_news_summary


def news_agent_node(state: AgentState) -> Dict:
    """
    News Agent node function.
    
    Queries recent news and formats it into a summary.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state dict with news_summary
    """
    company_id = state.get("company_id", "2330")
    
    # Query news
    articles = query_news(company_id, limit=5)
    
    if articles:
        summary = format_news_summary(articles)
        return {
            "news_summary": summary
        }
    else:
        return {
            "news_summary": f"No recent news available for company {company_id}."
        }
