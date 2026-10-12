"""
01_debt_and_maturities.py
Question 1: What does AMC owe, at what rate, and when is it due?
Question 2: Where did the debt come from?

    python 01_debt_and_maturities.py
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import CHARTS, COLORS, DATA, RESULTS, balance_sheet, ensure_folders, tidy

MILESTONES = [
    ("2015-12-31", "Before the acquisitions"),
    ("2016-12-31", "After Carmike and Odeon/UCI"),
    ("2017-12-31", "After Nordic"),
    ("2019-12-31", "Before the pandemic"),
    ("2020-12-31", "End of 2020"),
    ("2021-12-31", "End of 2021"),
    ("2022-12-31", "End of 2022"),
    ("2023-12-31", "End of 2023"),
    ("2024-12-31", "End of 2024"),
    ("2025-12-31", "End of 2025"),
    ("2026-06-30", "Latest (June 2026)"),
]


def main():
    ensure_folders()
    b = balance_sheet("AMC")

    rows = []
    for d, label in MILESTONES:
        r = b.loc[d]
        rows.append({"date": d, "point": label, "corporate_debt_m": r["debt_m"],
                     "finance_leases_m": r["finance_lease_m"], "operating_leases_m": r["operating_lease_m"],
                     "cash_m": r["cash_m"], "debt_minus_cash_m": r["debt_m"] - r["cash_m"]})
    hist = pd.DataFrame(rows).round(0)
    hist.to_csv(os.path.join(RESULTS, "01_debt_history.csv"), index=False)
    print("=== AMC'S DEBT AT KEY POINTS (US$ millions) ===")
    print(hist.to_string(index=False))
    print("Operating leases are on the balance sheet only from 2019 (new lease accounting standard).")

    led = pd.read_csv(os.path.join(DATA, "debt_ledger.csv"))
    print("\n=== INSTRUMENT BY INSTRUMENT (as tagged in the filings) ===")
    for d, g in led.groupby("as_of"):
        print(f"\n{d}  (balance-sheet total ${g['balance_sheet_total_m'].iloc[0]:,.0f}m; "
              f"instruments tagged ${g['amount_m'].sum():,.0f}m)")
        print(g[["instrument", "matures", "type", "amount_m", "stated_rate_%", "effective_rate_%"]].to_string(index=False))

    mat = pd.read_csv(os.path.join(DATA, "debt_maturities.csv"))
    amc = mat[mat["company"] == "AMC"]
    print("\n=== PRINCIPAL DUE BY YEAR, AS REPORTED AT EACH YEAR END (US$ millions) ===")
    print(amc.pivot(index="year_due", columns="as_of", values="principal_due_m").to_string())
    latest = amc[amc["as_of"] == "2025-12-31"]
    total = latest["principal_due_m"].sum()
    big = latest.loc[latest["principal_due_m"].idxmax()]
    print(f"\nAt the end of 2025, ${big['principal_due_m']:,.0f}m of ${total:,.0f}m "
          f"({100 * big['principal_due_m'] / total:.0f}%) was due in {big['year_due']}.")

    # Charts
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.5, 1]})
    ax = axes[0]
    idx = b.index
    ax.stackplot(idx, b["debt_m"] / 1000, b["finance_lease_m"].fillna(0) / 1000, b["operating_lease_m"].fillna(0) / 1000,
                 colors=[COLORS["debt"], COLORS["finance_lease"], COLORS["operating_lease"]], alpha=0.85,
                 labels=["Corporate debt (loans and bonds)", "Finance leases", "Operating leases (future rent, from 2019)"])
    ax.plot(idx, b["cash_m"] / 1000, color=COLORS["cash"], lw=2, label="Cash")
    for d, label in [("2016-12-31", "Carmike +\nOdeon"), ("2020-03-31", "Pandemic"), ("2023-08-31", "Reverse split,\nAPE conversion")]:
        ax.axvline(pd.Timestamp(d), color="#555", lw=0.7, ls="--")
        ax.annotate(label, (pd.Timestamp(d), 13.3), fontsize=7.5, ha="right", va="top", xytext=(-3, 0),
                    textcoords="offset points", color="#555")
    ax.set_ylim(0, 13.5)
    ax.set_ylabel("$ billions")
    ax.set_title("What AMC owes, quarter by quarter", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2)
    tidy(ax)

    ax = axes[1]
    order = ["2019-12-31", "2025-12-31"]
    colors = ["#bdc3c7", COLORS["AMC"]]
    for k, (d, c) in enumerate(zip(order, colors)):
        g = amc[amc["as_of"] == d]
        years = [int(str(y).rstrip("+")) for y in g["year_due"]]
        ax.bar(np.array(years) + (k - 0.5) * 0.4, g["principal_due_m"] / 1000, width=0.4, color=c,
               label=f"As of end {d[:4]}" + (" (last bar: due that year or later)" if k == 0 else ""))
    ax.set_xticks(range(2020, 2031))
    ax.tick_params(axis="x", labelsize=8, rotation=45)
    ax.set_ylabel("Principal due, $ billions")
    ax.set_title("The maturity wall: when the debt falls due", loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    tidy(ax)
    fig.tight_layout()
    path = os.path.join(CHARTS, "01_debt_and_maturities.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
