# 📊 Financial Model & Market Feasibility Dashboard

An interactive dashboard for evaluating the investment viability of early-stage startups. Built with Python, Streamlit, and Plotly.

## 🚀 What It Does

- Analyses **3 startups** across HealthTech, CleanTech, and EdTech sectors
- Computes key financial metrics: **NPV, ROI, Break-even, Burn Rate, CAGR, Runway**
- Visualises **revenue vs cost trajectories** and **cumulative P&L**
- Generates an **Investability Score (0–100)** for each startup
- Side-by-side **comparative view** across all startups

## 📐 Financial Models Used

| Metric | Description |
|---|---|
| **NPV** | Net Present Value — discounted future cash flows |
| **ROI** | Return on Investment over 12-month period |
| **Break-even** | Month when cumulative revenue exceeds costs |
| **Burn Rate** | Average monthly cash consumed during loss phase |
| **Runway** | Months before cash depletion |
| **CAGR** | Compound Annual Growth Rate of revenue |
| **TAM Penetration** | Revenue at target market share |

## 🛠️ Tech Stack

- **Python** — financial modelling logic
- **Streamlit** — interactive dashboard UI
- **Plotly** — charts (area, bar, line)
- **Pandas / NumPy** — data processing

## ⚡ Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/financial-dashboard.git
cd financial-dashboard

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## 📁 Project Structure

```
financial-dashboard/
├── app.py                  # Streamlit dashboard (entry point)
├── data/
│   └── startups.py         # Mock startup financial data
├── models/
│   └── financials.py       # NPV, ROI, burn rate, score calculations
├── requirements.txt
└── README.md
```

## 📸 Features

- **Sidebar controls** — switch between startups, toggle compare view, change chart type
- **KPI cards** — instant read on 5 key metrics per startup
- **Dual charts** — revenue/cost breakdown + cumulative P&L trajectory
- **Data table** — full month-by-month breakdown
- **Compare mode** — grouped bar chart comparing all 3 startups

## 👩‍💻 Author

**Armita Patro** — CSE @ KIIT · GenAI & Financial Modelling  
[LinkedIn](https://linkedin.com/in/armitapatro) · [GitHub](https://github.com/Armita-07)
