"""
Reporter Agent (Template-Based)

Generates AI Supply Chain Analysis Report following the standardized template.
"""

from typing import Dict
from datetime import datetime
import sys
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from llm_config import invoke_llm, get_system_prompt, logger


def format_financial_status_table(finance_data: Dict) -> str:
    """
    Format financial data into a time-series table.
    
    Expected format:
    - Calendar YQ: 2024Q3, 2024Q4, 2025Q1, 2025Q2, 2025Q3
    - Latest: QoQ, YoY
    - Metrics: Revenue (USD), Gross Margin (%), DOI (days)
    """
    if not finance_data:
        return "No financial data available."
    
    company_name = finance_data.get("company_name", "Unknown")
    
    # Extract key metrics
    revenue = finance_data.get("revenue", {})
    gross_margin = finance_data.get("gross_margin", {})
    operating_margin = finance_data.get("operating_margin", {})
    
    # Format revenue value (convert to billions for readability)
    revenue_value = revenue.get("value", 0)
    revenue_unit = revenue.get("unit", "USD")
    
    # Convert TWD to USD if needed (approximate rate: 1 USD = 31 TWD)
    if revenue_unit == "TWD":
        revenue_usd = revenue_value / 31_000_000_000  # Convert to billions USD
    else:
        revenue_usd = revenue_value / 1_000_000_000  # Already in USD, convert to billions
    
    revenue_yoy = revenue.get("yoy_growth", "N/A")
    gm_value = gross_margin.get("value", "N/A")
    gm_qoq = gross_margin.get("qoq_change", "N/A")
    
    # Build table (simplified version - in real scenario, you'd have historical quarters)
    table = f"""
**Financial Status:**

| Company Financial Indices | 2024Q3 | 2024Q4 | 2025Q1 | 2025Q2 | 2025Q3 | QoQ | YoY |
|---------------------------|--------|--------|--------|--------|--------|-----|-----|
| {company_name} - Revenue (USD B) | - | - | - | - | {revenue_usd:.2f}B | - | {revenue_yoy} |
| Gross Margin (%) | - | - | - | - | {gm_value}% | {gm_qoq} | - |
| DOI (days) | - | - | - | - | - | X | X |

*Note: Historical quarterly data not available in current dataset. Only latest quarter shown.*
"""
    return table


def generate_template_report(state: AgentState) -> str:
    """
    Generate report following the AI Supply Chain Analysis Report template.
    
    Template structure:
    1. Header (Company, Latest Earnings Call, Create date)
    2. Financial Status (3 metrics table)
    3. AI Analysis:
       - Latest Earnings Call Transcript - QA Session Summary (<5 key points>)
       - News Summary (<Latest key news within 30 days, around 20 news>)
       - Supply Chain Analysis:
         <1. Summary target company status>
         <2. Supply chain analysis - vertical>
         <3. Supply chain analysis - horizontal>
    """
    # Extract all data
    basic_info = state.get("basic_info", {})
    company_name = basic_info.get("name", "Unknown")
    company_id = state.get("company_id", "Unknown")
    
    finance_results = state.get("finance_results", {})
    finance_data = finance_results.get("raw_data", {})
    
    earnings_summary = state.get("earnings_call_summary", "")
    news_summary = state.get("news_summary", "")
    sc_analysis = state.get("supply_chain_analysis", {})
    
    # Get latest earnings call info
    fiscal_info = finance_data.get("fiscal_year", "2025") + " Q" + finance_data.get("fiscal_quarter", "4").replace("Q", "")
    
    # Generate report
    report = f"""# AI Supply Chain Analysis Report

**Create date:** {datetime.now().strftime("%Y/%m/%d")}

---

**Company:** {company_name}

**Latest Earnings Call (Calendar Year):** {fiscal_info}

---

## Financial Status

"""
    
    # Add financial status table
    report += format_financial_status_table(finance_data)
    
    report += """

---

## AI Analysis

### ● Latest Earnings Call Transcript - QA Session Summary:

"""
    
    # Extract 5 key points from earnings call
    report += earnings_summary if earnings_summary else "<5 key points>\n\n*No earnings call data available.*"
    
    report += """

---

### ● News Summary:

<Latest key news within 30 days, around 20 news>

"""
    
    report += news_summary if news_summary else "*No recent news available.*"
    
    report += """

---

### ● Supply Chain Analysis:

**<1. Summary target company status>**

"""
    
    # Add supply chain summary
    sc_summary = sc_analysis.get("summary", "No supply chain data available.")
    report += sc_summary
    
    report += """

**<2. Supply chain analysis - vertical>**

*Analysis of upstream suppliers and downstream customers in the value chain.*

"""
    
    # Vertical analysis would go here
    customers = sc_analysis.get("customers", [])
    suppliers = sc_analysis.get("suppliers", [])
    
    if customers:
        report += "\n**Key Customers:**\n"
        for customer in customers[:5]:  # Top 5
            report += f"- {customer}\n"
    
    if suppliers:
        report += "\n**Key Suppliers:**\n"
        for supplier in suppliers[:5]:  # Top 5
            report += f"- {supplier}\n"
    
    report += """

**<3. Supply chain analysis - horizontal>**

*Analysis of competitors and partners in the same industry segment.*

"""
    
    # Horizontal analysis
    competitors = sc_analysis.get("competitors", [])
    if competitors:
        report += "\n**Main Competitors:**\n"
        for competitor in competitors[:5]:
            report += f"- {competitor}\n"
    
    report += """

---

*此報告由 Multi-Agent System 自動生成，結合結構化數據與 AI 分析，僅供參考。*
"""
    
    return report


def reporter_node(state: AgentState) -> Dict:
    """
    Reporter Agent node function (Template-based).
    
    Generates a standardized AI Supply Chain Analysis Report.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state dict with final_report
    """
    logger.info("Reporter generating template-based report...")
    
    try:
        report = generate_template_report(state)
        logger.info("Template-based report generation completed")
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        report = f"Error generating report: {str(e)}"
    
    return {
        "final_report": report,
        "validation_status": True
    }
