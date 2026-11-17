# Zurich Route Snapshot

A small network analysis of Zurich Airport routes with public Eurostat data.

**Question:** Does 2024 data support the routes where SWISS adds flights in summer 2027
(Paris, Nice, Budapest, Hamburg, Montreal)?

**One-page summary:** [docs/Zurich_Route_Snapshot_Summary.pdf](docs/Zurich_Route_Snapshot_Summary.pdf)

## Results (2024, all airlines)
1. Long-haul routes are fuller than European ones: load factor Americas 86% and Asia-Pacific 88% vs. Europe 80%;
   domestic routes reach only 58%.
2. Montreal (92% full, 109% of 2019 passengers) and Budapest (105% of 2019) clearly support more flights.
3. Nice and Hamburg look weak over the full year (75%, below 2019), but reach 80% in June–August, about
   7 points above the rest of the year. This fits SWISS adding flights there for the summer season.
4. Paris is stable all year (78–80%), so the summer pattern alone does not explain the extra Paris flights.

| Route | Load factor 2024 | Passengers vs. 2019 | Load factor Jun–Aug | Rest of year |
|---|---|---|---|---|
| Paris CDG | 78.8% | 77.4% | 80.0% | 78.4% |
| Nice | 74.8% | 77.5% | 80.0% | 72.6% |
| Hamburg | 74.7% | 84.6% | 80.1% | 72.9% |
| Budapest | 79.6% | 105.2% | 83.5% | 78.3% |
| Montreal | 91.7% | 109.1% | 94.7% | 90.7% |

Load factor = passengers carried / seats available.

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
