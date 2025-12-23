import pandas as pd
from distance import haversine_km

CSV_PATH = "data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv"

def load_telemetry():
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
    df = df.sort_values(["animal_id", "timestamp"]).copy()

    return df

def add_segment_distances(df):
    df = df.copy()
    df["prev_lat"] = df.groupby("animal_id")["latitude"].shift(1)
    df["prev_lon"] = df.groupby("animal_id")["longitude"].shift(1)

    df["segment_km"] = haversine_km(
        df["prev_lat"],
        df["prev_lon"],
        df["latitude"],
        df["longitude"],
    ).fillna(0.0)

    return df

def compute_daily_distances(df):
    df = df.copy()
    df["date"] = df["timestamp"].dt.date

    daily = (
        df.groupby(["animal_id", "date"])["segment_km"]
          .sum()
          .reset_index()
          .rename(columns={"segment_km": "daily_km"})
    )
    return daily