# Multi-Agent System for Industry Analysis

**TSMC CareerHack 2026 - AI Supply Chain Analysis Report Generator**

## 📊 Project Overview

This is an intelligent multi-agent system designed for the **TSMC 2026 CareerHack** competition. The system automatically generates comprehensive **AI Supply Chain Analysis Reports** by integrating financial data, earnings call transcripts, news, and supply chain analysis using LangGraph and Google Gemini AI.

## 🚀 Features

- **Multi-Agent Architecture**: Built with LangGraph for orchestrating multiple specialized agents
- **Automated Report Generation**: Produces standardized analysis reports following TSMC template format
- **AI-Powered Analysis**: Leverages Google Gemini 2.5 Pro for intelligent insights
- **Supply Chain Risk Analysis**: Analyzes vertical (customers/suppliers) and horizontal (competitors/partners) relationships
- **Financial Trend Analysis**: Tracks quarterly performance with QoQ and YoY comparisons

## 🏗️ Architecture

The system consists of 6 specialized agents:

1. **Supervisor Agent**: Parses user queries and identifies target companies
2. **Financial Analyst**: Retrieves and analyzes financial data
3. **Earnings Call Analyst**: Extracts key points from earnings call transcripts
4. **News Agent**: Summarizes recent industry news
5. **Supply Chain Expert**: Performs risk analysis on supply chain relationships
6. **Reporter**: Generates the final comprehensive report

## 📋 Report Template

The generated report follows this structure:

```
┌─────────────────────────────────────────────┐
│ # AI Supply Chain Analysis Report          │
│ Create date: YYYY/MM/DD                     │
├─────────────────────────────────────────────┤
│ Company: [Company Name]                     │
│ Latest Earnings Call: [Year Quarter]       │
├─────────────────────────────────────────────┤
│ ## Financial Status                         │
│   - 5 Quarters Trend (2024Q3 - 2025Q3)      │
│   - Revenue (USD B) + QoQ/YoY               │
│   - Gross Margin (%) + QoQ/YoY              │
│   - DOI (days) + QoQ/YoY                    │
├─────────────────────────────────────────────┤
│ ## AI Analysis                              │
│   ● Earnings Call (5 key points)            │
│   ● News Summary (30 days)                  │
│   ● Supply Chain Analysis:                  │
│     - Status Summary                        │
│     - Vertical Analysis (Customers/Suppliers)│
│     - Horizontal Analysis (Competitors)     │
└─────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

- **Python 3.8+**
- **LangGraph**: Multi-agent workflow orchestration
- **Google Gemini 2.5 Pro**: LLM for AI-powered analysis
- **LangChain**: LLM integration framework

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/NTUyu016/muti-agent-system-demo.git
cd muti-agent-system-demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## 🚦 Usage

### Basic Usage

Run the system with the default query (TSMC analysis):
```bash
python main.py
```

### Custom Query

Analyze a specific company:
```bash
python main.py "請分析 Nvidia 的供應鏈關係"
python main.py "分析 Apple 的財務表現"
```

### Test LLM Connection

Verify your Gemini API setup:
```bash
python test_llm.py
```

## 📁 Project Structure

```
Report_agent/
├── agents/                  # Agent implementations
│   ├── supervisor.py       # Query parsing & company identification
│   ├── finance.py          # Financial data analysis
│   ├── earnings_call.py    # Earnings call analysis
│   ├── news.py             # News summarization
│   ├── supply_chain.py     # Supply chain risk analysis
│   └── reporter.py         # Report generation
├── data/                    # Data files
│   ├── financials_extended.json  # Quarterly financial data
│   ├── earnings_calls.json       # Earnings call transcripts
│   ├── news.json                 # Recent news articles
│   └── supply_chain_graph.json   # Supply chain relationships
├── tools/                   # Utility tools
│   ├── mock_bigquery.py    # Mock data retrieval
│   └── pdf_extractor.py    # PDF content extraction
├── graph.py                 # LangGraph workflow definition
├── main.py                  # Main entry point
├── agent_state.py           # State management
├── llm_config.py            # LLM configuration
└── output_report.md         # Generated report output
```

## 📊 Data Structure

### Financial Data

The system supports quarterly financial data with the following metrics:
- **Revenue**: Quarterly revenue in USD billions
- **Gross Margin**: Profitability metric in percentage
- **DOI (Days of Inventory)**: Inventory efficiency metric

Example data structure:
```json
{
  "2330": {
    "company_name": "TSMC",
    "quarterly_data": {
      "2025Q3": {
        "revenue": {"value": 868500000000, "unit": "TWD"},
        "gross_margin": {"value": 59.0, "unit": "%"},
        "doi_days": {"value": 82, "unit": "days"}
      }
    },
    "latest_changes": {
      "revenue_qoq": "29.0%",
      "revenue_yoy": "38.8%"
    }
  }
}
```

## 🔑 Environment Variables

Create a `.env` file with the following:

```env
# Required: Your Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Google Cloud Project ID (for future BigQuery integration)
# PROJECT_ID=your_project_id
```

Get your Gemini API key from: https://aistudio.google.com/app/apikey

## 🎯 Key Features

### 1. Financial Status Analysis
- ✅ Multi-quarter trend visualization
- ✅ QoQ (Quarter-over-Quarter) and YoY (Year-over-Year) comparisons
- ✅ Automatic currency conversion (TWD → USD)

### 2. LLM-Powered Insights
- ✅ Extracts exactly 5 key points from earnings calls
- ✅ Summarizes news with date and source
- ✅ Generates coherent narrative analysis

### 3. Supply Chain Risk Analysis
- ✅ Identifies geopolitical risks
- ✅ Analyzes customer concentration
- ✅ Evaluates supplier dependencies
- ✅ Maps risk propagation paths

## 📝 Example Output

See `output_report.md` for a sample generated report on TSMC.

## 🤝 Contributing

This project was developed for the TSMC 2026 CareerHack competition. Contributions and suggestions are welcome!

## 📄 License

This project is for educational and competition purposes.

## 👥 Authors

- **NTUyu016** - [GitHub](https://github.com/NTUyu016)

## 🙏 Acknowledgments

- TSMC CareerHack 2026 organizing team
- Google Gemini AI team
- LangChain & LangGraph communities

---

**Note**: This is a prototype system developed for the TSMC CareerHack competition. The data used is mock data for demonstration purposes.
