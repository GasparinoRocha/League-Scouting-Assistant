import psycopg2

# Database connection settings
DB_NAME = "scouting-assistant-db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Create table
cur.execute("""
    DROP TABLE lol_esports_matches CASCADE;
""")

# Clean up
conn.commit()
cur.close()
conn.close()
