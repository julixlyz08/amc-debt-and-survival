"""
02_cost_of_debt.py
Question 3: How much does AMC's debt really cost, compared with what the market charged?

AMC's effective interest rate each year = interest on corporate borrowings (from the
income statement: cash interest plus interest paid in extra debt ("PIK") and the
amortisation of discounts) divided by the average debt over the year (five quarter ends).
The cash-only version uses interest actually paid (cash-flow statement).

Benchmarks (yearly averages): 5-year Treasury (risk-free), Moody's Baa corporate bonds
(the lowest investment grade), and ICE BofA U.S. high-yield bonds, all and CCC-rated
(only from October 2023 on FRED).

    python 02_cost_of_debt.py
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import CHARTS, COLORS, DATA, RESULTS, balance_sheet, ensure_folders, income_statement, rates, tidy


def main():
    ensure_folders()
    b = balance_sheet("AMC")["debt_m"]
    q = income_statement("amc").set_index("quarter_end")
    cf = pd.read_csv(os.path.join(DATA, "cash_flow_annual.csv")).set_index("year")
    r = rates()

    rows = []
    for y in range(2015, 2027):
        ends = [pd.Timestamp(f"{y - 1}-12-31")] + [pd.Timestamp(f"{y}-{m}") for m in ("03-31", "06-30", "09-30", "12-31")]
        if y == 2026:
            ends = ends[:3]
        pts = b.reindex(ends).dropna()
        qi = q[q.index.year == y]["interest_debt"]
        if y == 2026:
            if len(qi) < 2:
                continue
            interest, scale, label = qi.sum(), 2, "2026 H1 (annualised)"
        else:
            if len(qi) < 4:
                continue
            interest, scale, label = qi.sum(), 1, str(y)
        avg = pts.mean()
        cash_paid = -cf.loc["2026 H1" if y == 2026 else str(y), "interest_paid_m"] if (
            ("2026 H1" if y == 2026 else str(y)) in cf.index) else np.nan
        months = r[(r.index.year == y)] if y < 2026 else r[(r.index >= "2026-01-01") & (r.index < "2026-07-01")]
        rows.append({
            "year": label,
            "average_debt_m": round(avg),
            "interest_expense_m": round(interest * scale, 1),
            "effective_rate_%": 100 * interest * scale / avg,
            "cash_interest_rate_%": 100 * cash_paid * scale / avg if pd.notna(cash_paid) else np.nan,
            "treasury_5y_%": months["treasury_5y"].mean(),
            "baa_corporate_%": months["baa_corporate"].mean(),
            "high_yield_all_%": months["high_yield_all"].mean() if months["high_yield_all"].notna().sum() >= 6 else np.nan,
            "high_yield_ccc_%": months["high_yield_ccc"].mean() if months["high_yield_ccc"].notna().sum() >= 6 else np.nan,
        })
    t = pd.DataFrame(rows)
    t["spread_over_treasury_pts"] = t["effective_rate_%"] - t["treasury_5y_%"]
    t["spread_over_baa_pts"] = t["effective_rate_%"] - t["baa_corporate_%"]
    t = t.round(2)
    t.to_csv(os.path.join(RESULTS, "02_cost_of_debt.csv"), index=False)
    print("=== WHAT AMC PAYS ON ITS DEBT VS WHAT THE MARKET CHARGED (% per year) ===")
    print(t.to_string(index=False))

    led = pd.read_csv(os.path.join(DATA, "debt_ledger.csv"))
    print("\n=== RATES ON INDIVIDUAL INSTRUMENTS (stated coupon, or effective rate where only that is tagged) ===")
    for d, g in led.groupby("as_of"):
        g = g.assign(rate=g["stated_rate_%"].fillna(g["effective_rate_%"]))
        w = (g["rate"] * g["amount_m"]).sum() / g.loc[g["rate"].notna(), "amount_m"].sum()
        print(f"  {d}: amount-weighted rate {w:.1f}% on the {100 * g.loc[g['rate'].notna(), 'amount_m'].sum() / g['amount_m'].sum():.0f}% "
              f"of tagged debt that has a rate")

    # Chart
    fig, ax = plt.subplots(figsize=(11.5, 5.2))
    x = np.arange(len(t))
    ax.plot(x, t["effective_rate_%"], marker="o", color=COLORS["AMC"], lw=2.2, label="AMC: effective rate on its debt")
    ax.plot(x, t["cash_interest_rate_%"], marker="o", ms=3, color=COLORS["AMC"], lw=1, ls="--",
            label="AMC: interest paid in cash only")
    ax.plot(x, t["high_yield_ccc_%"], marker="s", color=COLORS["ccc"], lw=1.5, label="CCC-rated junk bonds (from late 2023)")
    ax.plot(x, t["high_yield_all_%"], marker="s", color=COLORS["high_yield"], lw=1.5, label="All junk bonds (from late 2023)")
    ax.plot(x, t["baa_corporate_%"], color=COLORS["baa"], lw=1.5, label="Baa corporate bonds (lowest investment grade)")
    ax.plot(x, t["treasury_5y_%"], color=COLORS["treasury"], lw=1.5, label="5-year U.S. Treasury")
    ax.set_xticks(x)
    ax.set_xticklabels(t["year"].str.replace(" (annualised)", "\n(annualised)"), fontsize=8)
    ax.set_ylabel("% per year")
    ax.set_title("What AMC pays on its debt vs market rates", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    tidy(ax)
    fig.tight_layout()
    path = os.path.join(CHARTS, "02_cost_of_debt.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
