"""
04_survival_model.py
Question 7: Under which attendance and interest-rate scenarios can AMC carry its debt?

Connects the four projects:
  attendance (project 1: scenarios for 2026 Q3 to 2027 Q2)
  -> revenue: U.S. guests x revenue per U.S. guest (AMC's whole revenue, all countries,
     divided by U.S. attendance, so international theatres move with the U.S.)
  -> cash operating costs: fixed + variable share of revenue (project 3's break-even fit,
     re-estimated here on the same quarters)
  -> cash from operations: minus a calibration for cash items not in the income
     statement (deferred rent repayments, working capital), estimated from 2024 to mid-2026
  -> minus theatre investment, minus interest on the debt (this project)
  = free cash flow after interest: what is left to repay debt, or the gap that has to be
    filled by selling shares or borrowing more.

Two outputs:
  1. Cash paths, quarter by quarter to the end of 2029 (when most of the debt is due), for
     the five attendance scenarios of project 1, at today's interest cost.
  2. A "survival map": yearly free cash flow after interest for every combination of
     U.S. attendance and interest rate on the debt (all paid in cash, as on refinanced
     debt), with the line where it is zero. Scenario paths assume attendance after the
     forecast year stays at the forecast year's level.
     Also saved as a table for the interactive dashboard (with spend per guest and fixed
     costs as extra dimensions).

Everything is a deliberately simple, transparent model; all assumptions are at the top.

    python 04_survival_model.py
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import CHARTS, COLORS, DATA, RESULTS, annual, balance_sheet, ensure_folders, income_statement, tidy

# ---- assumptions (change here) ----
FIT_PERIOD = ("2022-07-01", "2026-06-30")       # quarters used for the fixed/variable cost split
CALIBRATION_YEARS = ["2024", "2025", "2026 H1"]  # cash-flow years used to calibrate cash vs profit
CAPEX_PER_YEAR = 225.0        # $m; recent years 246m, 2026 H1 92m
PRICE_GROWTH = 0.02           # spend per guest, per year
COST_INFLATION = 0.03         # fixed costs, per year
MIN_CASH = 250.0              # $m a theatre chain of this size needs on hand
PROJECT_TO = "2029-12-31"
DEBT_DUE_2029 = 3172.2        # $m principal due in 2029, as reported at the end of 2025

# survival map axes
ATTENDANCE_GRID = np.arange(120, 245, 5)        # U.S. guests per year, millions
RATE_GRID = np.round(np.arange(6.0, 16.01, 0.5), 1)   # % per year on the whole debt
SPEND_GRID = [-10, -5, 0, 5, 10, 15, 20]        # % change in spend per guest vs today
FIXED_GRID = [-10, -5, 0, 5, 10]                # % change in fixed costs vs today
MAP_YEAR_OFFSET = 1.5          # map is for 2028 cost and price levels (mid-way to 2029)


def fit_costs(q):
    d = q[q["quarter_end"].between(*FIT_PERIOD)]
    cash_costs = d["costs_total"] - d["cost_depreciation"] - d["cost_impairment_other"]
    v, fixed_q = np.polyfit(d["revenue_total"], cash_costs, 1)
    return v, 4 * fixed_q


def main():
    ensure_folders()
    q = income_statement("amc")
    us = pd.read_csv(os.path.join(DATA, "amc_quarterly.csv"), encoding="utf-8-sig", dtype=str, keep_default_na=False)
    us_att = pd.to_numeric(us.set_index(us["quarter"].str.strip())["us_attendance_millions"].str.strip(), errors="coerce")
    q["us_attendance_m"] = q["quarter"].map(us_att)
    b = balance_sheet("AMC")
    cf = pd.read_csv(os.path.join(DATA, "cash_flow_annual.csv")).set_index("year")

    v, fixed = fit_costs(q)
    last4 = q[q["quarter_end"].between("2025-07-01", "2026-06-30")]
    rev_per_guest = last4["revenue_total"].sum() / last4["us_attendance_m"].sum()
    debt0 = b.loc["2026-06-30", "debt_m"]
    cash0 = b.loc["2026-06-30", "cash_m"]

    # Calibration: actual cash from operations before interest vs the model's cash profit
    model_vs_actual = []
    for y in CALIBRATION_YEARS:
        yr = 2026 if y == "2026 H1" else int(y)
        d = q[q["year"] == yr]
        model = (1 - v) * d["revenue_total"].sum() - fixed * len(d) / 4
        model_vs_actual.append((y, model, cf.loc[y, "operating_cash_before_interest_m"], len(d) / 4))
    gap = sum(m - a for _, m, a, _ in model_vs_actual) / sum(w for *_, w in model_vs_actual)

    # Interest today: effective rate (incl. interest paid in extra debt) and the cash part
    ann_q = q[q["quarter_end"].between("2025-07-01", "2026-06-30")]["interest_debt"].sum()
    avg_debt = b.loc["2025-06-30":"2026-06-30", "debt_m"].mean()
    rate_now = ann_q / avg_debt
    cash_paid_h1 = -cf.loc["2026 H1", "interest_paid_m"] * 2
    cash_share = min(1.0, cash_paid_h1 / ann_q)

    inputs = pd.Series({
        "variable_cost_share_of_revenue": v, "fixed_cash_costs_per_year_m": fixed,
        "revenue_per_us_guest_$": rev_per_guest, "cash_gap_vs_model_per_year_m": gap,
        "debt_2026_06_30_m": debt0, "cash_2026_06_30_m": cash0,
        "effective_interest_rate_last_4q": rate_now, "cash_share_of_interest": cash_share,
        "capex_per_year_m": CAPEX_PER_YEAR, "price_growth": PRICE_GROWTH, "cost_inflation": COST_INFLATION,
    })
    inputs.round(4).to_csv(os.path.join(RESULTS, "04_model_inputs.csv"), header=["value"])
    print("=== MODEL INPUTS (estimated from the data) ===")
    print(inputs.round(3).to_string())
    print("\nCalibration (model cash profit vs actual cash from operations before interest, $m):")
    for y, m, a, w in model_vs_actual:
        print(f"  {y}: model {m:,.0f}, actual {a:,.0f}")
    print(f"  -> {gap:,.0f}m a year of cash costs outside the income statement are deducted in the model")

    # Check: the model on the last four quarters
    model_fcf = (1 - v) * last4["revenue_total"].sum() - fixed - gap - CAPEX_PER_YEAR - rate_now * cash_share * debt0
    print(f"\nModel on the last four quarters: free cash flow after cash interest {model_fcf:,.0f}m a year")

    # 1. Cash paths by attendance scenario
    sc = pd.read_csv(os.path.join(DATA, "attendance_scenarios.csv"))
    quarters = pd.period_range("2026Q3", PROJECT_TO[:4] + "Q4", freq="Q")
    paths = []
    for name in ["stress low", "low", "base", "high", "stress high"]:
        first_year = dict(zip(sc["quarter"].str.replace(" ", ""), sc[name]))
        cash, debt = cash0, debt0
        for i, p in enumerate(quarters):
            key = f"{p.year}Q{p.quarter}"
            # after the forecast year, each quarter repeats the same quarter of the forecast year
            att = first_year[f"{2026 if p.quarter >= 3 else 2027}Q{p.quarter}"]
            t = (i + 0.5) / 4
            revenue = att * rev_per_guest * (1 + PRICE_GROWTH) ** t
            op_cash = (1 - v) * revenue - (fixed + gap) / 4 * (1 + COST_INFLATION) ** t
            interest = rate_now * debt / 4
            cash_interest = interest * cash_share
            debt += interest - cash_interest             # interest paid in extra debt
            if key == "2027Q2":
                debt -= 125.5; cash -= 125.5             # 6.125% notes due 2027, repaid in cash
            fcf = op_cash - CAPEX_PER_YEAR / 4 - cash_interest
            cash += fcf
            paths.append({"scenario": name, "quarter": key, "us_attendance_m": att, "revenue_m": revenue,
                          "operating_cash_m": op_cash, "cash_interest_m": cash_interest,
                          "free_cash_after_interest_m": fcf, "cash_m": cash, "debt_m": debt})
    paths = pd.DataFrame(paths).round(1)
    paths.to_csv(os.path.join(RESULTS, "04_scenario_paths.csv"), index=False)
    summary = paths.groupby("scenario").agg(
        us_attendance_per_year_m=("us_attendance_m", lambda s: s.iloc[:4].sum()),
        free_cash_after_interest_per_year_m=("free_cash_after_interest_m", lambda s: s.sum() / (len(s) / 4)),
        cash_end_2029_m=("cash_m", "last"), lowest_cash_m=("cash_m", "min"),
        debt_end_2029_m=("debt_m", "last")).reindex(["stress low", "low", "base", "high", "stress high"])
    summary["shortfall_vs_min_cash_m"] = (MIN_CASH - summary["lowest_cash_m"]).clip(lower=0)
    summary.round(0).to_csv(os.path.join(RESULTS, "04_scenario_summary.csv"))
    print("\n=== CASH PATHS TO THE END OF 2029, AT TODAY'S INTEREST COST, NO NEW SHARES OR LOANS ($m) ===")
    print(summary.round(0).to_string())

    # 2. Survival map (steady state, 2028 price and cost levels)
    grid = []
    t = MAP_YEAR_OFFSET + 0.5
    debt_map = debt0 - 125.5
    for att in ATTENDANCE_GRID:
        for rate in RATE_GRID:
            for spend in SPEND_GRID:
                for fx in FIXED_GRID:
                    revenue = att * rev_per_guest * (1 + spend / 100) * (1 + PRICE_GROWTH) ** t
                    fixed_y = (fixed + gap) * (1 + fx / 100) * (1 + COST_INFLATION) ** t
                    op_cash = (1 - v) * revenue - fixed_y
                    interest = rate / 100 * debt_map
                    fcf = op_cash - CAPEX_PER_YEAR - interest
                    ebitdar = op_cash + gap + 4 * 222    # back to an earnings basis, adding rent (~$222m a quarter)
                    grid.append({"us_attendance_m": att, "interest_rate_%": rate, "spend_per_guest_change_%": spend,
                                 "fixed_cost_change_%": fx, "revenue_m": revenue, "operating_cash_m": op_cash,
                                 "interest_m": interest, "capex_m": CAPEX_PER_YEAR,
                                 "free_cash_after_interest_m": fcf, "self_funding": fcf >= 0})
    grid = pd.DataFrame(grid).round(1)
    grid.to_csv(os.path.join(RESULTS, "04_survival_grid.csv"), index=False)

    base = grid[(grid["spend_per_guest_change_%"] == 0) & (grid["fixed_cost_change_%"] == 0)]
    need = []
    for rate in RATE_GRID:
        g = base[base["interest_rate_%"] == rate].sort_values("us_attendance_m")
        # attendance where free cash flow crosses zero (linear in attendance)
        x, y = g["us_attendance_m"].values, g["free_cash_after_interest_m"].values
        a = np.interp(0, y, x) if y.min() < 0 < y.max() else (np.nan if y.max() < 0 else x.min())
        need.append({"interest_rate_%": rate, "us_attendance_needed_m": a})
    need = pd.DataFrame(need).round(1)
    need.to_csv(os.path.join(RESULTS, "04_attendance_needed_by_rate.csv"), index=False)
    print("\n=== U.S. GUESTS A YEAR NEEDED FOR AMC TO FUND ITSELF (free cash after interest >= 0) ===")
    print(need[need["interest_rate_%"].isin([6, 8, 10, 11, 12, 14, 16])].to_string(index=False))
    print(f"  Today: about {last4['us_attendance_m'].sum():.0f}m U.S. guests a year; interest {100 * rate_now:.1f}% "
          f"in total, of which {100 * rate_now * cash_share:.1f}% paid in cash (the map's rate is all paid in cash).")

    # Charts
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.6), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    piv = base.pivot(index="interest_rate_%", columns="us_attendance_m", values="free_cash_after_interest_m")
    lim = np.nanmax(np.abs(piv.values))
    im = ax.imshow(piv.values, origin="lower", aspect="auto", cmap="RdYlGn", vmin=-lim, vmax=lim,
                   extent=[ATTENDANCE_GRID[0] - 2.5, ATTENDANCE_GRID[-1] + 2.5, RATE_GRID[0] - 0.25, RATE_GRID[-1] + 0.25])
    ax.plot(need["us_attendance_needed_m"], need["interest_rate_%"], color="black", lw=2,
            label="Break-even: free cash after interest = 0")
    ax.axvspan(151.1, 214.9, color="white", alpha=0.18)
    ax.axvline(169.9, color="white", lw=1.2, ls="--")
    ax.annotate("attendance forecast\n(project 1): base 170m,\n8-in-10 range 151-215m", (172, RATE_GRID[0] + 0.3),
                color="black", fontsize=7.5)
    ax.scatter([last4["us_attendance_m"].sum()], [100 * rate_now * cash_share], color="black", s=90, marker="*",
               zorder=5, label=f"Today: {last4['us_attendance_m'].sum():.0f}m guests, {100 * rate_now * cash_share:.1f}% paid in cash")
    ax.set_xlabel("U.S. guests per year (millions)")
    ax.set_ylabel("Interest paid in cash on all of AMC's debt (% per year)")
    ax.set_title("Survival map: free cash flow after interest ($m a year)", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.colorbar(im, ax=ax, label="$m a year (green: AMC funds itself; red: needs new money)")

    ax = axes[1]
    colors = {"stress low": "#922b21", "low": "#e67e22", "base": "#1f4e79", "high": "#27ae60", "stress high": "#145a32"}
    for name in ["stress high", "high", "base", "low", "stress low"]:
        g = paths[paths["scenario"] == name]
        ax.plot(range(len(g)), g["cash_m"] / 1000, marker="o", ms=3, color=colors[name], label=name)
    ax.axhline(MIN_CASH / 1000, color="#555", ls="--", lw=0.8)
    ax.annotate(f"cash needed to operate (~${MIN_CASH:.0f}m)", (0, MIN_CASH / 1000), xytext=(2, 3),
                textcoords="offset points", fontsize=7.5, color="#555")
    ax.axhline(0, color="#333", lw=0.8)
    ql = paths["quarter"].unique()
    ax.set_xticks(range(0, len(ql), 2))
    ax.set_xticklabels(ql[::2], fontsize=8, rotation=45)
    ax.set_ylabel("Cash, $ billions")
    ax.set_title(f"Cash to 2029 with no new money (then ${DEBT_DUE_2029 / 1000:.1f}bn of debt falls due)",
                 loc="left", fontsize=10)
    ax.legend(title="Attendance scenario", frameon=False, fontsize=8, title_fontsize=8)
    tidy(ax)
    fig.tight_layout()
    path = os.path.join(CHARTS, "04_survival.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
