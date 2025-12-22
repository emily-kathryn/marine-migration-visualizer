import pandas as pd
from distance import haversine_km

CSV_PATH = "data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv"

# 1) Load + select only what we need
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()

df = df[[
    "individual-local-identifier",
    "timestamp",
    "location-lat",
    "location-long",
]].copy()

df = df.rename(columns={
    "individual-local-identifier": "animal_id",
    "location-lat": "latitude",
    "location-long": "longitude",
})

# 2) Clean types
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df = df.dropna(subset=["animal_id", "timestamp", "latitude", "longitude"])

# 3) Sort so "previous point" makes sense
df = df.sort_values(["animal_id", "timestamp"]).copy()

# 4) Create previous point columns per animal
df["prev_lat"] = df.groupby("animal_id")["latitude"].shift(1)
df["prev_lon"] = df.groupby("animal_id")["longitude"].shift(1)

# 5) Distance from previous point -> current point
df["segment_km"] = haversine_km(df["prev_lat"], df["prev_lon"], df["latitude"], df["longitude"])

# First point has no previous point → NaN → set to 0
df["segment_km"] = df["segment_km"].fillna(0.0)

# 6) Summarize total distance per turtle
totals = (
    df.groupby("animal_id")["segment_km"]
      .sum()
      .reset_index()
      .rename(columns={"segment_km": "total_km"})
      .sort_values("total_km", ascending=False)
)

print("Top 10 turtles by total distance (km):")
print(totals.head(10))

# Save results (this is your first real project output artifact)
totals.to_csv("outputs/total_distance_per_turtle.csv", index=False)
print("\nSaved: outputs/total_distance_per_turtle.csv")