import pandas as pd

CSV_PATH = 'data/raw/Hawksbill_green turtles Chagos Archipelago Western Indian Ocean.csv'

# Try default read
df_default = pd.read_csv(CSV_PATH)
print("DEFAULT columns:", list(df_default.columns)[:20])

# Try tab-separated
df_tab = pd.read_csv(CSV_PATH, sep="\t")
print("TAB columns:", list(df_tab.columns)[:20])

# Show first row of each (helps confirm)
print("\nDEFAULT head:")
print(df_default.head(1))

print("\nTAB head:")
print(df_tab.head(1))
