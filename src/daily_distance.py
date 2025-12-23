from data_utils import load_telemetry, add_segment_distances, compute_daily_distances

df = load_telemetry()
df = add_segment_distances(df)
daily = compute_daily_distances(df)

summary = (
    daily.groupby("animal_id")["daily_km"]
         .agg(
             avg_daily_km="mean",
             max_daily_km="max",
             total_km="sum",
             days_tracked="count",
         )
         .reset_index()
         .sort_values("total_km", ascending=False)
)

print("Daily summary (top 10):")
print(summary.head(10))

daily.to_csv("outputs/daily_distance.csv", index=False)
summary.to_csv("outputs/daily_summary.csv", index=False)