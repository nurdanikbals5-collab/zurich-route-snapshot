"""Download route data for Zurich airport (LSZH) from Eurostat dataset avia_par_ch.

avia_par_ch = "Air passenger transport routes between partner airports and main airports in Switzerland".
Each route is an airport pair (e.g. CH_LSZH_UK_EGLL = Zurich - London Heathrow) and covers ALL airlines
on that pair, both directions together.

Measures used:
    PAS / PAS_CRD   passengers carried
    SEAT / ST_PAS   seats available on passenger flights
    FLIGHT / CAF_PAS  commercial passenger flights

Output (data/):
    zrh_routes_annual.csv   one row per route and year (2019, 2023, 2024)
    zrh_routes_monthly.csv  one row per route and month (2023-01 .. 2024-12) for the six focus routes
    eurostat_download_info.txt  dataset update date and download date

Run: ./.venv/bin/python src/download_eurostat.py
"""
import datetime as dt
from pathlib import Path

import pandas as pd
import requests

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/avia_par_ch"
DATA = Path(__file__).resolve().parents[1] / "data"

MEASURES = [("PAS", "PAS_CRD", "passengers"), ("SEAT", "ST_PAS", "seats"), ("FLIGHT", "CAF_PAS", "flights")]
YEARS = ["2019", "2023", "2024"]

# Routes where SWISS adds frequencies in summer 2027 (Paris, Nice, Budapest, Hamburg) and Montreal
# (goes daily). Bremen also gets more flights, but Eurostat lists Zurich-Bremen only for 2019;
# Toulouse, Nis and Bengaluru have no Zurich data at all.
FOCUS = {
    "CH_LSZH_FR_LFPG": "Paris CDG",
    "CH_LSZH_FR_LFMN": "Nice",
    "CH_LSZH_HU_LHBP": "Budapest",
    "CH_LSZH_DE_EDDH": "Hamburg",
    "CH_LSZH_CA_CYUL": "Montreal",
}


def fetch(params):
    """Return the Eurostat JSON-stat answer as a long DataFrame (one row per value)."""
    r = requests.get(API, params=params, timeout=120)
    r.raise_for_status()
    d = r.json()
    ids, size = d["id"], d["size"]
    cats = []
    for k in ids:
        index = d["dimension"][k]["category"]["index"]
        cats.append(sorted(index, key=index.get))
    labels = d["dimension"]["airp_pr"]["category"]["label"]
    rows = []
    for flat, value in d["value"].items():
        # turn the flat JSON-stat index back into one position per dimension
        rest, pos = int(flat), []
        for s in reversed(size):
            rest, p = divmod(rest, s)
            pos.append(p)
        pos.reverse()
        row = {k: cats[i][pos[i]] for i, k in enumerate(ids)}
        row["value"] = value
        rows.append(row)
    df = pd.DataFrame(rows)
    df["route_label"] = df["airp_pr"].map(labels)
    return df, d.get("updated")


def measure_name(df):
    names = {(u, m): n for u, m, n in MEASURES}
    return [names.get((u, m)) for u, m in zip(df["unit"], df["tra_meas"])]


def main():
    DATA.mkdir(exist_ok=True)
    base = [("unit", u) for u, _, _ in MEASURES] + [("tra_meas", m) for _, m, _ in MEASURES]

    # 1) annual values for all Swiss airport pairs, then keep Zurich
    annual, updated = fetch([("format", "JSON"), ("lang", "EN"), ("freq", "A")] + base +
                            [("time", y) for y in YEARS])
    annual = annual[annual["airp_pr"].str.startswith("CH_LSZH_")].copy()
    annual["measure"] = measure_name(annual)
    annual = annual.dropna(subset=["measure"])
    wide = annual.pivot_table(index=["airp_pr", "route_label", "time"], columns="measure",
                              values="value", aggfunc="sum").reset_index()
    wide = wide.rename(columns={"airp_pr": "route_code", "time": "year"})
    wide["partner_country"] = wide["route_code"].str.split("_").str[2]
    wide["partner_icao"] = wide["route_code"].str.split("_").str[3]
    wide["partner_airport"] = wide["route_label"].str.replace("ZURICH airport - ", "", regex=False)
    cols = ["route_code", "partner_airport", "partner_country", "partner_icao", "year",
            "passengers", "seats", "flights"]
    wide = wide.reindex(columns=cols).sort_values(["route_code", "year"])
    wide.to_csv(DATA / "zrh_routes_annual.csv", index=False)

    # 2) monthly values 2023-2024 for the six focus routes
    months = [f"{y}-{m:02d}" for y in (2023, 2024) for m in range(1, 13)]
    monthly, _ = fetch([("format", "JSON"), ("lang", "EN"), ("freq", "M")] + base +
                       [("airp_pr", r) for r in FOCUS] + [("time", t) for t in months])
    monthly["measure"] = measure_name(monthly)
    monthly = monthly.dropna(subset=["measure"])
    mw = monthly.pivot_table(index=["airp_pr", "time"], columns="measure", values="value",
                             aggfunc="sum").reset_index()
    mw = mw.rename(columns={"airp_pr": "route_code", "time": "month"})
    mw.insert(1, "route", mw["route_code"].map(FOCUS))
    mw = mw.reindex(columns=["route_code", "route", "month", "passengers", "seats", "flights"])
    mw.sort_values(["route", "month"]).to_csv(DATA / "zrh_routes_monthly.csv", index=False)

    (DATA / "eurostat_download_info.txt").write_text(
        f"Dataset: avia_par_ch (Eurostat)\nDataset last updated: {updated}\n"
        f"Downloaded: {dt.date.today().isoformat()}\nAPI: {API}\n")
    print(f"annual rows: {len(wide)}  routes: {wide['route_code'].nunique()}  monthly rows: {len(mw)}")
    print(f"dataset updated: {updated}")


if __name__ == "__main__":
    main()
