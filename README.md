# Zurich Route Snapshot

A small network analysis of Zurich Airport routes with public Eurostat data.

**Question:** Does 2024 data support the routes where SWISS adds flights in summer 2027
(Paris, Nice, Budapest, Hamburg, Montreal)?

Status: work in progress (November 2026).

## Data
- Eurostat dataset `avia_par_ch`: passengers carried, seats and commercial passenger flights per airport pair,
  2019, 2023 and 2024, plus monthly data 2023–2024 for the focus routes.
- Each route covers **all airlines** on the airport pair, both directions.

## Limitations
- Not SWISS-only data; no revenue or cost data, so route profitability cannot be judged.
- No split between local and transfer passengers.
- Latest full year is 2024. Eurostat lists only main partner airports (Zurich–Bremen only for 2019;
  Toulouse, Niš and Bengaluru have no data).

## How it was made
- `src/download_eurostat.py` downloads the data and `src/build_workbook.py` creates the starter workbook.
  Both scripts were written by an AI coding assistant; I defined the question and checked the results.
- The analysis in `excel/Zurich_Route_Snapshot.xlsx` (calculated columns, PivotTables, charts) is built by hand.
