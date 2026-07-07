# Working Student Coding Exercise — Equity Data Analysis

Thanks for taking the time to work on this. It should take roughly 1 hour. There are no trick constraints on tools: use whatever language, libraries or AI assistants you normally would. We are more interested in **how** you reason about data than in a perfect answer.

Participation is voluntary, but it will help us to understand your approach to data analysis and your coding style, and it will help you preparing for our interview and the sort of work you will be doing.

## The Data

`data/prices.csv` contains daily OHLCV data for 100 stocks over the year 2021. The data is dummy data, but it is structured like real-world data. The company names are mostly real, but only for illustrative purposes.

The data is in CSV format, with the following columns:

| Column   | Description                |
| -------- | -------------------------- |
| `date`   | trading date (YYYY-MM-DD)  |
| `isin`   | instrument identifier      |
| `ticker` | short symbol               |
| `name`   | company name               |
| `open`   | opening price              |
| `high`   | daily high                 |
| `low`    | daily low                  |
| `close`  | closing price              |
| `volume` | shares traded              |

## Time Frame for This Task

- **X (start)** = `2021-06-01`
- **Y (end)** = `2021-10-13`

## Tasks

1. Which are the **top 5** performing titles from day X to day Y?
2. By how much did they increase?
3. **Bonus:** what was each one's 30-day average trading volume on day Y?
4. Create a plot of the best performing titles' price history over the period.
5. What else did you notice while investigating the data?
6. Produce a PDF containing a table with, for the top 5 titles:
   - company name
   - ISIN
   - performance over the time frame
   - 30-day average trading volume

## What to Hand Back

- your code (any structure you like)
- the output PDF
- a short note on your approach, any assumptions you made, and anything about the data that influenced your decisions

Please write down your reasoning where a judgement call was involved — that part matters to us.
