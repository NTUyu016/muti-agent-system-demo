"""
LLM Configuration and Utilities

This module provides centralized LLM configuration and helper functions
for all agents that need to interact with Gemini.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMConfig:
    """Centralized LLM configuration."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        
        self.model_name = "models/gemini-2.5-pro"  # Full model path for Gemini 2.5 Pro
        self.temperature = 0.1  # Low temperature for factual analysis
        self.max_tokens = 8192  # Increased for full report generation
        
    def get_llm(self, temperature: Optional[float] = None) -> ChatGoogleGenerativeAI:
        """
        Get configured LLM instance.
        
        Args:
            temperature: Optional temperature override
        
        Returns:
            Configured ChatGoogleGenerativeAI instance
        """
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in .env file.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
        
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=temperature or self.temperature,
            max_tokens=self.max_tokens
        )


# Global LLM config instance
llm_config = LLMConfig()


def invoke_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: Optional[float] = None,
    max_retries: int = 3
) -> str:
    """
    Invoke LLM with retry logic and error handling.
    
    Args:
        system_prompt: System instruction for the LLM
        user_prompt: User query/input
        temperature: Optional temperature override
        max_retries: Maximum number of retry attempts
    
    Returns:
        LLM response text
    
    Raises:
        Exception: If all retry attempts fail
    """
    llm = llm_config.get_llm(temperature)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    for attempt in range(max_retries):
        try:
            logger.info(f"LLM invocation attempt {attempt + 1}/{max_retries}")
            response = llm.invoke(messages)
            
            # Debug logging
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response content type: {type(response.content)}")
            logger.info(f"LLM response received ({len(str(response.content))} chars)")
            
            # Handle different response types
            content = ""
            if hasattr(response, 'content'):
                content = str(response.content) if response.content else ""
            
            if not content:
                logger.warning("Empty response content received from LLM")
                if hasattr(response, 'response_metadata'):
                    logger.info(f"Response metadata: {response.response_metadata}")
            
            return content
        
        except Exception as e:
            logger.error(f"LLM invocation failed (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"LLM invocation failed after {max_retries} attempts: {str(e)}")
            # Wait before retry (exponential backoff)
            import time
            time.sleep(2 ** attempt)
    
    return ""


def format_llm_prompt(template: str, **kwargs) -> str:
    """
    Format prompt template with variables.
    
    Args:
        template: Prompt template with {variable} placeholders
        **kwargs: Variables to fill in the template
    
    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing variable in prompt template: {e}")
        raise


# System prompts for different agents
SYSTEM_PROMPTS = {
    "earnings_call_analyst": """你是一位專業的財報分析師，專門分析企業法說會內容。
你的任務是：
1. 提取法說會中的關鍵資訊（營運數據、未來展望、管理層評論）
2. 識別重要的前瞻性陳述（forward-looking statements）
3. 以結構化、客觀的方式呈現資訊
4. 標註資訊來源（source_file）

請以專業、精確的語言撰寫，避免主觀臆測。""",
    
    "news_analyst": """你是一位產業新聞分析師，專門分析半導體產業新聞。
你的任務是：
1. 識別新聞的關鍵事件與影響
2. 判斷新聞情緒（正面/中性/負面）
3. 分析對相關公司的潛在影響
4. 標註資訊來源（source_file）

請保持客觀中立，基於事實進行分析。""",
    
    "supply_chain_analyst": """你是一位供應鏈風險分析專家，專注於半導體產業。
你的任務是：
1. 分析供應鏈關係（客戶、供應商、合作夥伴）
2. 識別潛在風險（地緣政治、技術依賴、客戶集中度）
3. 評估風險傳導路徑
4. 提供可行的風險緩解建議

請基於數據進行推論，避免過度推測。""",
    
    "reporter": """你是一位資深產業分析報告撰寫者。
你的任務是：
1. 整合財務、法說會、新聞、供應鏈等多維度資訊
2. 撰寫結構清晰、邏輯連貫的分析報告
3. 提供有洞察力的總結與建議
4. 確保所有陳述有數據支持

請以專業、易讀的 Markdown 格式撰寫報告。"""
}


def get_system_prompt(agent_type: str) -> str:
    """
    Get system prompt for a specific agent type.
    
    Args:
        agent_type: Type of agent (e.g., 'earnings_call_analyst')
    
    Returns:
        System prompt string
    """
    return SYSTEM_PROMPTS.get(agent_type, "You are a helpful AI assistant.")
