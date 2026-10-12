"""
03_cash_leases_swaps.py
Question 4: Where did AMC's cash come from and where did it go, 2020 to mid-2026?
Question 5: Leases are debt too: leverage including leases, AMC vs Cinemark.
Question 6: How much debt was swapped for shares, and at what price?

    python 03_cash_leases_swaps.py
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import CHARTS, COLORS, DATA, RESULTS, annual, balance_sheet, ensure_folders, income_statement, tidy

FLOWS = [  # column, label, colour
    ("operating_cash_before_interest_m", "Cash from running the theatres (before interest)", "operating"),
    ("interest_paid_m", "Interest paid", "interest"),
    ("theatre_investment_capex_m", "Investment in theatres", "capex"),
    ("other_investing_m", "Other investing", "other"),
    ("equity_raised_m", "Shares sold for cash", "equity"),
    ("net_borrowing_and_other_financing_m", "Net new borrowing (and other financing)", "borrowing"),
]
LEVERAGE_YEARS = [2019, 2023, 2024, 2025]


def leverage(ticker, company):
    a = annual(income_statement(ticker))
    b = balance_sheet(company)
    rows = []
    for y in LEVERAGE_YEARS:
        e = b.loc[f"{y}-12-31"]
        ebitda = a.loc[y, "operating_income"] + a.loc[y, "cost_depreciation"] + a.loc[y, "cost_impairment_other"]
        ebitdar = ebitda + a.loc[y, "cost_rent"]
        leases = e["finance_lease_m"] + e["operating_lease_m"]
        rows.append({
            "company": company, "year": y,
            "debt_m": e["debt_m"], "lease_liabilities_m": leases, "cash_m": e["cash_m"],
            "ebitda_m": ebitda, "rent_m": a.loc[y, "cost_rent"], "ebitdar_m": ebitdar,
            "debt_to_ebitda": e["debt_m"] / ebitda if ebitda > 0 else np.nan,
            "debt_plus_leases_to_ebitdar": (e["debt_m"] + leases) / ebitdar if ebitdar > 0 else np.nan,
            "net_debt_plus_leases_to_ebitdar": (e["debt_m"] + leases - e["cash_m"]) / ebitdar if ebitdar > 0 else np.nan,
        })
    return pd.DataFrame(rows)


def main():
    ensure_folders()
    cf = pd.read_csv(os.path.join(DATA, "cash_flow_annual.csv")).set_index("year")
    cf = cf.loc[[i for i in cf.index if i >= "2019"]]
    print("=== WHERE AMC'S CASH CAME FROM AND WENT (US$ millions) ===")
    print(cf.drop(columns="check_m").to_string())
    since = cf.loc[[i for i in cf.index if i >= "2020"]].sum()
    print("\n=== 2020 TO JUNE 2026, IN TOTAL ===")
    for col, label, _ in FLOWS:
        print(f"  {label:50s} {since[col]:>9,.0f}")
    print(f"  {'Change in cash (incl. currency effects)':50s} {since['change_in_cash_m']:>9,.0f}")
    print(f"\n  Shares sold for cash covered {100 * since['equity_raised_m'] / -since['interest_paid_m']:.0f}% "
          f"of the interest paid over the period.")

    lev = pd.concat([leverage("amc", "AMC"), leverage("cnk", "CNK")]).round(2)
    lev.to_csv(os.path.join(RESULTS, "03_leverage_with_leases.csv"), index=False)
    print("\n=== LEVERAGE, WITH AND WITHOUT LEASES (times a year's earnings) ===")
    print(lev[["company", "year", "debt_m", "lease_liabilities_m", "ebitda_m", "ebitdar_m",
               "debt_to_ebitda", "debt_plus_leases_to_ebitdar"]].to_string(index=False))

    e4d = pd.read_csv(os.path.join(DATA, "equity_for_debt.csv")).set_index("year")
    print("\n=== SHARES ISSUED TO CANCEL DEBT (and as fees to lenders) ===")
    print(e4d.to_string())
    tot_val = e4d["value_of_shares_issued_for_debt_m"].sum() + e4d["value_of_fee_shares_to_lenders_m"].sum()
    tot_sh = e4d["shares_issued_for_debt_m_split_adjusted"].sum() + e4d["fee_shares_m"].sum()
    shares_now = 892.6   # cover of the 2026 Q2 10-Q (see the stock project)
    print(f"\n  In total: ${tot_val:,.0f}m of shares, {tot_sh:,.0f}m shares (split-adjusted), "
          f"about {100 * tot_sh / shares_now:.0f}% of the {shares_now:.0f}m shares outstanding in July 2026.")

    # Charts
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.4), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    yrs = list(cf.index)
    x = np.arange(len(yrs))
    pos = np.zeros(len(yrs))
    neg = np.zeros(len(yrs))
    for col, label, ckey in FLOWS:
        v = cf[col].values / 1000
        bottom = np.where(v >= 0, pos, neg)
        ax.bar(x, v, bottom=bottom, color=COLORS[ckey], label=label, width=0.65)
        pos += np.where(v >= 0, v, 0)
        neg += np.where(v < 0, v, 0)
    ax.plot(x, cf["change_in_cash_m"] / 1000, color="black", marker="D", ms=5, lw=0, label="Change in cash")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(yrs, fontsize=8)
    ax.set_ylabel("$ billions")
    ax.set_title("Where AMC's cash came from (above zero) and went (below zero)", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3)
    tidy(ax)

    ax = axes[1]
    for k, (comp, color) in enumerate([("AMC", COLORS["AMC"]), ("CNK", COLORS["CNK"])]):
        g = lev[lev["company"] == comp]
        xs = np.arange(len(g)) + (k - 0.5) * 0.38
        ax.bar(xs, g["debt_plus_leases_to_ebitdar"], width=0.38, color=color,
               label=("AMC" if comp == "AMC" else "Cinemark") + ": debt + leases / earnings before rent")
        ax.scatter(xs, g["debt_to_ebitda"], color="white", edgecolor=color, zorder=3, s=30,
                   label=("AMC" if comp == "AMC" else "Cinemark") + ": debt only / earnings after rent")
        for xi, v in zip(xs, g["debt_plus_leases_to_ebitdar"]):
            ax.annotate(f"{v:.1f}x", (xi, v), ha="center", va="bottom", fontsize=8, xytext=(0, 2), textcoords="offset points")
    ax.set_xticks(range(len(LEVERAGE_YEARS)))
    ax.set_xticklabels(LEVERAGE_YEARS)
    ax.set_ylabel("Years of earnings needed to repay")
    ax.set_title("Leverage, counting leases as debt", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)
    tidy(ax)
    fig.tight_layout()
    path = os.path.join(CHARTS, "03_cash_and_leverage.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
