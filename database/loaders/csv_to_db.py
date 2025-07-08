import sqlite3
import pathlib
import pandas as pd

DB_PATH   = "../pests.db"      # adjust if you keep the DB elsewhere
CSV_DIR   = pathlib.Path("../data_csv")
TABLES_IN_ORDER = [
    # parents first
    "species", "diseases", "locations", "controls", "references", "medias",
    # bridges next
    "distributed", "carries",
    "species_control", "species_reference"
]

def load_table(csv_file: pathlib.Path, conn: sqlite3.Connection):
    print(f"Loading {csv_file.name} …")
    df = pd.read_csv(csv_file)
    # optional: explicit dtypes to avoid float-converted IDs
    int_cols = [c for c in df.columns if df[c].dropna().apply(float.is_integer).all()]
    for col in int_cols:
        df[col] = df[col].astype("Int64")  # nullable integer
    df.to_sql(csv_file.stem, conn,
              if_exists="append",  # use 'replace' to wipe & reload
              index=False,
              method="multi",      # bulk executemany
              chunksize=1000)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    for table in TABLES_IN_ORDER:
        csv_path = CSV_DIR / f"{table}.csv"
        if csv_path.exists():
            load_table(csv_path, conn)
        else:
            print(f"⚠  {csv_path.name} not found; skipping")
    conn.commit()
    conn.close()
    print("✅ All done!")

if __name__ == "__main__":
    main()
