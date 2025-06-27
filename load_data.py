import pandas as pd
import psycopg2
import io

# Connection settings
DB_NAME     = "scouting-assistant-db"
DB_USER     = "postgres"
DB_PASSWORD = "postgres"
DB_HOST     = "localhost"
DB_PORT     = "5432"

CSV_FILES = [
    "data/2022_LoL_esports_match_data_from_OraclesElixir.csv",
    "data/2023_LoL_esports_match_data_from_OraclesElixir.csv",
    "data/2024_LoL_esports_match_data_from_OraclesElixir.csv",
    "data/2025_LoL_esports_match_data_from_OraclesElixir.csv",     # newest file must be last
]
TABLE_NAME = "lol_esports_matches"

# Load schema from 2022 file
schema_df = pd.read_csv(CSV_FILES[0], low_memory=False)

# Define types: use float64 for numeric
dtype_map = {}
pg_columns = []

for col, dt in schema_df.dtypes.items():
    if pd.api.types.is_integer_dtype(dt) or pd.api.types.is_float_dtype(dt):
        dtype_map[col] = "float64"
        pg_columns.append(f'"{col}" DOUBLE PRECISION')
    elif pd.api.types.is_bool_dtype(dt):
        dtype_map[col] = "boolean"
        pg_columns.append(f'"{col}" BOOLEAN')
    elif pd.api.types.is_datetime64_any_dtype(dt):
        dtype_map[col] = "datetime64[ns]"
        pg_columns.append(f'"{col}" TIMESTAMP')
    else:
        dtype_map[col] = "string"
        pg_columns.append(f'"{col}" TEXT')

# SQL to recreate the table
columns_sql = ",\n    ".join(pg_columns)
create_stmt = f"""
DROP TABLE IF EXISTS {TABLE_NAME};
CREATE TABLE {TABLE_NAME} (
    {columns_sql}
);
"""

# Connect
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute(create_stmt)
print("Table created ✅")

# Load and insert CSVs
for csv_file in CSV_FILES:
    print(f"\n📥 Loading: {csv_file}")
    df = pd.read_csv(csv_file, dtype=dtype_map, low_memory=False)

    # Write to in-memory CSV buffer
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    print(f"📤 Inserting {len(df)} rows using COPY ...")
    with conn.cursor() as cur:
        cur.copy_expert(f"COPY {TABLE_NAME} FROM STDIN WITH CSV", buffer)
    print("✅ Insert complete.")

conn.close()
