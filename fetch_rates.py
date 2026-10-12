"""
fetch_rates.py
Downloads market interest rates from FRED (Federal Reserve Bank of St. Louis), used to
compare what AMC pays on its debt with what the market charged at the time:

    DGS5, DGS10       U.S. Treasury yields, 5 and 10 years (a risk-free benchmark)
    SOFR              the overnight rate that AMC's term loan floats on
    BAMLH0A0HYM2EY    yield on U.S. high-yield ("junk") corporate bonds, all ratings
    BAMLH0A3HYCEY     yield on the lowest-rated (CCC and below) high-yield bonds

No key is needed. FRED can be slow, so each series is retried; if FRED still does not
answer, Treasury yields come from the U.S. Treasury's own site and SOFR from the
New York Fed instead (the junk-bond yields are only on FRED).

Run from the project folder:
    pip install requests pandas
    python fetch_rates.py

Output: data/rates_monthly.csv (monthly averages, % per year)
"""

import io
import os
import time

import pandas as pd
import requests

SERIES = {
    "DGS5": "treasury_5y",
    "DGS10": "treasury_10y",
    "SOFR": "sofr",
    "BAMLH0A0HYM2EY": "high_yield_all",
    "BAMLH0A3HYCEY": "high_yield_ccc",
}
START = "2014-01-01"


def get(url, timeout=120, tries=3):
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt == tries:
                raise
            print(f"    attempt {attempt} failed ({type(e).__name__}), retrying...")
            time.sleep(5 * attempt)


def fred(series_id):
    r = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START}")
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")      # "." marks missing days
    return df.dropna().set_index("date")["value"]


def treasury(column):
    """Daily par yield curve from the U.S. Treasury, one file per year."""
    parts = []
    for year in range(int(START[:4]), pd.Timestamp.today().year + 1):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
               f"daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
               f"&field_tdr_date_value={year}&page&_format=csv")
        df = pd.read_csv(io.StringIO(get(url, timeout=60).text))
        parts.append(df.set_index(pd.to_datetime(df["Date"]))[column])
    return pd.to_numeric(pd.concat(parts), errors="coerce").dropna().sort_index()


def nyfed_sofr():
    end = pd.Timestamp.today().strftime("%Y-%m-%d")
    url = f"https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2018-04-02&endDate={end}"
    rates = get(url, timeout=60).json()["refRates"]
    s = pd.Series({pd.Timestamp(r["effectiveDate"]): r["percentRate"] for r in rates})
    return s.sort_index()


FALLBACKS = {
    "DGS5": ("U.S. Treasury", lambda: treasury("5 Yr")),
    "DGS10": ("U.S. Treasury", lambda: treasury("10 Yr")),
    "SOFR": ("New York Fed", nyfed_sofr),
}


def main():
    os.makedirs("data", exist_ok=True)
    monthly = {}
    for sid, name in SERIES.items():
        print(f"  {sid} ({name})")
        s, source = None, "FRED"
        try:
            s = fred(sid)
        except Exception as e:
            print(f"    FRED did not answer ({type(e).__name__})")
            if sid in FALLBACKS:
                source, fallback = FALLBACKS[sid]
                try:
                    s = fallback()
                except Exception as e2:
                    print(f"    {source} did not answer either ({type(e2).__name__})")
        if s is None or s.empty:
            print("    skipped; the analysis will work without it")
            continue
        monthly[name] = s.resample("MS").mean()
        print(f"    from {source}: {s.index.min():%Y-%m-%d} to {s.index.max():%Y-%m-%d}, {len(s):,} days")
    out = pd.DataFrame(monthly).round(3)
    out.index.name = "month"
    out.to_csv(os.path.join("data", "rates_monthly.csv"))
    print(f"Saved data/rates_monthly.csv ({len(out)} months)")


if __name__ == "__main__":
    main()
