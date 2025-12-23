from data_utils import load_telemetry, add_segment_distances, compute_daily_distances

HARD_CAP_KM_PER_DAY = 150

df = load_telemetry()
df = add_segment_distances(df)
daily = compute_daily_distances(df)

stats = (
    daily.groupby("animal_id")["daily_km"]
         .agg(mean_km="mean", std_km="std")
         .reset_index()
)

daily = daily.merge(stats, on="animal_id", how="left")
daily["zscore"] = (daily["daily_km"] - daily["mean_km"]) / daily["std_km"]

daily["flag_hard_cap"] = daily["daily_km"] > HARD_CAP_KM_PER_DAY
daily["flag_3sigma"] = daily["daily_km"] > (daily["mean_km"] + 3 * daily["std_km"])
daily["is_outlier"] = daily["flag_hard_cap"] | daily["flag_3sigma"]

flagged = daily[daily["is_outlier"]].sort_values("daily_km", ascending=False)
flagged.to_csv("outputs/flagged_days.csv", index=False)

clean_daily = daily[~daily["is_outlier"]]

clean_summary = (
    clean_daily.groupby("animal_id")["daily_km"]
               .agg(
                   avg_daily_km="mean",
                   max_daily_km="max",
                   total_km="sum",
                   days_tracked="count",
               )
               .reset_index()
               .sort_values("total_km", ascending=False)
)

clean_summary.to_csv("outputs/daily_summary_cleaned.csv", index=False)

print("Flagged days:", len(flagged))
print(clean_summary.head(10))