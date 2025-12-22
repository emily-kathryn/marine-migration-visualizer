import pandas as pd
from distance import haversine_km

CSV_PATH = "data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv"

# 1) Load + keep only the core columns
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

# 3) Sort correctly
df = df.sort_values(["animal_id", "timestamp"]).copy()

# 4) Previous point per animal
df["prev_lat"] = df.groupby("animal_id")["latitude"].shift(1)
df["prev_lon"] = df.groupby("animal_id")["longitude"].shift(1)

# 5) Segment distance
df["segment_km"] = haversine_km(df["prev_lat"], df["prev_lon"], df["latitude"], df["longitude"])
df["segment_km"] = df["segment_km"].fillna(0.0)

# 6) Convert timestamps into just the date (daily grouping)
df["date"] = df["timestamp"].dt.date

# 7) Daily distance traveled per animal
daily = (
    df.groupby(["animal_id", "date"])["segment_km"]
      .sum()
      .reset_index()
      .rename(columns={"segment_km": "daily_km"})
)

# 8) Summary status per animal
summary = (
    daily.groupby("animal_id")["daily_km"]
         .agg(avg_daily_km="mean", max_daily_km="max", days_tracked="count", total_km="sum")
         .reset_index()
         .sort_values("total_km", ascending=False)
)


print("Per-animal daily summary (top 10 by total_km):")
print(summary.head(10))

print("\nTop 10 biggest single-day movements:")
print(daily.sort_values("daily_km", ascending=False).head(10))

# Save outputs
daily.to_csv("outputs/daily_distance.csv", index=False)
summary.to_csv("outputs/daily_summary.csv", index=False)
print("\nSaved: outputs/daily_distance.csv and outputs/daily_summary.csv")

