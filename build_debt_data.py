"""
build_debt_data.py
Builds the tables every analysis script reads, from the full XBRL files and FRED/Treasury
rates:

    data/balance_sheet_quarterly.csv   AMC and Cinemark at each quarter end: debt, leases, cash
    data/debt_maturities.csv           principal due each year, as reported at each year end
    data/debt_ledger.csv               AMC's debt instrument by instrument at selected dates,
                                       with a check against the balance-sheet total
    data/cash_flow_annual.csv          where AMC's cash came from and went, by year
    data/equity_for_debt.csv           shares issued to cancel debt, by year
    data/market_rates_monthly.csv      Treasury, SOFR, Baa and high-yield rates, monthly

    python build_debt_data.py
"""

import re

import numpy as np
import pandas as pd

LEDGER_DATES = ["2019-12-31", "2025-12-31", "2026-06-30"]
MATURITY_DATES = ["2019-12-31", "2022-12-31", "2025-12-31"]
PARENT = "dei:LegalEntityAxis=cnk:CnkMember"   # Cinemark's parent-company values (2023 filings)


def load(ticker):
    x = pd.read_csv(f"data/{ticker}_xbrl_full.csv.gz")
    x["days"] = (pd.to_datetime(x["end"]) - pd.to_datetime(x["start"])).dt.days
    x["total"] = x["dimensions"].isna() | (x["dimensions"] == PARENT)
    return x


def instant(x, concepts):
    """Company-total balance at each report date: first concept found, parent values preferred."""
    t = x[x["total"] & x["start"].isna() & x["value"].notna() & (x["end"] == x["report_date"])]
    out = {}
    for c in concepts:
        s = (t[t["concept"] == c].assign(p=lambda d: d["dimensions"].eq(PARENT))
             .sort_values(["filed", "p"]).groupby("end")["value"].last())
        for k, v in s.items():
            out.setdefault(k, v)
    return pd.Series(out, dtype=float) / 1e6


def balance_sheet(ticker):
    x = load(ticker)
    debt_cur = instant(x, ["us-gaap:LongTermDebtCurrent"])
    debt_non = instant(x, ["us-gaap:LongTermDebtNoncurrent"])
    df = pd.DataFrame({
        "debt_current_m": debt_cur,
        "debt_noncurrent_m": debt_non,
        "finance_lease_m": instant(x, ["us-gaap:FinanceLeaseLiability"]),
        "finance_lease_current_m": instant(x, ["us-gaap:FinanceLeaseLiabilityCurrent"]),
        "finance_lease_noncurrent_m": instant(x, ["us-gaap:FinanceLeaseLiabilityNoncurrent"]),
        "operating_lease_m": instant(x, ["us-gaap:OperatingLeaseLiability"]),
        "operating_lease_current_m": instant(x, ["us-gaap:OperatingLeaseLiabilityCurrent"]),
        "operating_lease_noncurrent_m": instant(x, ["us-gaap:OperatingLeaseLiabilityNoncurrent"]),
        "cash_m": instant(x, ["us-gaap:CashAndCashEquivalentsAtCarryingValue"]),
    })
    df["debt_m"] = df["debt_current_m"].fillna(0) + df["debt_noncurrent_m"]
    # Lease totals are not always tagged; current + noncurrent when missing.
    df["finance_lease_m"] = df["finance_lease_m"].fillna(df["finance_lease_current_m"] + df["finance_lease_noncurrent_m"])
    df["operating_lease_m"] = df["operating_lease_m"].fillna(df["operating_lease_current_m"] + df["operating_lease_noncurrent_m"])
    df.index.name = "date"
    df.insert(0, "company", ticker.upper())
    return df.reset_index()


def maturities(ticker):
    x = load(ticker)
    names = {
        "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths": 1,
        "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo": 2,
        "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree": 3,
        "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour": 4,
        "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive": 5,
        "LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive": 6,
    }
    rows = []
    for d in MATURITY_DATES:
        for c, k in names.items():
            v = instant(x, [f"us-gaap:{c}"]).get(d)
            if pd.notna(v):
                y = int(d[:4]) + k
                rows.append({"company": ticker.upper(), "as_of": d,
                             "year_due": f"{y}+" if k == 6 else str(y), "principal_due_m": round(v, 1)})
    return pd.DataFrame(rows)


def readable(member):
    """'SeniorSubordinatedNotes6.125PercentDue2027' -> 'Senior Subordinated Notes 6.125% due 2027'."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z0-9])", " ", member)
    s = re.sub(r"(?<=[0-9])(?=[A-Z])", " ", s)
    s = s.replace(" Percent", "%").replace("Due In ", "due ").replace("Due ", "due ").replace("  ", " ")
    return s


def ledger():
    """AMC's instruments at selected dates. Amount: carrying amount if tagged, else long-term
    debt, else face amount. Rates as tagged (stated coupon or effective rate)."""
    x = load("amc")
    x = x[x["start"].isna() & (x["end"] == x["report_date"])]
    one = x[x["dimensions"].fillna("").str.fullmatch(r"us-gaap:DebtInstrumentAxis=[^;]+")].copy()
    one["instrument"] = one["dimensions"].str.split(":").str[-1].str.replace("Member", "")
    totals = instant(load("amc"), ["us-gaap:LongTermDebtCurrent"]).fillna(0) + \
        instant(load("amc"), ["us-gaap:LongTermDebtNoncurrent"])
    rows = []
    for d in LEDGER_DATES:
        g = one[one["report_date"] == d]
        for inst, h in g.groupby("instrument"):
            val = {c.split(":")[1]: v for c, v in zip(h["concept"], h["value"])}
            amount = next((val[c] for c in ["DebtInstrumentCarryingAmount", "LongTermDebt", "DebtInstrumentFaceAmount"]
                           if pd.notna(val.get(c))), np.nan)
            discount = val.get("DebtInstrumentUnamortizedDiscountPremiumNet", np.nan)
            if pd.isna(amount):
                continue
            year = re.search(r"(20\d\d)", inst)
            rows.append({
                "as_of": d, "instrument": readable(inst),
                "matures": int(year.group(1)) if year else None,
                "type": ("Exchangeable/convertible" if re.search("Exchang|Convert", inst) else
                         "Second lien" if "SecondLien" in inst else
                         "Subordinated (unsecured)" if "Subordinated" in inst else
                         "Secured (first lien / term loan)"),
                "amount_m": round(amount / 1e6, 1),
                "unamortized_discount_premium_m": round(discount / 1e6, 1) if pd.notna(discount) else None,
                "stated_rate_%": round(100 * val["DebtInstrumentInterestRateStatedPercentage"], 3)
                if pd.notna(val.get("DebtInstrumentInterestRateStatedPercentage")) else None,
                "effective_rate_%": round(100 * val["DebtInstrumentInterestRateEffectivePercentage"], 3)
                if pd.notna(val.get("DebtInstrumentInterestRateEffectivePercentage")) else None,
                "balance_sheet_total_m": round(totals.get(d, np.nan), 1),
            })
    led = pd.DataFrame(rows).sort_values(["as_of", "matures", "instrument"])
    cover = led.groupby("as_of").agg(tagged_m=("amount_m", "sum"), total_m=("balance_sheet_total_m", "first"))
    cover["tagged_vs_total_%"] = (100 * cover["tagged_m"] / cover["total_m"]).round(1)
    return led, cover


def annual_flow(x, concepts, year, allow_dims=False):
    """Full-year value (10-K), or the six months to June for 2026, first concept found."""
    for c in concepts:
        t = x[(x["concept"] == c) & x["value"].notna() & (x["total"] | allow_dims)]
        if year == 2026:
            t = t[(t["end"] == "2026-06-30") & t["days"].between(170, 190)]
        else:
            t = t[(t["end"] == f"{year}-12-31") & (t["days"] > 350)]
        if len(t):
            return t.sort_values("filed")["value"].iloc[-1] / 1e6
    return np.nan


def cash_flow():
    x = load("amc")
    rows = []
    for y in range(2017, 2027):
        f = lambda cs: annual_flow(x, [f"us-gaap:{c}" if ":" not in c else c for c in cs], y)
        ocf = f(["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"])
        icf = f(["NetCashProvidedByUsedInInvestingActivities", "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"])
        fcf = f(["NetCashProvidedByUsedInFinancingActivities", "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"])
        fx = f(["EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                "EffectOfExchangeRateOnCashAndCashEquivalents"])
        change = f(["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
                    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
                    "CashAndCashEquivalentsPeriodIncreaseDecrease"])
        interest = f(["InterestPaidNet", "InterestPaid"])
        capex = f(["PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment"])
        # Cash raised by selling shares (cash-flow statement); 2020 only tagged by share class,
        # so the equity statement's value is used. The 2021 Mudrick placement is a separate line.
        equity = f(["ProceedsFromIssuanceOrSaleOfEquity", "ProceedsFromIssuanceOfPreferredStockAndPreferenceStock",
                    "ProceedsFromIssuanceOfCommonStock"])
        if pd.isna(equity):
            equity = f(["StockIssuedDuringPeriodValueNewIssues"])
        mudrick = f(["amch:NetProceedsFromIssuanceOfClassCommonStockIssuedToMudrick"])
        equity = np.nansum([equity, mudrick]) if pd.notna(equity) or pd.notna(mudrick) else 0.0
        rows.append({
            "year": "2026 H1" if y == 2026 else str(y),
            "operating_cash_before_interest_m": ocf + interest,
            "interest_paid_m": -interest,
            "theatre_investment_capex_m": -capex,
            "other_investing_m": icf + capex,
            "equity_raised_m": equity,
            "net_borrowing_and_other_financing_m": fcf - equity,
            "fx_m": fx if pd.notna(fx) else 0.0,
            "change_in_cash_m": change,
            "check_m": (ocf + icf + fcf + (fx if pd.notna(fx) else 0.0)) - change,
        })
    return pd.DataFrame(rows).round(1)


def year_total(x, concepts, year, dims_regex=None):
    """Full-year value, or for years where only quarters are tagged (and 2026 H1), the sum
    of the quarters. dims_regex selects dimensional values (e.g. the common-share class)."""
    for c in concepts:
        t = x[(x["concept"] == c) & x["value"].notna()]
        if dims_regex:
            t = t[t["dimensions"].fillna("").str.fullmatch(dims_regex)]
        else:
            t = t[t["total"] | (t["dimensions"] == "us-gaap:StatementEquityComponentsAxis=us-gaap:ParentMember")]
        t = t.sort_values("filed").drop_duplicates(["start", "end"], keep="last")
        full = t[(t["end"] == f"{year}-12-31") & (t["days"] > 350)]
        if len(full) and year < 2026:
            return full["value"].iloc[0]
        q = t[t["days"].between(80, 100) & t["end"].str.startswith(str(year))]
        if len(q):
            return q.drop_duplicates("end")["value"].sum()
    return np.nan


def equity_for_debt():
    """Shares AMC issued to cancel debt (exchanges and conversions) and as fees to lenders.
    Measured on the equity side: debt-for-debt exchanges are not included."""
    x = load("amc")
    common = r".*StatementClassOfStockAxis=[^;]*(CommonClassA|ClassAndClassB)[^;]*Member;.*CommonStockMember"
    rows = []
    for y in range(2020, 2027):
        # Conversions of convertible notes into shares (2020-21). From 2023 the same tag is used
        # for converting APE units into common shares, which is not a debt transaction.
        conv = y <= 2021
        value = np.nansum([
            year_total(x, ["us-gaap:StockIssuedDuringPeriodValueUponExchangeOfDebtForEquity",
                           "amch:StockIssuedDuringPeriodValueUponExchangeOfDebtForEquity"], y),
            year_total(x, ["us-gaap:StockIssuedDuringPeriodValueConversionOfConvertibleSecurities"], y) if conv else np.nan])
        fee = year_total(x, ["us-gaap:StockIssuedDuringPeriodValueConsentFeesToDebtholders",
                             "amch:StockIssuedDuringPeriodValueConsentFeesToDebtholders"], y)
        shares = np.nansum([
            year_total(x, ["us-gaap:StockIssuedDuringPeriodSharesUponExchangeOfDebtForEquity",
                           "amch:StockIssuedDuringPeriodSharesUponExchangeOfDebtForEquity"], y, common),
            year_total(x, ["us-gaap:StockIssuedDuringPeriodSharesConversionOfConvertibleSecurities"], y, common)
            if conv else np.nan])
        fee_shares = year_total(x, ["us-gaap:StockIssuedDuringPeriodSharesConsentFeesToDebtholders",
                                    "amch:StockIssuedDuringPeriodSharesConsentFeesToDebtholders"], y, common)
        split = 10 if y <= 2022 else 1      # 1-for-10 reverse split, August 2023
        rows.append({
            "year": "2026 H1" if y == 2026 else str(y),
            "value_of_shares_issued_for_debt_m": value / 1e6,
            "shares_issued_for_debt_m_split_adjusted": shares / 1e6 / split,
            "value_per_share_split_adjusted": (value / shares * split) if shares else np.nan,
            "value_of_fee_shares_to_lenders_m": (fee / 1e6) if pd.notna(fee) else 0.0,
            "fee_shares_m": (fee_shares / 1e6) if pd.notna(fee_shares) else 0.0,
            "gain_loss_on_debt_extinguishment_m": annual_flow(x, ["us-gaap:GainsLossesOnExtinguishmentOfDebt"], y),
        })
    return pd.DataFrame(rows).round(2)


def market_rates():
    m = pd.read_csv("data/rates_monthly.csv", parse_dates=["month"]).set_index("month")
    baa = pd.read_csv("data/BAA.csv", parse_dates=["observation_date"]).set_index("observation_date")["BAA"]
    m["baa_corporate"] = baa.reindex(m.index)
    for f, name in [("BAMLH0A0HYM2EY", "high_yield_all"), ("BAMLH0A3HYCEY", "high_yield_ccc")]:
        d = pd.read_csv(f"data/{f}.csv", parse_dates=["observation_date"]).set_index("observation_date")[f]
        m[name] = pd.to_numeric(d, errors="coerce").resample("MS").mean().reindex(m.index)
    return m.round(3)


def main():
    bs = pd.concat([balance_sheet("amc"), balance_sheet("cnk")])
    bs.round(1).to_csv("data/balance_sheet_quarterly.csv", index=False)
    print("Balance sheets:", bs.groupby("company")["date"].agg(["min", "max", "count"]).to_dict("index"))
    print(bs[bs["date"].isin(["2019-12-31", "2025-12-31", "2026-06-30"])]
          [["company", "date", "debt_m", "finance_lease_m", "operating_lease_m", "cash_m"]].round(0).to_string(index=False))

    mat = pd.concat([maturities("amc"), maturities("cnk")])
    mat.to_csv("data/debt_maturities.csv", index=False)

    led, cover = ledger()
    led.to_csv("data/debt_ledger.csv", index=False)
    print("\nLedger coverage (tagged instruments vs balance-sheet total):")
    print(cover.round(1).to_string())

    cf = cash_flow()
    cf.to_csv("data/cash_flow_annual.csv", index=False)
    print("\nCash flow check (should be ~0):", cf.set_index("year")["check_m"].abs().max())

    e4d = equity_for_debt()
    e4d.to_csv("data/equity_for_debt.csv", index=False)
    rates = market_rates()
    rates.to_csv("data/market_rates_monthly.csv")
    print(f"\nMarket rates: {rates.index.min():%Y-%m} to {rates.index.max():%Y-%m}; "
          f"non-empty months: {rates.notna().sum().to_dict()}")


if __name__ == "__main__":
    main()
