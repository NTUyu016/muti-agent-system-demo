"""
Reporter Agent - AI Supply Chain Analysis Report Template

Generates standardized reports following the TSMC Hackathon template format.
"""

from typing import Dict
from datetime import datetime
import json
import sys
import os
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from llm_config import invoke_llm, get_system_prompt, format_llm_prompt, logger


def load_extended_financial_data(company_id: str) -> Dict:
    """Load extended financial data with quarterly history."""
    try:
        data_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "data", 
            "financials_extended.json"
        )
        with open(data_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data.get(company_id, {})
    except Exception as e:
        logger.error(f"Failed to load extended financial data: {e}")
        return {}


def format_financial_table(company_id: str, finance_data: Dict) -> str:
    """
    Format financial data into the standardized table format.
    
    Generates a table with:
    - Calendar YQ: 2024Q3, 2024Q4, 2025Q1, 2025Q2, 2025Q3
    - Latest: QoQ, YoY
    - Three metrics: Revenue (USD), Gross Margin (%), DOI (days)
    """
    # Try to load extended data first
    extended_data = load_extended_financial_data(company_id)
    
    if not extended_data or "quarterly_data" not in extended_data:
        # Fallback to basic data
        return format_basic_financial_table(finance_data)
    
    company_name = extended_data.get("company_name", "Unknown")
    currency = extended_data.get("currency", "USD")
    quarterly_data = extended_data.get("quarterly_data", {})
    latest_changes = extended_data.get("latest_changes", {})
    latest_quarter = extended_data.get("latest_quarter", {})
    
    # Define quarter order
    quarters = ["2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3"]
    
    # Helper function to convert currency
    def convert_to_usd_billions(value, unit):
        if unit == "TWD":
            return value / 31_000_000_000  # TWD to USD billions
        else:
            return value / 1_000_000_000  # Already USD, convert to billions
    
    # Build revenue row
    revenue_row = [company_name, "Revenue (USD B)"]
    for q in quarters:
        if q in quarterly_data:
            rev = quarterly_data[q].get("revenue", {})
            value = convert_to_usd_billions(rev.get("value", 0), rev.get("unit", currency))
            revenue_row.append(f"{value:.2f}")
        else:
            revenue_row.append("-")
    revenue_row.append(latest_changes.get("revenue_qoq", "X"))
    revenue_row.append(latest_changes.get("revenue_yoy", "X"))
    
    # Build gross margin row
    gm_row = ["", "Gross Margin (%)"]
    for q in quarters:
        if q in quarterly_data:
            gm = quarterly_data[q].get("gross_margin", {})
            value = gm.get("value", 0)
            gm_row.append(f"{value:.2f}")
        else:
            gm_row.append("-")
    gm_row.append(latest_changes.get("gross_margin_qoq", "X"))
    gm_row.append(latest_changes.get("gross_margin_yoy", "X"))
    
    # Build DOI row
    doi_row = ["", "DOI (days)"]
    for q in quarters:
        if q in quarterly_data:
            doi = quarterly_data[q].get("doi_days", {})
            value = doi.get("value", 0)
            doi_row.append(f"{value:.1f}")
        else:
            doi_row.append("-")
    doi_row.append(latest_changes.get("doi_qoq", "X"))
    doi_row.append(latest_changes.get("doi_yoy", "X"))
    
    # Format as markdown table
    table = f"""| Company Financial Indices | Calendar YQ ||||| Latest || 
|---------------------------|---------|---------|---------|---------|---------|-----|-----|
|                           | 2024Q3  | 2024Q4  | 2025Q1  | 2025Q2  | 2025Q3  | QoQ | YoY |
| {revenue_row[0]} - {revenue_row[1]} | {revenue_row[2]} | {revenue_row[3]} | {revenue_row[4]} | {revenue_row[5]} | {revenue_row[6]} | {revenue_row[7]} | {revenue_row[8]} |
| {gm_row[1]} | {gm_row[2]} | {gm_row[3]} | {gm_row[4]} | {gm_row[5]} | {gm_row[6]} | {gm_row[7]} | {gm_row[8]} |
| {doi_row[1]} | {doi_row[2]} | {doi_row[3]} | {doi_row[4]} | {doi_row[5]} | {doi_row[6]} | {doi_row[7]} | {doi_row[8]} |
"""
    
    return table


def format_basic_financial_table(finance_data: Dict) -> str:
    """Fallback: Format basic financial table from simple data."""
    if not finance_data:
        return "*No financial data available.*\n"
    
    company_name = finance_data.get("company_name", "Unknown")
    revenue = finance_data.get("revenue", {})
    gm = finance_data.get("gross_margin", {})
    
    # Convert revenue
    currency = revenue.get("unit", "USD")
    rev_value = revenue.get("value", 0)
    if currency == "TWD":
        rev_usd = rev_value / 31_000_000_000
    else:
        rev_usd = rev_value / 1_000_000_000
    
    table = f"""| Company Financial Indices | Calendar YQ ||||| Latest || 
|---------------------------|---------|---------|---------|---------|---------|-----|-----|
|                           | 2024Q3  | 2024Q4  | 2025Q1  | 2025Q2  | 2025Q3  | QoQ | YoY |
| {company_name} - Revenue (USD B) | - | - | - | - | {rev_usd:.2f} | - | {revenue.get('yoy_growth', 'N/A')} |
| Gross Margin (%) | - | - | - | - | {gm.get('value', 'N/A')} | {gm.get('qoq_change', 'N/A')} | - |
| DOI (days) | - | - | - | - | - | X | X |

*Note: Historical quarterly data not available. Only latest quarter shown.*
"""
    return table


def extract_earnings_key_points(earnings_summary: str) -> str:
    """
    Extract or format earnings call summary to 5 key points.
    
    Uses LLM to distill the summary into exactly 5 concise bullet points.
    """
    if not earnings_summary or earnings_summary == "無法說會數據":
        return "*No earnings call data available.*\n"
    
    try:
        system_prompt = """你是專業的財報分析師，擅長提取法說會的關鍵資訊。
請將法說會內容濃縮成 **精確的 5 個要點**，每個要點應：
1. 簡潔有力（不超過一句話）
2. 數據導向（包含具體數字或百分比）
3. 前瞻性（關注未來展望）

以 markdown bullet points 格式輸出，不需要其他說明文字。"""
        
        user_prompt = f"請從以下法說會摘要中提取 5 個最關鍵的要點：\n\n{earnings_summary}"
        
        key_points = invoke_llm(system_prompt, user_prompt, temperature=0.2)
        return key_points
    except Exception as e:
        logger.error(f"Failed to extract key points: {e}")
        return earnings_summary


def extract_news_highlights(news_summary: str) -> str:
    """
    Extract news highlights (around 20 news items within 30 days).
    
    Uses LLM to format news into concise bullet points.
    """
    if not news_summary or news_summary == "無新聞數據":
        return "*No recent news available.*\n"
    
    try:
        system_prompt = """你是新聞分析師，請將新聞內容整理成易讀的條列格式。
每則新聞應包含：
- 📅 日期
- 📰 標題
- 📊 簡短摘要（一句話）

請保持客觀中立，按時間倒序排列。"""
        
        user_prompt = f"請整理以下新聞摘要（最近 30 天內）：\n\n{news_summary}"
        
        formatted_news = invoke_llm(system_prompt, user_prompt, temperature=0.1)
        return formatted_news
    except Exception as e:
        logger.error(f"Failed to format news: {e}")
        return news_summary


def format_supply_chain_analysis(sc_analysis: Dict) -> str:
    """
    Format supply chain analysis into three sections:
    1. Summary of target company status
    2. Vertical analysis (upstream suppliers, downstream customers)
    3. Horizontal analysis (competitors, partners)
    """
    summary = sc_analysis.get("summary", "")
    
    # Section 1: Summary
    section1 = f"**<1. Summary target company status>**\n\n{summary if summary else '*No summary available.*'}\n"
    
    # Section 2: Vertical analysis
    section2 = "\n**<2. Supply chain analysis - vertical>**\n\n"
    section2 += "*Analysis of upstream suppliers and downstream customers in the value chain.*\n\n"
    
    customers = sc_analysis.get("customers", [])
    suppliers = sc_analysis.get("suppliers", [])
    
    if customers:
        section2 += "**Key Customers (Downstream):**\n\n"
        for customer in customers[:8]:  # Top 8
            if isinstance(customer, dict):
                name = customer.get('name', 'Unknown')
                country = customer.get('country', '')
                category = customer.get('category', '')
                desc = customer.get('relationship_description', '')
                tags = ', '.join(customer.get('tags', []))
                section2 += f"- **{name}** ({country}, {category})\n"
                if tags:
                    section2 += f"  - *Tags:* {tags}\n"
                if desc:
                    section2 += f"  - {desc}\n"
            else:
                section2 += f"- {customer}\n"
        section2 += "\n"
    
    if suppliers:
        section2 += "**Key Suppliers (Upstream):**\n\n"
        for supplier in suppliers[:8]:  # Top 8
            if isinstance(supplier, dict):
                name = supplier.get('name', 'Unknown')
                country = supplier.get('country', '')
                category = supplier.get('category', '')
                desc = supplier.get('relationship_description', '')
                tags = ', '.join(supplier.get('tags', []))
                section2 += f"- **{name}** ({country}, {category})\n"
                if tags:
                    section2 += f"  - *Tags:* {tags}\n"
                if desc:
                    section2 += f"  - {desc}\n"
            else:
                section2 += f"- {supplier}\n"
        section2 += "\n"
    
    if not customers and not suppliers:
        section2 += "*No vertical supply chain data available.*\n\n"
    
    # Section 3: Horizontal analysis
    section3 = "**<3. Supply chain analysis - horizontal>**\n\n"
    section3 += "*Analysis of competitors and partners in the same industry segment.*\n\n"
    
    competitors = sc_analysis.get("competitors", [])
    partners = sc_analysis.get("partners", [])
    
    if competitors:
        section3 += "**Main Competitors:**\n\n"
        for competitor in competitors[:6]:  # Top 6
            if isinstance(competitor, dict):
                name = competitor.get('name', 'Unknown')
                country = competitor.get('country', '')
                category = competitor.get('category', '')
                tags = ', '.join(competitor.get('tags', []))
                section3 += f"- **{name}** ({country}, {category})\n"
                if tags:
                    section3 += f"  - *Tags:* {tags}\n"
            else:
                section3 += f"- {competitor}\n"
        section3 += "\n"
    
    if partners:
        section3 += "**Strategic Partners:**\n\n"
        for partner in partners[:6]:
            if isinstance(partner, dict):
                name = partner.get('name', 'Unknown')
                country = partner.get('country', '')
                category = partner.get('category', '')
                desc = partner.get('relationship_description', '')
                tags = ', '.join(partner.get('tags', []))
                section3 += f"- **{name}** ({country}, {category})\n"
                if tags:
                    section3 += f"  - *Tags:* {tags}\n"
                if desc:
                    section3 += f"  - {desc}\n"
            else:
                section3 += f"- {partner}\n"
        section3 += "\n"
    
    if not competitors and not partners:
        section3 += "*No horizontal supply chain data available.*\n\n"
    
    return section1 + section2 + section3


def generate_template_report(state: AgentState) -> str:
    """
    Generate AI Supply Chain Analysis Report following the standard template.
    
    Template structure:
    ┌─────────────────────────────────────────────┐
    │ AI Supply Chain Analysis Report             │
    │ Create date: 2026/xx/xx                     │
    ├─────────────────────────────────────────────┤
    │ Company: [Company Name]                     │
    │ Latest Earnings Call: [Year Quarter]       │
    ├─────────────────────────────────────────────┤
    │ Financial Status:                           │
    │ [3-metric table with 5 quarters + QoQ/YoY]  │
    ├─────────────────────────────────────────────┤
    │ AI Analysis:                                │
    │ ● Earnings Call (5 key points)              │
    │ ● News Summary (30 days, ~20 news)          │
    │ ● Supply Chain Analysis:                    │
    │   - Summary                                 │
    │   - Vertical (suppliers/customers)          │
    │   - Horizontal (competitors/partners)       │
    └─────────────────────────────────────────────┘
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
    
    # Determine latest earnings call quarter
    fiscal_year = finance_data.get("fiscal_year", "2025")
    fiscal_quarter = finance_data.get("fiscal_quarter", "Q4").replace("Q", "")
    latest_earnings = f"{fiscal_year} Q{fiscal_quarter}"
    
    # Check if extended data exists
    extended_data = load_extended_financial_data(company_id)
    if extended_data and "latest_quarter" in extended_data:
        lq = extended_data["latest_quarter"]
        latest_earnings = f"{lq.get('fiscal_year', fiscal_year)} {lq.get('fiscal_quarter', 'Q'+fiscal_quarter)}"
    
    # Build report
    report = f"""# AI Supply Chain Analysis Report

**Create date:** {datetime.now().strftime("%Y/%m/%d")}

---

**Company:** {company_name}

**Latest Earnings Call (Calendar Year):** {latest_earnings}

---

## Financial Status:

{format_financial_table(company_id, finance_data)}

---

## AI Analysis:

### ● Latest Earnings Call Transcript - QA Session Summary:

<5 key points>

{extract_earnings_key_points(earnings_summary)}

---

### ● News Summary:

<Latest key news within 30 days, around 20 news>

{extract_news_highlights(news_summary)}

---

### ● Supply Chain Analysis:

{format_supply_chain_analysis(sc_analysis)}

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
    logger.info("Reporter generating AI Supply Chain Analysis Report...")
    
    try:
        report = generate_template_report(state)
        logger.info("Template-based report generation completed")
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        report = f"Error generating report: {str(e)}"
    
    return {
        "final_report": report,
        "validation_status": True
    }
