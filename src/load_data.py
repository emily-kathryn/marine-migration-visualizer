import pandas as pd

CSV_PATH = "data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv"

# This file is comma-separated (your peek confirmed this)
df = pd.read_csv(CSV_PATH)

# Clean column names just in case there are hidden spaces
df.columns = df.columns.str.strip()

# Keep only what we need (plus outlier flag for filtering)
df = df[[
    "individual-local-identifier",
    "timestamp",
    "location-lat",
    "location-long",
    "algorithm-marked-outlier",
    "sensor-type",
]].copy()

# Rename into our standard names
df = df.rename(columns={
    "individual-local-identifier": "animal_id",
    "location-lat": "latitude",
    "location-long": "longitude",
})

# Parse and clean types
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

# Drop broken rows
df = df.dropna(subset=["animal_id", "timestamp", "latitude", "longitude"])

# Filter out obvious outliers if marked (only removes True values)
df = df[df["algorithm-marked-outlier"] != True]

# Sanity checks
print(df.head())
print("\nRows:", len(df))
print("Animals:", df["animal_id"].nunique())
print("Time range:", df["timestamp"].min(), "to", df["timestamp"].max())
print("\nSensor types (top):")
print(df["sensor-type"].value_counts().head(10))