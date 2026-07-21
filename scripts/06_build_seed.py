"""
06_build_seed.py

Builds the final production-ready Pangia dataset
from enriched_places.csv.

Input:
    data/enriched_places.csv

Output:
    data/pangia_places_seed.csv

Project: Pangia
Author: Monicah Wambui
"""

from pathlib import Path
import pandas as pd
import re

# --------------------------------------------------
# Locate project root
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

input_csv = project_root / "data" / "enriched_places.csv"

output_csv = project_root / "data" / "pangia_places_seed.csv"

# --------------------------------------------------
# Read enriched dataset
# --------------------------------------------------

df = pd.read_csv(input_csv)

print("\n" + "=" * 70)
print("BUILDING PANGIA SEED DATASET")
print("=" * 70)
print(f"Loaded {len(df)} enriched places.\n")

# --------------------------------------------------
# Create slug from place name
# --------------------------------------------------

def create_slug(place_name):
    """
    Convert place name into a URL-friendly slug.
    Example:
    "Sironka Valley Resort"
    -> "sironka-valley-resort"
    """

    if pd.isna(place_name):
        return ""

    slug = str(place_name).lower()

    # Remove apostrophes
    slug = slug.replace("'", "")

    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug

# Add slug column
df["slug"] = df["place_name"].apply(create_slug)

# --------------------------------------------------
# Rename columns for final frontend schema
# --------------------------------------------------

df = df.rename(columns={
    "verified_county": "county",
    "notes": "description"
})

# --------------------------------------------------
# Select final columns for Pangia MVP
# --------------------------------------------------

final_columns = [

    # Core identity
    "slug",
    "place_name",
    "county",
    "address",

    # Coordinates
    "latitude",
    "longitude",

    # Pangia experience data
    "experience_category",
    "tags",
    "best_for",
    "visit_duration",
    "transport_options",
    "best_time_to_visit",

    # Pricing
    "budget_level",
    "typical_spend_pp",

    # Ratings and media
    "rating",
    "user_ratings_total",
    "photo_name",

    # Content
    "description",

    # Google reference
    "place_id"
]

# Keep only columns that exist
existing_columns = [
    column for column in final_columns
    if column in df.columns
]

seed_df = df[existing_columns]

# --------------------------------------------------
# Export final seed dataset
# --------------------------------------------------

seed_df.to_csv(output_csv, index=False)

# --------------------------------------------------
# Final summary
# --------------------------------------------------

print("\n" + "=" * 70)
print("PANGIA SEED DATASET COMPLETE")
print("=" * 70)

print(f"Total places exported: {len(seed_df)}")
print(f"Total columns: {len(seed_df.columns)}")

print("\nFinal columns:")
for column in seed_df.columns:
    print(f"  - {column}")

print("\n" + "-" * 70)
print(f"CSV exported successfully:\n{output_csv}")
print("-" * 70)

print("\n🎉 Pangia production seed file is ready!")