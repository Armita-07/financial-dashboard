import numpy as np
import pandas as pd


def calculate_npv(cash_flows, discount_rate, initial_investment):
    """Net Present Value calculation."""
    npv = -initial_investment
    for i, cf in enumerate(cash_flows, start=1):
        npv += cf / ((1 + discount_rate / 12) ** i)
    return round(npv, 2)


def calculate_roi(total_revenue, initial_investment):
    """Return on Investment over the period."""
    roi = ((total_revenue - initial_investment) / initial_investment) * 100
    return round(roi, 2)


def calculate_burn_rate(monthly_costs, monthly_revenue):
    """Average monthly net burn (negative = burning cash)."""
    net = [r - c for r, c in zip(monthly_revenue, monthly_costs)]
    burn_months = [n for n in net if n < 0]
    avg_burn = np.mean(burn_months) if burn_months else 0
    return round(avg_burn, 2)


def calculate_breakeven_month(monthly_revenue, monthly_costs):
    """Month index when cumulative revenue exceeds cumulative costs."""
    cum_rev = np.cumsum(monthly_revenue)
    cum_cost = np.cumsum(monthly_costs)
    for i, (r, c) in enumerate(zip(cum_rev, cum_cost)):
        if r >= c:
            return i + 1
    return None  # Not reached within the period


def calculate_runway(initial_investment, monthly_costs, monthly_revenue):
    """Months of runway remaining given current burn."""
    cash = initial_investment
    for i, (cost, rev) in enumerate(zip(monthly_costs, monthly_revenue)):
        cash += rev - cost
        if cash <= 0:
            return i + 1
    return len(monthly_costs)  # survived full period


def calculate_cagr(monthly_revenue, months=12):
    """Compound Annual Growth Rate from first non-zero to last month."""
    non_zero = [(i, r) for i, r in enumerate(monthly_revenue) if r > 0]
    if len(non_zero) < 2:
        return 0
    start_i, start_r = non_zero[0]
    end_i, end_r = non_zero[-1]
    period_years = (end_i - start_i) / 12
    if period_years == 0:
        return 0
    cagr = ((end_r / start_r) ** (1 / period_years) - 1) * 100
    return round(cagr, 2)


def tam_penetration(market_size, target_share):
    """Addressable revenue at target market share."""
    return round(market_size * target_share, 2)


def build_monthly_df(startup):
    """Build a month-by-month DataFrame for a startup."""
    f = startup["financials"]
    months = [f"M{i+1}" for i in range(12)]
    revenue = f["monthly_revenue"]
    costs = f["monthly_costs"]
    profit = [r - c for r, c in zip(revenue, costs)]
    cum_profit = list(np.cumsum(profit))

    return pd.DataFrame({
        "Month": months,
        "Revenue": revenue,
        "Costs": costs,
        "Net Profit": profit,
        "Cumulative P&L": cum_profit
    })


def score_startup(startup):
    """Composite investability score out of 100."""
    f = startup["financials"]
    score = 0

    # NPV positive? (30 pts)
    cash_flows = [r - c for r, c in zip(f["monthly_revenue"], f["monthly_costs"])]
    npv = calculate_npv(cash_flows, f["discount_rate"], f["initial_investment"])
    if npv > 0:
        score += 30
    elif npv > -100000:
        score += 15

    # Break-even within 12 months? (25 pts)
    be = calculate_breakeven_month(f["monthly_revenue"], f["monthly_costs"])
    if be and be <= 6:
        score += 25
    elif be and be <= 12:
        score += 15

    # Growth rate (25 pts)
    gr = f.get("growth_rate", 0)
    if gr >= 0.20:
        score += 25
    elif gr >= 0.12:
        score += 15
    else:
        score += 5

    # ROI (20 pts)
    total_rev = sum(f["monthly_revenue"])
    roi = calculate_roi(total_rev, f["initial_investment"])
    if roi > 50:
        score += 20
    elif roi > 0:
        score += 10

    return min(score, 100)


def full_analysis(startup):
    """Return a dict of all key metrics for a startup."""
    f = startup["financials"]
    revenue = f["monthly_revenue"]
    costs = f["monthly_costs"]
    cash_flows = [r - c for r, c in zip(revenue, costs)]

    return {
        "npv": calculate_npv(cash_flows, f["discount_rate"], f["initial_investment"]),
        "roi": calculate_roi(sum(revenue), f["initial_investment"]),
        "burn_rate": calculate_burn_rate(costs, revenue),
        "breakeven_month": calculate_breakeven_month(revenue, costs),
        "runway_months": calculate_runway(f["initial_investment"], costs, revenue),
        "cagr": calculate_cagr(revenue),
        "tam_penetration": tam_penetration(f["market_size"], f["target_market_share"]),
        "total_revenue": sum(revenue),
        "total_costs": sum(costs),
        "score": score_startup(startup),
        "df": build_monthly_df(startup)
    }
