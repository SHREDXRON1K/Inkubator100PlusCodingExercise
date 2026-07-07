'''
INKUBATOR 100 PLUS GMBH CODING EXERCISE
This code analyses an OHLCV data in csv format and gives the report about top 5 performers in pdf format and its plot diagram as png
@author - Astero Wahyu Athala  
'''

import pandas as pd
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

INPUT_CSV_PATH = "/home/ast_t480/HDA/Docs/Werkstudent/Interview/Inkubator100/CodingExercise/CodingExcercise/data/prices.csv"
OUTPUT_PLOT_PATH = "/home/ast_t480/HDA/Docs/Werkstudent/Interview/Inkubator100/CodingExercise/CodingExcercise/output/plotdiagram.png"
OUTPUT_PDF_PATH = "/home/ast_t480/HDA/Docs/Werkstudent/Interview/Inkubator100/CodingExercise/CodingExcercise/output/report.pdf"

SUSPICIOUS_JUMP_THRESHOLD = 0.5
JUMP_REVERSION_TOLERANCE = 0.05

START_TIME_FRAME = "2021-06-01"
END_TIME_FRAME = "2021-10-13"
TRADING_DAYS_FOR_VOLUME_AVERAGE = 30
TOP_N_PERFORMERS = 5

REQUIRED_PRICE_VALUE = ["open", "high", "low", "close", "volume"]

#LOAD DATA
def load_file (csv_path : str) -> dict[str, pd.DataFrame] : 
    dict_data_frames: dict[str, pd.DataFrame] = {}
    raw_data = pd.read_csv(csv_path)
    raw_data["date"] = pd.to_datetime(raw_data["date"])

    for ticker_symbol, ticker_data in raw_data.groupby("ticker") : 
        # clean the data, just in case
        ticker_data = ticker_data.drop_duplicates(subset="date")
        ticker_data = ticker_data.dropna(subset=REQUIRED_PRICE_VALUE)

        ticker_data = ticker_data.set_index("date")
        dict_data_frames[ticker_symbol] = ticker_data

    return dict_data_frames

def flag_suspicious_jumps (dict_data_frames : dict[str, pd.DataFrame]) -> dict[str, dict] :

    flagged_tickers: dict[str, dict] = {}

    for ticker_symbol, ticker_data in dict_data_frames.items() : 
        jump = ticker_data["close"].pct_change()
        largest_absolute_jump = jump.abs().max()

        if largest_absolute_jump > SUSPICIOUS_JUMP_THRESHOLD :
            jump_date = jump.abs().idxmax()
            jump_row_position = ticker_data.index.get_loc(jump_date)
            price_before_jump = ticker_data["close"].iloc[jump_row_position - 1]
            has_next_day = (jump_row_position + 1) < len(ticker_data)

            if has_next_day :
                price_next_day = ticker_data["close"].iloc[jump_row_position + 1]
                relative_difference = abs(price_next_day - price_before_jump) / price_before_jump
                price_reverted = relative_difference < JUMP_REVERSION_TOLERANCE

            else :
                price_reverted = None

            flagged_tickers[ticker_symbol] = {
                    "day": jump_date,
                    "magnitude": largest_absolute_jump,
                    "reverts": price_reverted,
                }
        
    return flagged_tickers
    
def compute_top_perfomers(data_frames : dict[dict, pd.DataFrame]) -> pd.DataFrame : 
    performance_records = []

    for ticker_symbol, ticker_data in data_frames.items() : 
        window = ticker_data.loc[(ticker_data.index >= START_TIME_FRAME) & (ticker_data.index <= END_TIME_FRAME)]

        if window.empty:
            continue

        price_at_start = window["close"].iloc[0]
        price_at_end = window["close"].iloc[-1]
        percent_change = (price_at_end / price_at_start - 1) * 100

        # Trailing 30 *trading days* (not calendar days) up to end_date —
        # trading calendars exclude weekends/holidays, so this is the
        # correct window for "average daily volume" in a market context.
        trailing_volume_window = ticker_data.loc[ticker_data.index <= END_TIME_FRAME]["volume"]
        average_volume_30_days = trailing_volume_window.tail(TRADING_DAYS_FOR_VOLUME_AVERAGE).mean()

        performance_records.append({
            "ticker": ticker_symbol,
            "name": ticker_data["name"].iloc[0],
            "isin": ticker_data["isin"].iloc[0],
            "pct_change": percent_change,
            "avg_volume_30d": average_volume_30_days,
        })

    performance_table = pd.DataFrame(performance_records)
    top_performers = performance_table.nlargest(TOP_N_PERFORMERS, "pct_change").reset_index(drop=True)
    return top_performers


def plot_top_performers(
    data_frames: dict[str, pd.DataFrame],
    top_performers: pd.DataFrame,
) -> None:
    """
    Plot the closing-price history of each top performer over the
    analysis window and save the chart as a PNG file.

    Args:
        ticker_universe: output of load_universe().
        top_performers: output of compute_top_performers().
        start_date: first date of the analysis window.
        end_date: last date of the analysis window.
        output_path: file path to save the resulting PNG chart to.
    """
    plt.figure(figsize=(10, 6))

    for _, performer_row in top_performers.iterrows():
        ticker_symbol = performer_row["ticker"]
        ticker_data = data_frames[ticker_symbol]
        window = ticker_data.loc[(ticker_data.index >= START_TIME_FRAME) & (ticker_data.index <= END_TIME_FRAME)]

        chart_label = f"{ticker_symbol} ({performer_row['pct_change']:.1f}%)"
        plt.plot(window.index, window["close"], label=chart_label)

    plt.title(f"Top {len(top_performers)} Performers: {START_TIME_FRAME} to {END_TIME_FRAME}")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_PATH, dpi=150)
    plt.close()


def generate_pdf_report(top_performers: pd.DataFrame) -> None:
    """
    Build a one-page PDF with a table of the top performers: company name,
    ISIN, % performance, and 30-day average trading volume.
    """
    document = SimpleDocTemplate(OUTPUT_PDF_PATH, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
 
    title = Paragraph(f"Top {len(top_performers)} Performers: {START_TIME_FRAME} to {END_TIME_FRAME}", styles["Title"])
    story.append(title)
    story.append(Spacer(1, 20))
 
    header_row = ["Company Name", "ISIN", "Performance", "30-Day Avg Volume"]
    data_rows = [
        [
            row["name"],
            row["isin"],
            f"{row['pct_change']:.2f}%",
            f"{row['avg_volume_30d']:,.0f}",
        ]
        for _, row in top_performers.iterrows()
    ]
    table_data = [header_row] + data_rows
 
    table = Table(table_data, colWidths=[160, 110, 90, 130])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
 
    story.append(table)
    document.build(story)


def main() -> None:
    ticker_universe = load_file(INPUT_CSV_PATH)
    logger.info(f"\nLoaded {len(ticker_universe)} tickers\n")

    suspicious_jumps = flag_suspicious_jumps(ticker_universe)
    logger.info(f"Suspicious jumps flagged: {len(suspicious_jumps)}")
    for ticker_symbol, jump_info in suspicious_jumps.items():
        logger.info(
            f"  {ticker_symbol}: {jump_info['day'].date()} "
            f"move={jump_info['magnitude']:.1%} reverts={jump_info['reverts']}"
        )

    top_performers = compute_top_perfomers(ticker_universe)
    print("\nTop performers:")
    print(top_performers.to_string(index=False))

    plot_top_performers(ticker_universe, top_performers)
    logger.info(f"\nSaved chart to {OUTPUT_PLOT_PATH}")

    generate_pdf_report(top_performers)
    logger.info(f"\nSaved pdf to {OUTPUT_PDF_PATH}")

    # --- data quality notes -------------------------------------------
    print("\n--- Data quality notes ---")
    print(
        f"- No 'adj_close' column in the source data; fell back to 'close' "
        f"for all {len(ticker_universe)} tickers."
    )

    row_counts_per_ticker = {ticker: len(data) for ticker, data in ticker_universe.items()}
    min_row_count = min(row_counts_per_ticker.values())
    max_row_count = max(row_counts_per_ticker.values())
    if min_row_count != max_row_count:
        print(
            f"- Row counts vary across tickers ({min_row_count}-{max_row_count} rows). "
            "Comparing % performance across tickers with unequal date coverage "
            "can be misleading."
        )
    else:
        print(f"- All tickers have identical row counts ({min_row_count}).")


if __name__ == "__main__":
    main()





