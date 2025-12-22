import pandas as pd
from distance import haversine_km

CSV_PATH = "data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv"

# ---------------------------
# 1. Load and clean core data
# ---------------------------
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

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df = df.dropna(subset=["animal_id", "timestamp", "latitude", "longitude"])

# ---------------------------
# 2. Segment distances
# ---------------------------
df = df.sort_values(["animal_id", "timestamp"]).copy()

df["prev_lat"] = df.groupby("animal_id")["latitude"].shift(1)
df["prev_lon"] = df.groupby("animal_id")["longitude"].shift(1)

df["segment_km"] = haversine_km(
    df["prev_lat"],
    df["prev_lon"],
    df["latitude"],
    df["longitude"]
).fillna(0.0)

# ---------------------------
# 3. Daily distance totals
# ---------------------------
df["date"] = df["timestamp"].dt.date

daily = (
    df.groupby(["animal_id", "date"])["segment_km"]
      .sum()
      .reset_index()
      .rename(columns={"segment_km": "daily_km"})
)

# ---------------------------
# 4. Flag implausible days
# ---------------------------

# Very conservative biological threshold
HARD_CAP_KM_PER_DAY = 150

stats = (
    daily.groupby("animal_id")["daily_km"]
         .agg(mean_km="mean", std_km="std")
         .reset_index()
)

daily = daily.merge(stats, on="animal_id", how="left")

# Z-score relative to each turtle's behavior
daily["zscore"] = (daily["daily_km"] - daily["mean_km"]) / daily["std_km"]

daily["flag_hard_cap"] = daily["daily_km"] > HARD_CAP_KM_PER_DAY
daily["flag_3sigma"] = daily["daily_km"] > (daily["mean_km"] + 3 * daily["std_km"])

daily["is_outlier"] = daily["flag_hard_cap"] | daily["flag_3sigma"]

# ---------------------------
# 5. Save flagged days
# ---------------------------
flagged = daily[daily["is_outlier"]].sort_values("daily_km", ascending=False)

flagged.to_csv("outputs/flagged_days.csv", index=False)

print("Flagged days (top 15):")
print(
    flagged[
        ["animal_id", "date", "daily_km", "zscore", "flag_hard_cap", "flag_3sigma"]
    ].head(15)
)

print(f"\nTotal flagged days: {len(flagged)}")
print("Saved: outputs/flagged_days.csv")

# ---------------------------
# 6. Cleaned summary (optional)
# ---------------------------
clean_daily = daily[~daily["is_outlier"]].copy()

clean_summary = (
    clean_daily.groupby("animal_id")["daily_km"]
               .agg(
                   avg_daily_km="mean",
                   max_daily_km="max",
                   total_km="sum",
                   days_tracked="count"
               )
               .reset_index()
               .sort_values("total_km", ascending=False)
)

clean_summary.to_csv("outputs/daily_summary_cleaned.csv", index=False)

print("\nCleaned summary (top 10 turtles):")
print(clean_summary.head(10))
print("Saved: outputs/daily_summary_cleaned.csv")