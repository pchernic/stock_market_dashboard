# 📈 Interactive Stock Market Dashboard

A modern, dark-themed dashboard built with [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/python/) to visualize stock price data, key performance indicators, and company fundamentals in real time using data from [Yahoo Finance](https://finance.yahoo.com/).

---

## 🚀 Features

- 📊 **Price Visualization**
  - Historical candlestick charts
  - Intraday line charts with 5-minute intervals

- 🧾 **Fundamentals View**
  - Company sector, industry, market cap
  - PE Ratio, Dividend Yield, EPS, and more

- 💡 **KPI Cards**
  - Latest price, daily change (%), market cap, PE ratio, etc.

- 🔀 **Multi-page Layout**
  - Navigation between the main dashboard and fundamentals page

---

## 🛠️ Technologies

- `Dash` for web framework and callbacks
- `Plotly` for interactive charting
- `yFinance` for financial data
- `Pandas` for data manipulation

---

## 📸 Screenshots

### Dashboard View:
![Dashboard Screenshot](screenshots/dashboard.png)

### Fundamentals View:
![Fundamentals Screenshot](screenshots/fundamentals.png)

---

## 📦 Installation

### 1. Clone the repository
'''
bash
git clone https://github.com/yourusername/stock_market_dashboard.git
cd stock_market_dashboard
'''

### 2. Virtual Environment 
Example:
python -m venv stockdash

### 3.  Activate venv stockdash
.\stockdash\Scripts\Activate.ps1

### 4. Install dependencies

pip install -r requirements.txt 

### 5.  Run app.py

python app.py

