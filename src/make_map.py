import folium
from data_utils import load_telemetry, add_segment_distances

CSV_PATH = "data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv"

MAX_SEGMENT_KM = 200   # prevents drawing teleport jumps
MAX_TURTLES = 8        # keep the UI clean; raise if you want more
DOWNSAMPLE_N = 5       # keep every Nth point per turtle (speed)

# 1) Load + compute segment distances (for jump filtering)
df = load_telemetry()
df = add_segment_distances(df)

# 2) Remove suspicious jumps so lines look realistic
df["is_jump"] = df["segment_km"] > MAX_SEGMENT_KM
df = df[~df["is_jump"]].copy()

# 3) Choose turtles to include (most points = best tracks)
top_ids = df["animal_id"].value_counts().head(MAX_TURTLES).index.tolist()
df = df[df["animal_id"].isin(top_ids)].copy()

# 4) Downsample points per turtle so map renders fast
df = df.groupby("animal_id", group_keys=False).apply(lambda g: g.iloc[::DOWNSAMPLE_N]).reset_index(drop=True)

# 5) Build the base map
center = [df["latitude"].mean(), df["longitude"].mean()]
m = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")

colors = ["red", "blue", "green", "purple", "orange", "cadetblue", "darkred", "darkblue"]

# 6) One layer per turtle (toggleable)
for i, (animal_id, g) in enumerate(df.groupby("animal_id")):
    layer = folium.FeatureGroup(name=f"Turtle {int(animal_id)}", show=(i < 3))  # first 3 visible by default

    g = g.sort_values("timestamp")
    coords = g[["latitude", "longitude"]].to_numpy().tolist()

    if len(coords) >= 2:
        folium.PolyLine(coords, color=colors[i % len(colors)], weight=3).add_to(layer)

    # Start/end markers
    folium.Marker(coords[0], tooltip=f"Start {int(animal_id)}").add_to(layer)
    folium.Marker(coords[-1], tooltip=f"End {int(animal_id)}").add_to(layer)

    layer.add_to(m)

# 7) Add toggle control
folium.LayerControl(collapsed=False).add_to(m)

m.save("outputs/migration_map.html")
print("Saved: outputs/migration_map.html")
print("Toggleable turtle layers:", [int(x) for x in top_ids])