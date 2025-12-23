import folium
from data_utils import load_telemetry, add_segment_distances

MAX_SEGMENT_KM = 200

df = load_telemetry()
df = add_segment_distances(df)

df["is_jump"] = df["segment_km"] > MAX_SEGMENT_KM
df = df[~df["is_jump"]]

top_ids = df["animal_id"].value_counts().head(5).index.tolist()
df = df[df["animal_id"].isin(top_ids)]

center = [df["latitude"].mean(), df["longitude"].mean()]
m = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")

colors = ["red", "blue", "green", "purple", "orange"]

for (animal_id, g), color in zip(df.groupby("animal_id"), colors):
    coords = g.sort_values("timestamp")[["latitude", "longitude"]].values.tolist()
    folium.PolyLine(coords, color=color, weight=3, tooltip=f"{animal_id}").add_to(m)

m.save("outputs/migration_map.html")
print("Saved outputs/migration_map.html")