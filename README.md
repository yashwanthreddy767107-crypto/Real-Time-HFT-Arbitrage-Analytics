# Real-Time HFT Arbitrage Detection and Analytics System

## 📌 Project Overview
This project is a simulated cryptocurrency arbitrage detection and analytics system developed using Python, PostgreSQL, and Streamlit. It monitors cryptocurrency prices across simulated exchanges, identifies potential arbitrage opportunities, and displays market analytics through an interactive dashboard.

## 🎯 Problem Statement
Cryptocurrency prices can vary between exchanges. Manually comparing prices and calculating potential profits is time-consuming. This project automates price comparison and profit-and-loss analysis to help identify potential arbitrage opportunities.

## 💡 Objectives
- Simulate cryptocurrency market data across multiple exchanges.
- Store market data using PostgreSQL.
- Detect potential arbitrage opportunities by comparing buy and sell prices.
- Calculate estimated profit and loss.
- Visualize market data and analytics through an interactive dashboard.
- Display charts, metrics, and exchange comparisons.

## 🛠️ Technologies Used
- **Python** — application logic and arbitrage calculations
- **PostgreSQL** — database management
- **Streamlit** — interactive dashboard
- **Pandas** — data processing
- **Plotly** — interactive charts

## 📂 Project Files
- `market_data_simulator.py` — generates simulated market prices
- `arbitrage_detector.py` — detects potential arbitrage opportunities
- `database.py` — handles database connectivity
- `profit_loss.py` — calculates profit and loss
- `dashboard.py` — displays analytics and visualizations
- `insert_test_data.py` — inserts test data
- `test_database.py` — tests database functionality

## ⚙️ Setup and Installation

1. Install Python and PostgreSQL.
2. Clone this repository:
   ```bash
   git clone https://github.com/yashwanthreddy767107-crypto/Real-Time-HFT-Arbitrage-Analytics.git
   ```
3. Open the project folder:
   ```bash
   cd Real-Time-HFT-Arbitrage-Analytics
   ```
4. Create and activate a virtual environment on Windows:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Configure PostgreSQL connection settings in `database.py` or your environment variables. Create the required database and tables according to your project code.

## ▶️ How to Run

Open separate terminals in the project folder and activate the virtual environment in each terminal.

**Terminal 1 — Market data simulator**
```bash
python market_data_simulator.py
```

**Terminal 2 — Arbitrage detector**
```bash
python arbitrage_detector.py
```

**Terminal 3 — Dashboard**
```bash
streamlit run dashboard.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## 📊 Expected Results
- Simulated cryptocurrency market prices
- Potential arbitrage opportunities across exchanges
- Estimated profit-and-loss calculations
- Interactive charts and market analytics
- Dashboard-based monitoring of simulated market activity

## ⚠️ Disclaimer
This project uses simulated market data for educational and demonstration purposes. It does not execute real trades or guarantee profits. Transaction fees, slippage, latency, liquidity, and market risks must be considered before any real-world implementation.

## 👨‍💻 Author
Developed as an academic project to explore Python programming, database integration, financial data analysis, and interactive dashboard development.
