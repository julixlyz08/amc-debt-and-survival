"""
make_tableau_files.py
Writes clean, clearly named CSV files for the Tableau dashboard (see TABLEAU_GUIDE.md).
Run after the four analysis scripts.

    python make_tableau_files.py

Output folder: tableau/
"""

import os

import pandas as pd

OUT = "tableau"


def main():
    os.makedirs(OUT, exist_ok=True)

    g = pd.read_csv("results/04_survival_grid.csv")
    g = g.rename(columns={
        "us_attendance_m": "US Guests (m)", "interest_rate_%": "Interest Rate (%)",
        "spend_per_guest_change_%": "Spend per Guest Change (%)", "fixed_cost_change_%": "Fixed Cost Change (%)",
        "revenue_m": "Revenue ($m)", "operating_cash_m": "Operating Cash ($m)", "interest_m": "Interest ($m)",
        "capex_m": "Theatre Investment ($m)", "free_cash_after_interest_m": "Free Cash After Interest ($m)",
        "self_funding": "Self-Funding"})
    g["Self-Funding"] = g["Self-Funding"].map({True: "Yes", False: "No"})
    g.to_csv(os.path.join(OUT, "survival_grid.csv"), index=False)

    p = pd.read_csv("results/04_scenario_paths.csv")
    p["Quarter End"] = pd.PeriodIndex(p["quarter"], freq="Q").end_time.date
    p = p.rename(columns={"scenario": "Scenario", "quarter": "Quarter", "us_attendance_m": "US Guests (m)",
                          "revenue_m": "Revenue ($m)", "operating_cash_m": "Operating Cash ($m)",
                          "cash_interest_m": "Cash Interest ($m)",
                          "free_cash_after_interest_m": "Free Cash After Interest ($m)",
                          "cash_m": "Cash ($m)", "debt_m": "Debt ($m)"})
    p["Scenario"] = p["Scenario"].str.title()
    p.to_csv(os.path.join(OUT, "scenario_paths.csv"), index=False)

    b = pd.read_csv("data/balance_sheet_quarterly.csv")
    b = b[["company", "date", "debt_m", "finance_lease_m", "operating_lease_m", "cash_m"]]
    long = b.melt(id_vars=["company", "date"], var_name="Item", value_name="Amount ($m)").dropna()
    long["Item"] = long["Item"].map({"debt_m": "Corporate Debt", "finance_lease_m": "Finance Leases",
                                     "operating_lease_m": "Operating Leases", "cash_m": "Cash"})
    long = long.rename(columns={"company": "Company", "date": "Date"})
    long["Company"] = long["Company"].map({"AMC": "AMC", "CNK": "Cinemark"})
    long.to_csv(os.path.join(OUT, "debt_history.csv"), index=False)

    m = pd.read_csv("data/debt_maturities.csv")
    m = m.rename(columns={"company": "Company", "as_of": "As Of", "year_due": "Year Due",
                          "principal_due_m": "Principal Due ($m)"})
    m["Company"] = m["Company"].map({"AMC": "AMC", "CNK": "Cinemark"})
    m.to_csv(os.path.join(OUT, "maturities.csv"), index=False)

    c = pd.read_csv("results/02_cost_of_debt.csv")
    c = c[["year", "effective_rate_%", "cash_interest_rate_%", "treasury_5y_%", "baa_corporate_%",
           "high_yield_all_%", "high_yield_ccc_%"]]
    c = c.melt(id_vars="year", var_name="Series", value_name="Rate (%)").dropna()
    c["Series"] = c["Series"].map({
        "effective_rate_%": "AMC: effective rate", "cash_interest_rate_%": "AMC: cash interest only",
        "treasury_5y_%": "5-year Treasury", "baa_corporate_%": "Baa corporate bonds",
        "high_yield_all_%": "All junk bonds", "high_yield_ccc_%": "CCC junk bonds"})
    c = c.rename(columns={"year": "Year"})
    c.to_csv(os.path.join(OUT, "cost_of_debt.csv"), index=False)

    for f in sorted(os.listdir(OUT)):
        print(f"  {OUT}/{f}: {len(pd.read_csv(os.path.join(OUT, f))):,} rows")


if __name__ == "__main__":
    main()
