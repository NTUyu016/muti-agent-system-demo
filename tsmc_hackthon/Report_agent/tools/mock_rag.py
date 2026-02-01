"""
Mock RAG Tool

This module simulates RAG (Retrieval Augmented Generation) queries
for earnings calls and news data. In production, this would connect
to a vector database like ChromaDB or FAISS.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


_DATA_DIR = Path(__file__).parent.parent / "data"
_earnings_data: Optional[Dict] = None
_news_data: Optional[List] = None


def _load_earnings_data() -> Dict:
    """Load earnings call data from JSON file."""
    global _earnings_data
    if _earnings_data is None:
        with open(_DATA_DIR / "earnings_calls.json", "r", encoding="utf-8") as f:
            _earnings_data = json.load(f)
    return _earnings_data


def _load_news_data() -> List:
    """Load news data from JSON file."""
    global _news_data
    if _news_data is None:
        with open(_DATA_DIR / "news.json", "r", encoding="utf-8") as f:
            _news_data = json.load(f)
    return _news_data


def query_earnings_calls(company_id: str, limit: int = 2) -> List[Dict]:
    """
    Query earnings call data for a company.
    
    Args:
        company_id: The company ID (e.g., "2330")
        limit: Maximum number of results to return
    
    Returns:
        List of earnings call summaries.
    
    Note: This is a mock implementation. In production, this would perform
    a semantic search over embedded earnings call transcripts.
    """
    data = _load_earnings_data()
    calls = data.get(company_id, [])
    return calls[:limit]


def format_earnings_call_summary(calls: List[Dict]) -> str:
    """
    Format earnings call data into a readable summary.
    
    Args:
        calls: List of earnings call dicts
    
    Returns:
        Formatted string summary.
    """
    if not calls:
        return "No earnings call data available."
    
    summary = "## 法說會重點摘要\n\n"
    
    for call in calls:
        summary += f"### {call.get('title', 'N/A')} ({call.get('date', 'N/A')})\n\n"
        
        summary += "**Key Points:**\n"
        for point in call.get("key_points", []):
            summary += f"- {point}\n"
        
        summary += f"\n**Outlook:** {call.get('outlook', 'N/A')}\n\n"
        
        quotes = call.get("management_quotes", [])
        if quotes:
            summary += "**Management Quotes:**\n"
            for quote in quotes:
                summary += f"> {quote}\n\n"
        
        summary += "---\n\n"
    
    return summary.strip()


def query_news(company_id: str, limit: int = 5) -> List[Dict]:
    """
    Query news articles related to a company.
    
    Args:
        company_id: The company ID (e.g., "2330")
        limit: Maximum number of results to return
    
    Returns:
        List of news article summaries.
    
    Note: This is a mock implementation. In production, this would perform
    a semantic search over embedded news articles.
    """
    data = _load_news_data()
    # Filter news that mention the company
    related = [
        article for article in data
        if company_id in article.get("related_companies", [])
    ]
    return related[:limit]


def format_news_summary(articles: List[Dict]) -> str:
    """
    Format news data into a readable summary.
    
    Args:
        articles: List of news article dicts
    
    Returns:
        Formatted string summary.
    """
    if not articles:
        return "No recent news available."
    
    summary = "## 近期新聞摘要\n\n"
    
    for article in articles:
        sentiment_emoji = {
            "positive": "🟢",
            "neutral": "🟡",
            "negative": "🔴"
        }.get(article.get("sentiment", "neutral"), "🟡")
        
        summary += f"### {sentiment_emoji} {article.get('title', 'N/A')}\n"
        summary += f"*{article.get('source', 'N/A')} | {article.get('date', 'N/A')}*\n\n"
        summary += f"{article.get('summary', 'N/A')}\n\n"
        summary += "---\n\n"
    
    return summary.strip()
