"""
Supply Chain Expert Agent (LLM-Powered)

This agent analyzes supply chain relationships using both structured data
and LLM-powered reasoning for risk assessment and insights.
"""

from typing import Dict, List
import sys
import json
sys.path.append(str(__file__).rsplit("\\", 2)[0])

from agent_state import AgentState
from tools.graph_reader import get_node_by_id, get_related_companies
from llm_config import invoke_llm, get_system_prompt, format_llm_prompt, logger


def format_supply_chain_data(
    company_info: Dict,
    related: Dict[str, List[Dict]]
) -> str:
    """
    Format supply chain data for LLM analysis.
    
    Args:
        company_info: Target company node info
        related: Dict with customers, suppliers, partners, competitors
    
    Returns:
        Formatted data string for LLM
    """
    data = {
        "company": {
            "name": company_info.get("name"),
            "country": company_info.get("country"),
            "category": company_info.get("category"),
            "role": company_info.get("role"),
            "tags": company_info.get("tags", [])
        },
        "customers": [
            {
                "name": c.get("name"),
                "country": c.get("country"),
                "category": c.get("category"),
                "tags": c.get("tags", []),
                "relationship": c.get("relationship_description")
            }
            for c in related.get("customers", [])
        ],
        "suppliers": [
            {
                "name": s.get("name"),
                "country": s.get("country"),
                "category": s.get("category"),
                "tags": s.get("tags", []),
                "relationship": s.get("relationship_description")
            }
            for s in related.get("suppliers", [])
        ],
        "partners": [
            {
                "name": p.get("name"),
                "country": p.get("country"),
                "category": p.get("category"),
                "relationship": p.get("relationship_description")
            }
            for p in related.get("partners", [])
        ],
        "competitors": [
            {
                "name": comp.get("name"),
                "country": comp.get("country"),
                "tags": comp.get("tags", [])
            }
            for comp in related.get("competitors", [])
        ]
    }
    
    return json.dumps(data, indent=2, ensure_ascii=False)


def generate_llm_analysis(company_info: Dict, related: Dict[str, List[Dict]]) -> str:
    """
    Use LLM to generate supply chain risk analysis.
    
    Args:
        company_info: Target company info
        related: Related companies data
    
    Returns:
        LLM-generated analysis in Markdown format
    """
    try:
        # Format data for LLM
        data_str = format_supply_chain_data(company_info, related)
        
        # Create prompt
        user_prompt = format_llm_prompt(
            """請基於以下供應鏈數據，進行深入的風險分析：

{data}

請提供：
1. **供應鏈結構分析**：客戶、供應商、合作夥伴的分布與特徵
2. **關鍵風險識別**：
   - 地緣政治風險（基於國家分布）
   - 客戶集中度風險
   - 供應商依賴風險
   - 技術依賴風險
3. **競爭態勢分析**：與主要競爭者的比較
4. **風險傳導路徑**：潛在的風險如何影響目標公司

請以 Markdown 格式輸出，包含清晰的章節標題。
資料來源：supply_chain_graph.json""",
            data=data_str
        )
        
        # Invoke LLM
        system_prompt = get_system_prompt("supply_chain_analyst")
        analysis = invoke_llm(system_prompt, user_prompt, temperature=0.2)
        
        return analysis
    
    except Exception as e:
        logger.error(f"LLM analysis failed: {str(e)}")
        # Fallback to rule-based analysis
        return generate_fallback_analysis(company_info, related)


def generate_fallback_analysis(
    company_info: Dict,
    related: Dict[str, List[Dict]]
) -> str:
    """
    Fallback rule-based analysis when LLM is unavailable.
    
    Args:
        company_info: Target company info
        related: Related companies data
    
    Returns:
        Rule-based analysis in Markdown format
    """
    company_name = company_info.get("name", "Unknown")
    country = company_info.get("country", "Unknown")
    
    summary = f"## 供應鏈分析：{company_name}\n\n"
    summary += f"**公司國別：** {country}\n"
    summary += f"**產業類別：** {company_info.get('category', 'N/A')}\n"
    summary += f"**標籤：** {', '.join(company_info.get('tags', []))}\n\n"
    
    # Customers
    customers = related.get("customers", [])
    if customers:
        summary += "### 主要客戶 (Customers)\n\n"
        summary += "| 公司 | 國家 | 類別 | 關係描述 |\n"
        summary += "|------|------|------|----------|\n"
        for c in customers:
            summary += f"| {c.get('name', 'N/A')} | {c.get('country', 'N/A')} | {c.get('category', 'N/A')} | {c.get('relationship_description', 'N/A')} |\n"
        summary += "\n"
    
    # Suppliers
    suppliers = related.get("suppliers", [])
    if suppliers:
        summary += "### 主要供應商 (Suppliers)\n\n"
        summary += "| 公司 | 國家 | 類別 | 關係描述 |\n"
        summary += "|------|------|------|----------|\n"
        for s in suppliers:
            summary += f"| {s.get('name', 'N/A')} | {s.get('country', 'N/A')} | {s.get('category', 'N/A')} | {s.get('relationship_description', 'N/A')} |\n"
        summary += "\n"
    
    # Partners
    partners = related.get("partners", [])
    if partners:
        summary += "### 合作夥伴 (Partners)\n\n"
        summary += "| 公司 | 國家 | 類別 | 關係描述 |\n"
        summary += "|------|------|------|----------|\n"
        for p in partners:
            summary += f"| {p.get('name', 'N/A')} | {p.get('country', 'N/A')} | {p.get('category', 'N/A')} | {p.get('relationship_description', 'N/A')} |\n"
        summary += "\n"
    
    # Competitors
    competitors = related.get("competitors", [])
    if competitors:
        summary += "### 主要競爭者 (Competitors)\n\n"
        summary += "| 公司 | 國家 | 標籤 |\n"
        summary += "|------|------|------|\n"
        for comp in competitors:
            tags = ", ".join(comp.get("tags", []))
            summary += f"| {comp.get('name', 'N/A')} | {comp.get('country', 'N/A')} | {tags} |\n"
        summary += "\n"
    
    # Risk Analysis
    summary += "### 風險分析\n\n"
    
    # Geographic concentration risk
    customer_countries = set(c.get("country") for c in customers if c.get("country"))
    supplier_countries = set(s.get("country") for s in suppliers if s.get("country"))
    
    if len(customer_countries) <= 2 and customers:
        summary += f"- **客戶集中度風險：** 主要客戶集中於 {', '.join(customer_countries)}，地緣政治風險需關注。\n"
    
    if "USA" in supplier_countries and "Netherlands" in supplier_countries:
        summary += "- **設備供應風險：** 關鍵設備供應商位於美國與荷蘭，受出口管制政策影響。\n"
    
    # Customer dependency
    hpc_customers = [c for c in customers if "HPC" in str(c.get("tags", [])) or "AI" in str(c.get("tags", []))]
    if hpc_customers:
        customer_names = [c.get("name") for c in hpc_customers[:3]]
        summary += f"- **AI/HPC 依賴：** {', '.join(customer_names)} 為主要 AI 晶片客戶，需求週期性波動風險。\n"
    
    summary += "\n*資料來源：supply_chain_graph.json*\n"
    
    return summary


def supply_chain_expert_node(state: AgentState) -> Dict:
    """
    Supply Chain Expert Agent node function (LLM-powered).
    
    Analyzes supply chain relationships and generates risk assessment
    using LLM for deeper insights.
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state dict with supply_chain_analysis
    """
    company_id = state.get("company_id", "2330")
    
    logger.info(f"Supply Chain Expert analyzing company: {company_id}")
    
    # Get company info
    company_info = get_node_by_id(company_id)
    if not company_info:
        logger.warning(f"No company info found for {company_id}")
        return {
            "supply_chain_analysis": {
                "summary": f"No supply chain data available for company {company_id}.",
                "customers": [],
                "suppliers": [],
                "partners": [],
                "competitors": []
            }
        }
    
    # Get related companies
    related = get_related_companies(company_id)
    
    # Generate analysis (LLM-powered with fallback)
    try:
        summary = generate_llm_analysis(company_info, related)
        logger.info("LLM-powered supply chain analysis completed")
    except Exception as e:
        logger.error(f"Falling back to rule-based analysis: {str(e)}")
        summary = generate_fallback_analysis(company_info, related)
    
    return {
        "supply_chain_analysis": {
            "summary": summary,
            "customers": related.get("customers", []),
            "suppliers": related.get("suppliers", []),
            "partners": related.get("partners", []),
            "competitors": related.get("competitors", [])
        }
    }
