# AMC in four projects: attendance, stock, business, debt

One company, followed from the ticket counter to the balance sheet, with public data only (SEC filings, market prices, FRED). Each project answers one question and hands the next project its starting point.

| # | Project | Question | Answer in one line |
|---|---|---|---|
| 1 | [Attendance forecast and subscription model](https://github.com/julixlyz08/amc-attendance-forecast-subscription) | How many people will go to AMC theatres next year? | About 170 million U.S. guests (8-in-10 range 151 to 215 million). Simple seasonal methods beat models using the film slate. |
| 2 | [Stock vs attendance](https://github.com/julixlyz08/amc-stock-vs-attendance) | Does the share price follow attendance? | No measurable link. The 97% fall in the price since 2019 is explained by issuing new shares, not by fewer guests. |
| 3 | [How AMC makes money](https://github.com/julixlyz08/amc-how-it-makes-money) | Where does each guest's money go? | Snacks now earn AMC as much as tickets. The theatres roughly break even, and interest turns that into losses. |
| 4 | [Debt and survival](https://github.com/julixlyz08/amc-debt-and-survival) | Can AMC carry its debt? | It needs about 168 million U.S. guests a year at today's rates and has 165 million. $3.2bn falls due in 2029. |

## The story

1. **Guests spend more but come less.** U.S. attendance is about a fifth below 2015. Spend per guest rose 50%, but only snacks beat inflation (+36% after inflation); ticket prices merely kept up. *(Projects 1 and 3)*
2. **The theatres cover their own costs, barely.** About 52 cents of each revenue dollar goes on costs that rise with business (studios' share, food), and about $1.9bn a year is fixed (rent, staff, head office). At today's attendance, that leaves roughly break-even operating results. *(Project 3)*
3. **The debt is the problem.** Built up by acquisitions in 2016-17 and the pandemic, it now costs about 12% a year, close to what the riskiest borrowers pay. Interest has exceeded what the theatres earn before depreciation every year since 2023. *(Projects 3 and 4)*
4. **Shareholders paid the bill.** From 2020 to 2026, AMC sold $3.9bn of shares to cover $2.3bn of interest and its investment, and swapped debt for about 36% of today's shares. That is why the share price collapsed while the business recovered, and why the stock does not react to attendance. *(Projects 2 and 4)*
5. **What happens next depends on attendance clearing a line.** About 168 million U.S. guests a year pays the interest at today's rates. The forecast's central case is just above it; the low case runs out of cash by the end of 2028. In 2029, $3.2bn of debt has to be refinanced. *(Projects 1 and 4)*

## Methods used across the series

- **Data:** SEC EDGAR, both the XBRL company-facts summaries and every 10-Q and 10-K's full XBRL data, parsed directly; Yahoo Finance prices, with corrections for distributions Yahoo misses; FRED, U.S. Treasury and New York Fed rates; BLS consumer prices.
- **Analysis:** rolling out-of-sample forecast tests; event studies with permutation tests; fixed/variable cost decomposition and break-even analysis; a cash-flow and debt model with a scenario grid.
- **Tools:** Python (pandas, numpy, matplotlib, statsmodels) and Tableau.
- **Checks built in:** every income statement and cash-flow split reconciles to reported totals, and every data correction is documented in the repository that uses it.

> Independent projects using public data. Not affiliated with AMC Entertainment or Cinemark. Not investment advice.
