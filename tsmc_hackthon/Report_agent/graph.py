"""
LangGraph Workflow Definition

This module defines the StateGraph workflow that orchestrates all agents.
"""

from langgraph.graph import StateGraph, END

from agent_state import AgentState
from agents.supervisor import supervisor_node
from agents.finance import financial_analyst_node
from agents.earnings_call import earnings_call_analyst_node
from agents.news import news_agent_node
from agents.supply_chain import supply_chain_expert_node
from agents.reporter import reporter_node


def create_workflow():
    """
    Create and compile the multi-agent workflow.
    
    The workflow follows this sequence:
    1. supervisor -> Parse query, extract company_id
    2. financial_agent -> Get financial data
    3. earnings_call_agent -> Get earnings call summaries
    4. news_agent -> Get recent news
    5. supply_chain_agent -> Analyze supply chain
    6. reporter -> Generate final report
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (each agent)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("financial_agent", financial_analyst_node)
    workflow.add_node("earnings_call_agent", earnings_call_analyst_node)
    workflow.add_node("news_agent", news_agent_node)
    workflow.add_node("supply_chain_agent", supply_chain_expert_node)
    workflow.add_node("reporter", reporter_node)
    
    # Define edges (sequential execution)
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "financial_agent")
    workflow.add_edge("financial_agent", "earnings_call_agent")
    workflow.add_edge("earnings_call_agent", "news_agent")
    workflow.add_edge("news_agent", "supply_chain_agent")
    workflow.add_edge("supply_chain_agent", "reporter")
    workflow.add_edge("reporter", END)
    
    # Compile the graph
    return workflow.compile()


# Pre-compiled workflow for easy import
app = create_workflow()
