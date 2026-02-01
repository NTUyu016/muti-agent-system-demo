"""
Supervisor Agent

This agent parses the user query and extracts the target company ID.
It serves as the entry point for the multi-agent workflow.
"""

import re
from typing import Dict
import sys
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from tools.graph_reader import get_node_by_id, get_node_by_name


# Mapping of common company names to IDs
COMPANY_ALIASES = {
    "tsmc": "2330",
    "台積電": "2330",
    "apple": "AAPL",
    "蘋果": "AAPL",
    "nvidia": "NVDA",
    "輝達": "NVDA",
    "amd": "AMD",
    "超微": "AMD",
    "intel": "INTC",
    "英特爾": "INTC",
    "asml": "ASML",
    "艾司摩爾": "ASML",
    "samsung": "5930",
    "三星": "5930",
    "qualcomm": "QCOM",
    "高通": "QCOM",
    "mediatek": "2454",
    "mtk": "2454",
    "聯發科": "2454",
    "tesla": "TSLA",
    "特斯拉": "TSLA",
    "microsoft": "MSFT",
    "微軟": "MSFT",
    "google": "GOOG",
    "谷歌": "GOOG",
    "amazon": "AMZN",
    "aws": "AMZN",
    "亞馬遜": "AMZN",
}


def extract_company_id(query: str) -> str:
    """
    Extract company ID from the user query.
    
    Args:
        query: User's natural language query
    
    Returns:
        Company ID string (defaults to "2330" for TSMC if not found)
    """
    query_lower = query.lower()
    
    # Check for direct ID mentions (e.g., "2330", "AAPL")
    id_pattern = r'\b([0-9]{4}|[A-Z]{2,4})\b'
    matches = re.findall(id_pattern, query.upper())
    for match in matches:
        node = get_node_by_id(match)
        if node:
            return match
    
    # Check for company name mentions
    for alias, company_id in COMPANY_ALIASES.items():
        if alias in query_lower:
            return company_id
    
    # Default to TSMC
    return "2330"


def supervisor_node(state: AgentState) -> Dict:
    """
    Supervisor Agent node function.
    
    Parses the query and extracts:
    - company_id
    - basic_info (company profile from graph)
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state dict
    """
    query = state.get("query", "")
    
    # Extract company ID
    company_id = extract_company_id(query)
    
    # Get basic info from graph
    node = get_node_by_id(company_id)
    basic_info = node if node else {
        "id": company_id,
        "name": "Unknown",
        "country": "Unknown",
        "category": "Unknown",
        "role": "Unknown",
        "tags": []
    }
    
    return {
        "company_id": company_id,
        "basic_info": basic_info
    }
