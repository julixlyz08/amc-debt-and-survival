# From box office to balance sheet: what four projects say about AMC

**The question behind the series:** AMC is the world's largest cinema chain, and its guests now spend more per visit than ever. So why did its share price fall 97%, and can the company survive on what its theatres earn?

**The answer, in one paragraph:** AMC's theatres are a viable business. They cover their own running costs, and guests spend about 50% more per visit than in 2015. The company around them is not yet viable: debt taken on for acquisitions and to get through the pandemic now costs about 12% a year, close to what the riskiest borrowers pay. Since 2020, shareholders have covered the gap: AMC sold $3.9bn of new shares and swapped debt for about 36% of today's shares. That is why the stock collapsed while attendance recovered, and why it no longer reacts to attendance. AMC needs about **168 million U.S. guests a year** to stop burning cash. It has **165 million**, and the central forecast is **170 million**. In 2029, **$3.2bn of debt falls due**. Whether AMC refinances on its own or sells more shares depends on whether attendance, spend per guest and costs move clearly past that line before then.

> Independent projects using public data (SEC filings, TMDB, market prices, FRED, U.S. Treasury). Not affiliated with AMC Entertainment, Cinemark or TMDB. Not investment advice.

---

## 1. How the four projects connect

Each project answers one question and hands the next one its starting point.

The series builds on my separate [movie profitability analysis](https://github.com/julixlyz08/movie_profitability_analysis) (franchise films earn 3.3x their budget vs 1.4x for standalone films; summer and December releases do best). Its film data (release dates, budgets and franchise status) was used to test the attendance forecast in project 1.

| # | Project | Question | Answer | What it hands on |
|---|---|---|---|---|
| 1 | [Attendance forecast](https://github.com/julixlyz08/amc-attendance-forecast-subscription) | How many people will go to AMC next year? | About 170 million U.S. guests (8-in-10 range: 151 to 215 million). Knowing the film slate did not improve the forecast. | The attendance scenarios used in project 4 |
| 2 | [Stock vs attendance](https://github.com/julixlyz08/amc-stock-vs-attendance) | Does the share price follow attendance? | No. Share issuance explains the whole 97% fall: the share count grew 70 to 86 times. | Why were all those shares sold? |
| 3 | [How AMC makes money](https://github.com/julixlyz08/amc-how-it-makes-money) | Where does each guest's money go? | Snacks now earn AMC as much as tickets. The theatres roughly break even, and interest turns that into large losses. | The cost structure (52.5% variable, $1.9bn fixed) used in project 4 |
| 4 | [Debt and survival](https://github.com/julixlyz08/amc-debt-and-survival) | Can AMC carry its debt? | Only just. About 168m guests a year at today's rates against 165m today, and $3.2bn due in 2029. | This conclusion |

## 2. The story in five steps

1. **Guests come less but spend more.** U.S. attendance is about a fifth below 2015. Spend per guest is up about 50%, and all the growth beyond inflation came from food and drink (+36% after inflation). Ticket prices only kept pace with inflation. *(Projects 1 and 3)*
2. **The business is hit-driven, and the hits can't be planned.** Returns depend on franchises and release timing (my separate movie profitability project), yet knowing the release calendar did not improve the attendance forecast (project 1). Attendance is the one big driver AMC cannot control.
3. **The costs are not hit-driven.** About $1.9bn a year of AMC's costs are fixed (rent, staff, head office): the same as before the pandemic, on about 12% less revenue. At today's attendance, the theatres roughly break even before interest. *(Project 3)*
4. **The debt turned a thin margin into a loss, and shareholders paid for it.** Interest grew five-fold from 2015 to 2025. Since 2023 it has exceeded everything the theatres earn before depreciation. From 2020 to mid-2026, share sales ($3.9bn) covered all of the interest paid ($2.3bn) and more. *(Projects 2, 3 and 4)*
5. **The future comes down to one line and one date.** About 168m guests a year to self-fund at today's rates. $3.2bn of debt due in 2029. *(Projects 1 and 4)*

## 3. So what?

### Two break-even lines, not one
The series produced two break-even figures, and the gap between them matters:
- **About 168 million U.S. guests a year** to **stop burning cash**: pay cash interest and keep investing in the theatres (project 4).
- **About 184 million** to **report a profit**: cover depreciation and all interest expense, including interest added to the debt instead of paid (project 3).

AMC is close to the first line and far from the second. It can survive near 168m guests, but it doesn't create value for shareholders until it gets well past 184m. In 2019, AMC had 250 million U.S. guests.

### Attendance is not the biggest lever AMC controls
AMC can't choose how many people come, but it can work on what they spend and what it costs to run the theatres. Using the survival model at today's position (165m guests, 10% interest rate), here is what each change does to free cash flow a year:

| Change | Effect on free cash a year |
|---|---|
| Guests spend **5% more** (about $1.60 per visit) | **+$129m** |
| Fixed costs **5% lower** (about $95m of rent, staff and overhead) | **+$102m** |
| **5 million more** U.S. guests | +$78m |
| Interest rate **1 point lower** | +$37m |

Any one of the first three gets AMC from −$64m to positive. A small gain in spend per guest or in costs is worth more than a good year at the box office. That fits project 3, where food and drink is the only part of the business growing faster than inflation. **The levers AMC controls (pricing, food and drink, premium formats, rent renegotiation, closing weak theatres) matter more than the film slate it doesn't control.**

### For shareholders: attendance won't fix the share price
Better attendance helps AMC survive, but the stock didn't follow attendance before (project 2), and the reason is still there. Each time the company is short of cash, lenders and new shareholders get a bigger slice. Debt swapped for shares went from $137 a share in 2021 to $1.60 in 2026 (split-adjusted). Until AMC stops needing new money, existing shareholders absorb the shortfall. That is a fact about the capital structure, not a forecast of the share price.

### For lenders: the 2029 refinancing is the real test
Even in the base case, AMC has about $0.7bn of cash at the end of 2029 against $3.2bn due that year. The refinancing will be priced on the attendance trend of 2027 and 2028. Above the line, AMC can argue for a lower rate. Each point lower is worth about 2.4 million guests of break-even. Below it, the low scenario runs out of cash by late 2028, and AMC is back to swapping debt for shares.

### For the industry: survival is about structure as well as demand
Cinemark faced the same pandemic and the same film slate. In 2025 it earned an operating profit of $10.70 per $100 of revenue; AMC lost $0.40. The gap is rent, theatre running costs and interest, not demand. AMC's problem is mostly its balance sheet and lease commitments. Moviegoing isn't dying.

## 4. What to watch (and the thresholds that matter)

| Signal | Where to find it | The line that matters |
|---|---|---|
| U.S. attendance | Weekly box office, AMC's quarterly results | About 168m a year to self-fund (roughly 3.2m guests a week on average) |
| Food and drink spend per guest | Quarterly results | Each 5% gain in total spend is worth about $129m a year |
| Rate on new or refinanced debt | Refinancing announcements | Today about 12%. Every point lower cuts break-even by about 2.4m guests |
| New shares sold or swapped for debt | 8-K filings, quarterly share count | Any sale means the cash gap still exists |
| Cash on hand | Quarterly balance sheet | About $250m minimum to run the business |
| 2029 maturities | Debt note in the 10-K | $3.2bn to refinance |

## 5. What would change the conclusion

- **A run of films that lifts attendance above about 185m guests** for several quarters would put AMC clearly in self-funding territory and make refinancing much easier (the high scenario adds about $0.7bn of cash a year).
- **A refinancing well below 12%** would lower the line. At 6%, about 160m guests would be enough.
- **Another shock to attendance** (strikes, a weak slate, a shift to streaming windows) would bring the low scenarios into play within two years.
- **The model is deliberately simple:** no taxes, no closures or openings, and international theatres move with the U.S. The figures are best read as a range, not to the million.

## Bottom line

AMC's theatres are a viable business. Its balance sheet makes the whole company fragile. **The stock collapsed because of dilution, not lost guests; the losses come from interest, not operations; and survival depends on a thin margin of attendance, spend and costs, tested in 2029.** AMC's best path out runs through the levers it controls (spend per guest, costs and refinancing terms) more than through the film slate.

---

**Methods used across the series:** SEC EDGAR XBRL data, both company-facts summaries and every 10-Q and 10-K parsed directly; the TMDB API; Yahoo Finance prices, corrected for distributions it misses; FRED, U.S. Treasury and New York Fed rates; BLS consumer prices. The analysis uses rolling out-of-sample forecast tests, event studies with permutation tests, fixed/variable cost decomposition, a cash-flow and debt model with a scenario grid, and interactive Tableau dashboards. Tools: Python (pandas, numpy, matplotlib, statsmodels), SQL/SQLite and Tableau.
