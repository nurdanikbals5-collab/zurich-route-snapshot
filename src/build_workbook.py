"""Build the starter workbook excel/Zurich_Route_Snapshot.xlsx from the Eurostat CSV files.

The workbook only holds raw data and reference lists. All calculated columns, PivotTables and charts
are built by hand in Excel. The script refuses to overwrite an existing workbook so manual work is never lost.

Run: ./.venv/bin/python src/build_workbook.py
"""
from datetime import date
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "excel" / "Zurich_Route_Snapshot.xlsx"

COUNTRIES = {
    "CH": ("Switzerland", "Domestic"),
    "AT": ("Austria", "Europe"), "BE": ("Belgium", "Europe"), "CY": ("Cyprus", "Europe"),
    "CZ": ("Czechia", "Europe"), "DE": ("Germany", "Europe"), "DK": ("Denmark", "Europe"),
    "EL": ("Greece", "Europe"), "ES": ("Spain", "Europe"), "FI": ("Finland", "Europe"),
    "FR": ("France", "Europe"), "HR": ("Croatia", "Europe"), "HU": ("Hungary", "Europe"),
    "IE": ("Ireland", "Europe"), "IS": ("Iceland", "Europe"), "IT": ("Italy", "Europe"),
    "LU": ("Luxembourg", "Europe"), "LV": ("Latvia", "Europe"), "MK": ("North Macedonia", "Europe"),
    "MT": ("Malta", "Europe"), "NL": ("Netherlands", "Europe"), "NO": ("Norway", "Europe"),
    "PL": ("Poland", "Europe"), "PT": ("Portugal", "Europe"), "RO": ("Romania", "Europe"),
    "RS": ("Serbia", "Europe"), "RU": ("Russia", "Europe"), "SE": ("Sweden", "Europe"),
    "SI": ("Slovenia", "Europe"), "TR": ("Türkiye", "Europe"), "UA": ("Ukraine", "Europe"),
    "UK": ("United Kingdom", "Europe"), "XK": ("Kosovo", "Europe"),
    "AE": ("United Arab Emirates", "Middle East & Africa"), "EG": ("Egypt", "Middle East & Africa"),
    "IL": ("Israel", "Middle East & Africa"), "OM": ("Oman", "Middle East & Africa"),
    "QA": ("Qatar", "Middle East & Africa"), "ZA": ("South Africa", "Middle East & Africa"),
    "BR": ("Brazil", "Americas"), "CA": ("Canada", "Americas"), "DO": ("Dominican Republic", "Americas"),
    "MX": ("Mexico", "Americas"), "US": ("United States", "Americas"),
    "CN": ("China", "Asia-Pacific"), "HK": ("Hong Kong", "Asia-Pacific"), "IN": ("India", "Asia-Pacific"),
    "JP": ("Japan", "Asia-Pacific"), "KR": ("South Korea", "Asia-Pacific"),
    "SG": ("Singapore", "Asia-Pacific"), "TH": ("Thailand", "Asia-Pacific"),
}

FOCUS = [
    ("Paris CDG", "CH_LSZH_FR_LFPG", "More weekly flights in summer 2027"),
    ("Nice", "CH_LSZH_FR_LFMN", "More weekly flights in summer 2027"),
    ("Budapest", "CH_LSZH_HU_LHBP", "More flights in summer 2027"),
    ("Hamburg", "CH_LSZH_DE_EDDH", "More flights in summer 2027"),
    ("Montreal", "CH_LSZH_CA_CYUL", "Goes daily in summer 2027"),
    ("Bremen", "CH_LSZH_DE_EDDW", "More flights in summer 2027 (Eurostat: data for 2019 only)"),
    ("Toulouse", "-", "New route, 2x weekly, 25 Jun - 23 Aug 2027 (no Eurostat data)"),
]
SOURCES_2027 = ("bluewin.ch, 2026: https://www.bluewin.ch/en/news/swiss-will-begin-flying-to-a-new-destination-"
                "in-europe-in-2027-li.3641996 · Lufthansa Group business site, 27 Oct 2026")

HEADER = PatternFill("solid", fgColor="1F3864")


def add_table(ws, df, name, number_cols=(), date_cols=()):
    ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([None if pd.isna(v) else v for v in row])
    ref = f"A1:{get_column_letter(len(df.columns))}{len(df) + 1}"
    table = Table(displayName=name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    ws.add_table(table)
    for i, col in enumerate(df.columns, start=1):
        letter = get_column_letter(i)
        ws.column_dimensions[letter].width = max(12, min(45, len(str(col)) + 4))
        if col in number_cols:
            for cell in ws[letter][1:]:
                cell.number_format = "#,##0"
        if col in date_cols:
            for cell in ws[letter][1:]:
                cell.number_format = "mmm yyyy"
    ws.freeze_panes = "A2"


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT.name} already exists - not overwriting manual work.")
    annual = pd.read_csv(ROOT / "data" / "zrh_routes_annual.csv")
    monthly = pd.read_csv(ROOT / "data" / "zrh_routes_monthly.csv")
    info = (ROOT / "data" / "eurostat_download_info.txt").read_text()

    wide = annual.pivot_table(index=["route_code", "partner_airport", "partner_country"], columns="year",
                              values=["passengers", "seats", "flights"]).reset_index()
    wide.columns = [f"{a.capitalize()} {b}" if b != "" else a for a, b in wide.columns]
    wide = wide.rename(columns={"route_code": "Route code", "partner_airport": "Partner airport",
                                "partner_country": "Country code"})
    wide["Partner airport"] = wide["Partner airport"].str.replace(" airport", "", regex=False).str.title()
    years = [2019, 2023, 2024]
    cols = (["Route code", "Partner airport", "Country code"]
            + [f"Passengers {y}" for y in years] + [f"Seats {y}" for y in years] + [f"Flights {y}" for y in years])
    wide = wide.reindex(columns=cols).sort_values("Passengers 2024", ascending=False)

    mon = monthly.rename(columns={"route": "Route", "month": "Month", "passengers": "Passengers",
                                  "seats": "Seats", "flights": "Flights"})
    mon["Month"] = pd.to_datetime(mon["Month"] + "-01").dt.date
    mon = mon[["Route", "Month", "Passengers", "Seats", "Flights"]]

    wb = Workbook()
    about = wb.active
    about.title = "About"
    lines = [
        ("Zurich Route Snapshot", True),
        ("Question: Does 2024 data support the routes where SWISS adds flights in summer 2027?", False),
        ("", False),
        ("Source: Eurostat, dataset avia_par_ch (air passenger transport routes between partner airports "
         "and main airports in Switzerland)", False),
        *[(line, False) for line in info.strip().splitlines()],
        ("", False),
        ("Definitions", True),
        ("Passengers = passengers carried (both directions, all airlines on the airport pair)", False),
        ("Seats = seats available on commercial passenger flights", False),
        ("Flights = commercial passenger flights", False),
        ("", False),
        ("Limitations", True),
        ("Data covers all airlines on a route, not only SWISS.", False),
        ("No revenue or cost data: route profitability cannot be judged.", False),
        ("No split between local and transfer passengers.", False),
        ("Latest full year is 2024. Eurostat lists only main partner airports (e.g. Bremen only in 2019).", False),
        ("", False),
        ("How this file was made", True),
        ("The data was downloaded with a Python script written by an AI coding assistant "
         "(src/download_eurostat.py). All calculated columns, PivotTables and charts are built by hand.", False),
        (f"Workbook created: {date.today().isoformat()}", False),
    ]
    for text, bold in lines:
        about.append([text])
        about.cell(about.max_row, 1).font = Font(bold=bold, size=14 if text == "Zurich Route Snapshot" else 11)
    about.column_dimensions["A"].width = 120
    for row in about.iter_rows():
        row[0].alignment = Alignment(wrap_text=True, vertical="top")

    add_table(wb.create_sheet("Routes"), wide, "tblRoutes", number_cols=cols[3:])
    countries = pd.DataFrame([(k, v[0], v[1]) for k, v in sorted(COUNTRIES.items())],
                             columns=["Country code", "Country", "Region"])
    add_table(wb.create_sheet("Countries"), countries, "tblCountries")
    add_table(wb.create_sheet("Monthly"), mon, "tblMonthly", number_cols=["Passengers", "Seats", "Flights"],
              date_cols=["Month"])
    focus = pd.DataFrame([(r, c, ch, SOURCES_2027) for r, c, ch in FOCUS],
                         columns=["Route", "Route code", "SWISS change summer 2027", "Source"])
    add_table(wb.create_sheet("Focus"), focus, "tblFocus")

    missing = set(wide["Country code"]) - set(COUNTRIES)
    if missing:
        raise SystemExit(f"Country codes without a name: {missing}")
    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(f"saved {OUT} | routes: {len(wide)} | monthly rows: {len(mon)}")


if __name__ == "__main__":
    main()
