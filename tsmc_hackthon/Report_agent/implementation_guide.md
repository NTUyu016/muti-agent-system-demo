
# 2026 TSMC CareerHack: 智慧產業分析 Multi-Agent System 實作指引

這是一份針對 Vibe Coding (或開發者) 的實作指引，旨在快速建立一個基於 **LangGraph** 與 **Vertex AI** 的產業分析 Agent 原型。

---

## 1. 專案概述 (Project Overview)

本系統目標是自動化生成針對目標企業的「財務」、「新聞」與「供應鏈」分析報告。
核心採用 **Supervisor Pattern**，由一個 Root Agent 指揮多個專家 Agent 協作。

### 1.1 目錄結構建議
```
Report_agent/
├── .env                    # API Key 設定 (GEMINI_API_KEY, PROJECT_ID...)
├── supply_chain_graph.json # 供應鏈圖譜數據 (Nodes/Edges)
├── main.py                 # 程式進入點 (Entry Point)
├── graph.py                # LangGraph 定義 (State & Workflow)
├── agents/                 # 各個 Agent 的實作
│   ├── supervisor.py       # Root Agent (Router)
│   ├── finance.py          # 財務分析 Agent
│   ├── news.py             # 新聞分析 Agent
│   └── supply_chain.py     # 供應鏈推論 Agent
├── tools/                  # 工具集
│   ├── bigquery_tool.py    # (Mock) 查詢 BigQuery
│   ├── rag_tool.py         # (Mock) 查詢 Vector DB
│   └── graph_reader.py     # 讀取 JSON Config
└── utils/
    └── formatter.py        # Markdown 格式化工具
```

---

## 2. 環境設定 (Environment Setup)

### 2.1 依賴套件
```bash
pip install langgraph langchain-google-vertexai langchain-core pydantic networkx
```

### 2.2 供應鏈數據 (Data Source)
系統依賴 `supply_chain_graph.json` 來理解產業關係。
*   **檔案位置**: 專案根目錄
*   **格式**: JSON (包含 `nodes` 與 `edges`)
*   **讀取方式**: 透過 `tools/graph_reader.py` 載入並構建 `NetworkX` 圖或是純字典查詢。

---

## 3. 核心組件定義 (Core Components)

### 3.1 狀態定義 (AgentState)
這是所有 Agent 共享的記憶體結構，確保資料在傳遞過程中不丟失。

```python
from typing import TypedDict, List, Dict, Annotated
import operator

class AgentState(TypedDict):
    # 任務輸入
    query: str                  # 使用者原始問題
    company_id: str             # 目標公司 ID (e.g., "2330")
    
    # 各 Agent 產出的中間資料
    basic_info: Dict            # 公司基本資料
    finance_results: Dict       # 財務數據摘要
    news_summary: str           # 新聞摘要
    supply_chain_risks: List[str] # 供應鏈風險推論
    
    # 最終輸出
    final_report: str           # 整合後的完整 Markdown 報告
    
    # 流程控制
    next_step: str              # 下一步要執行的 Agent
```

### 3.2 角色與職責 (Roles & Responsibilities)

#### **A. Supervisor (Root)**
*   **任務**: 接收 `query`，判斷需要調用哪些專家。通常是依序調用：`Finance -> News -> SupplyChain -> Reporter`。
*   **實作**: 使用 LLM 進行路由判斷 (Router) 或固定流程 (State Machine)。可以先做固定流程版本。

#### **B. Financial Analyst**
*   **任務**: 負責數據。
*   **Mock 行為**: 模擬從 BigQuery 撈出 TSMC 的 `Gross Margin` 和 `Revenue YoY`。

#### **C. News Analyst**
*   **任務**: 負責非結構化文本。
*   **Mock 行為**: 模擬從 RAG 撈出最近的新聞（如「CoWoS 產能擴充」、「高雄設廠」）。

#### **D. Supply Chain Expert (重點)**
*   **任務**: 讀取 `supply_chain_graph.json`，根據 `company_id` 找出其上游 (Supplier) 與下游 (Client)。
*   **邏輯**:
    1. 載入 JSON。
    2. 找到目標公司節點 (e.g., TSMC)。
    3. 遍歷 `edges`，找出所有連接到該節點的鄰居。
    4. 分析鄰居的 `relation` (Client/Supplier) 與 `tags`。
    5. 生成推論：例如「主要客戶 Apple 銷量下滑可能影響 TSMC 營收」。

---

## 4. 實作步驟指引 (Step-by-Step Guide)

1.  **準備資料**: 確保 `supply_chain_graph.json` 已經存在。
2.  **建立工具**: 撰寫 `graph_reader.py`，寫一個函數 `get_related_companies(company_id)` 回傳該公司的上下游名單。
3.  **建立 Agent**: 使用 `LangChain` 的 `@tool` 裝飾器定義工具，並綁定到 `Gemini Pro` 模型上。
4.  **定義流程**: 使用 `StateGraph` 定義節點與邊。
    ```python
    workflow = StateGraph(AgentState)
    workflow.add_node("financial_agent", financial_node)
    workflow.add_node("news_agent", news_node)
    workflow.add_node("supply_chain_agent", supply_chain_node)
    workflow.add_node("reporter", reporter_node)
    
    # 簡單的循序執行
    workflow.set_entry_point("financial_agent")
    workflow.add_edge("financial_agent", "news_agent")
    workflow.add_edge("news_agent", "supply_chain_agent")
    workflow.add_edge("supply_chain_agent", "reporter")
    workflow.add_edge("reporter", END)
    ```
5.  **測試**: 輸入 `query="分析 TSMC 2026 年展望"`, 觀察最終 `final_report` 是否包含財務、新聞與供應鏈資訊。

---

## 5. 提示詞工程 (System Prompts)

給 **Supply Chain Agent** 的提示詞範例：
> "你是一個半導體供應鏈專家。你擁有一個包含 Apple, Nvidia, ASML 等公司的知識圖譜。
> 當被問及特定公司時，請查詢它的客戶與供應商，並分析潛在的風險傳導。
> 例如：如果客戶是以消費性電子為主的 Apple，需考慮終端市場需求疲軟的風險。"

---

此指引可直接提供給 Coding Agent (Vibe Coding) 進行程式碼生成。
