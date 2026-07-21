from pathlib import Path
import pandas as pd

# Locate project root
project_root = Path(__file__).resolve().parent.parent

csv_path = project_root / "data" / "enriched_places.csv"

# Read the CSV
df = pd.read_csv(csv_path)

# Convert comma-separated best_for to pipe-separated
df["best_for"] = (
    df["best_for"]
    .fillna("")
    .apply(lambda x: "|".join(
        [item.strip() for item in str(x).split(",") if item.strip()]
    ))
)

# Save the CSV back
df.to_csv(csv_path, index=False)

print("✅ best_for column converted to pipe-separated format!")
print("Saved to:", csv_path)