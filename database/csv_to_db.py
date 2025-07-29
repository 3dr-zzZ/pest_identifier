import sqlite3
import pathlib
import pandas as pd

DB_PATH   = "../pests.db"      # adjust if you keep the DB elsewhere
CSV_DIR   = pathlib.Path("../data_csv")
TABLES_IN_ORDER = [
    # parents first
    "species", "taxonomies", "diseases", "locations", "references", "medias",
    # bridges next
    "belongs", "distributed", "carries",
    "species_reference"
]
MODE = "replace"  # append: append, replace: replace & reload

def load_table(csv_file: pathlib.Path, conn: sqlite3.Connection):
    print(f"Loading {csv_file.name} …")
    df = pd.read_csv(csv_file)
    # optional: explicit dtypes to avoid float-converted IDs
    # detect columns that contain only whole‑number values
    int_cols = [
        col for col in df.columns
        if df[col].dropna()
                 .apply(lambda v: isinstance(v, (int, float)) and float(v).is_integer())
                 .all()
    ]
    for col in int_cols:
        df[col] = df[col].astype("Int64")  # nullable integer
    df.to_sql(csv_file.stem, conn,
              if_exists=MODE,
              index=False,
              method="multi",      # bulk executemany
              chunksize=1000)

def main():
    conn = sqlite3.connect(DB_PATH)
    # Temporarily disable FK checks if we are going to replace tables
    if MODE == "replace":
        conn.execute("PRAGMA foreign_keys = OFF;")
    for table in TABLES_IN_ORDER:
        csv_path = CSV_DIR / f"{table}.csv"
        if csv_path.exists():
            load_table(csv_path, conn)
        else:
            print(f"⚠  {csv_path.name} not found; skipping")
    # Re‑enable FK enforcement when we’re done
    if MODE == "replace":
        conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    print("✅ All done!")

if __name__ == "__main__":
    main()
