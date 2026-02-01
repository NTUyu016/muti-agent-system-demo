"""
Mock BigQuery Tool

This module simulates BigQuery queries for financial data.
In production, this would connect to actual BigQuery.
"""

import json
from typing import Dict, Optional
from pathlib import Path


_DATA_PATH = Path(__file__).parent.parent / "data" / "financials.json"
_financial_data: Optional[Dict] = None


def _load_data() -> Dict:
    """Load financial data from JSON file."""
    global _financial_data
    if _financial_data is None:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            _financial_data = json.load(f)
    return _financial_data


def query_financial_data(company_id: str) -> Optional[Dict]:
    """
    Query financial data for a company.
    
    Args:
        company_id: The company ID (e.g., "2330")
    
    Returns:
        Financial data dict or None if not found.
    
    Note: This is a mock implementation. In production, this would execute
    a BigQuery SQL query.
    """
    data = _load_data()
    return data.get(company_id)


def format_financial_summary(data: Dict) -> str:
    """
    Format financial data into a readable summary.
    
    Args:
        data: Financial data dict
    
    Returns:
        Formatted string summary.
    """
    if not data:
        return "No financial data available."
    
    revenue = data.get("revenue", {})
    gross_margin = data.get("gross_margin", {})
    net_income = data.get("net_income", {})
    
    summary = f"""
**{data.get('company_name', 'N/A')} Financial Summary ({data.get('fiscal_year', 'N/A')} {data.get('fiscal_quarter', 'N/A')})**

| Metric | Value | Change |
|--------|-------|--------|
| Revenue | {revenue.get('value', 'N/A'):,} {revenue.get('unit', '')} | YoY {revenue.get('yoy_growth', 'N/A')} |
| Gross Margin | {gross_margin.get('value', 'N/A')}% | QoQ {gross_margin.get('qoq_change', 'N/A')} |
| Operating Margin | {data.get('operating_margin', {}).get('value', 'N/A')}% | - |
| Net Income | {net_income.get('value', 'N/A'):,} {net_income.get('unit', '')} | YoY {net_income.get('yoy_growth', 'N/A')} |
| EPS | {data.get('eps', {}).get('value', 'N/A')} {data.get('eps', {}).get('unit', '')} | - |

**Revenue by Platform:**
"""
    for platform, pct in data.get("revenue_by_platform", {}).items():
        summary += f"- {platform}: {pct}\n"
    
    summary += "\n**Revenue by Technology:**\n"
    for tech, pct in data.get("revenue_by_technology", {}).items():
        summary += f"- {tech}: {pct}\n"
    
    capex = data.get("capex_guidance_2026", {})
    if capex:
        summary += f"\n**2026 CapEx Guidance:** {capex.get('range', 'N/A')} USD\n"
    
    return summary.strip()
