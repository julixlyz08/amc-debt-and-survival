"""
common.py
Shared loaders and chart helpers.
"""

import os

import pandas as pd

DATA, CHARTS, RESULTS = "data", "charts", "results"

COLORS = {
    "AMC": "#c0392b", "CNK": "#1f4e79", "debt": "#922b21", "finance_lease": "#e59866",
    "operating_lease": "#8e44ad", "cash": "#27ae60", "treasury": "#7f8c8d", "baa": "#1f4e79",
    "high_yield": "#b7950b", "ccc": "#e67e22", "equity": "#2e86c1", "interest": "#922b21",
    "operating": "#27ae60", "capex": "#b7950b", "borrowing": "#7f8c8d", "other": "#bdc3c7",
}


def ensure_folders():
    for d in (CHARTS, RESULTS):
        os.makedirs(d, exist_ok=True)


def balance_sheet(company="AMC"):
    b = pd.read_csv(os.path.join(DATA, "balance_sheet_quarterly.csv"), parse_dates=["date"])
    return b[b["company"] == company].set_index("date").sort_index()


def income_statement(ticker="amc"):
    df = pd.read_csv(os.path.join(DATA, f"{ticker}_income_statement.csv"), parse_dates=["quarter_end"])
    df["year"] = df["quarter_end"].dt.year
    return df


def annual(df):
    num = df.select_dtypes("number").drop(columns=["year"], errors="ignore")
    g = num.groupby(df["year"])
    out = g.sum(min_count=1)
    return out[g.size() == 4]


def rates():
    return pd.read_csv(os.path.join(DATA, "market_rates_monthly.csv"), parse_dates=["month"]).set_index("month")


def tidy(ax, grid="y"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid, alpha=0.3)
