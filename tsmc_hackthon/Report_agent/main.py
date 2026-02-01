"""
Multi-Agent System for Industry Analysis

Main entry point for the TSMC CareerHack Multi-Agent System prototype.
This system generates comprehensive analysis reports for target companies.

Usage:
    python main.py
    python main.py "分析 TSMC 2026 年展望"
    python main.py "請告訴我 Nvidia 的供應鏈關係"
"""

import sys
from graph import app


def run_analysis(query: str) -> str:
    """
    Run the multi-agent analysis pipeline.
    
    Args:
        query: User's natural language query
    
    Returns:
        Final Markdown report
    """
    # Initial state
    initial_state = {
        "query": query,
        "company_id": "",
        "basic_info": None,
        "finance_results": None,
        "earnings_call_summary": None,
        "news_summary": None,
        "supply_chain_analysis": None,
        "validation_status": None,
        "final_report": None
    }
    
    # Run the workflow
    print(f"\n{'='*60}")
    print(f"🚀 Multi-Agent System 啟動")
    print(f"📝 Query: {query}")
    print(f"{'='*60}\n")
    
    # Execute each step and track progress
    final_state = None
    for step in app.stream(initial_state):
        # Save the latest state
        final_state = step
        
        # Print progress
        for node_name, node_output in step.items():
            print(f"✅ {node_name} 完成")
            if node_name == "supervisor":
                print(f"   └─ 目標公司: {node_output.get('basic_info', {}).get('name', 'N/A')}")
    
    print(f"\n{'='*60}")
    print(f"📊 報告生成完成")
    print(f"{'='*60}\n")
    
    # Extract final_report from the last node output (reporter)
    if final_state:
        # The last step should be the reporter node
        for node_name, node_output in final_state.items():
            if "final_report" in node_output:
                return node_output.get("final_report", "Error: No report generated.")
    
    return "Error: No report generated."


def main():
    """Main entry point."""
    # Get query from command line or use default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "請分析台積電 (TSMC) 的 2026 年展望，包含財務、法說會重點、新聞與供應鏈分析。"
    
    # Run analysis
    report = run_analysis(query)
    
    # Print the report
    print(report)
    
    # Optionally save to file
    output_file = "output_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n💾 報告已儲存至: {output_file}")


if __name__ == "__main__":
    main()
