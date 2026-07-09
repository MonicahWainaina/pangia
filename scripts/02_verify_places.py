"""
02_verify_places.py

Verifies places from master_places.csv using
Google Places API (New) and exports
verified_places.csv.

Project: Pangia
Author: Monicah Wainaina
"""

from pathlib import Path
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# --------------------------------------------------
# Locate project root
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Read master dataset
# --------------------------------------------------

master_csv = project_root / "data" / "master_places.csv"

df = pd.read_csv(master_csv)

print("\n" + "=" * 70)
print("PANGIA PLACE VERIFICATION")
print("=" * 70)
print(f"Loaded {len(df)} places.\n")

# --------------------------------------------------
# Output CSV
# --------------------------------------------------

output_path = project_root / "data" / "verified_places.csv"

# --------------------------------------------------
# Google Places API
# --------------------------------------------------

url = "https://places.googleapis.com/v1/places:searchText"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": (
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.rating,"
        "places.userRatingCount,"
        "places.id,"
        "places.primaryType,"
        "places.photos"
    )
}

# --------------------------------------------------
# Storage
# --------------------------------------------------

verified_places = []

stats = {
    "VERIFIED": 0,
    "NOT_FOUND": 0,
    "API_ERROR": 0,
    "REVIEW_REQUIRED": 0
}

# --------------------------------------------------
# Verify ALL places
# --------------------------------------------------

places_to_process = df

total_to_process = len(places_to_process)

for index, (_, place) in enumerate(
    places_to_process.iterrows(),
    start=1
):

    progress = (index / total_to_process) * 100

    print("\n" + "=" * 70)
    print(
        f"[{index}/{total_to_process}] "
        f"({progress:.1f}%)"
    )

    search_text = f"{place['place_name']} Kenya"

    print(f"Searching: {search_text}")

    payload = {
        "textQuery": search_text
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    # --------------------------------------------------
    # API Error
    # --------------------------------------------------

    if response.status_code != 200:

        print(f"❌ API Error ({response.status_code})")

        verified_places.append({

            "original_name": place["place_name"],
            "source_link": place["source_link"],
            "rough_county": place["rough_county"],
            "verified_county": None,
            "notes": place["notes"],

            "place_name": None,
            "address": None,
            "latitude": None,
            "longitude": None,
            "rating": None,
            "user_ratings_total": None,
            "place_id": None,
            "primary_type": None,
            "photo_name": None,

            "verification_status": "API_ERROR"

        })

        stats["API_ERROR"] += 1

        continue

    data = response.json()

    # --------------------------------------------------
    # Nothing returned
    # --------------------------------------------------

    if "places" not in data or len(data["places"]) == 0:

        print("❌ No place found")

        verified_places.append({

            "original_name": place["place_name"],
            "source_link": place["source_link"],
            "rough_county": place["rough_county"],
            "verified_county": None,
            "notes": place["notes"],

            "place_name": None,
            "address": None,
            "latitude": None,
            "longitude": None,
            "rating": None,
            "user_ratings_total": None,
            "place_id": None,
            "primary_type": None,
            "photo_name": None,

            "verification_status": "NOT_FOUND"

        })

        stats["NOT_FOUND"] += 1

        continue

    # --------------------------------------------------
    # Google Match
    # --------------------------------------------------

    google_place = data["places"][0]

    photos = google_place.get("photos", [])

    verified_place = {

        # Original Research
        "original_name": place["place_name"],
        "source_link": place["source_link"],
        "rough_county": place["rough_county"],

        # Filled later
        "verified_county": None,

        "notes": place["notes"],

        # Google Data
        "place_name":
            google_place.get(
                "displayName",
                {}
            ).get("text"),

        "address":
            google_place.get(
                "formattedAddress"
            ),

        "latitude":
            google_place.get(
                "location",
                {}
            ).get("latitude"),

        "longitude":
            google_place.get(
                "location",
                {}
            ).get("longitude"),

        "rating":
            google_place.get("rating"),

        "user_ratings_total":
            google_place.get(
                "userRatingCount"
            ),

        "place_id":
            google_place.get("id"),

        "primary_type":
            google_place.get(
                "primaryType"
            ),

        "photo_name":
            photos[0]["name"]
            if photos else None,

        "verification_status":
            "VERIFIED"

    }

    verified_places.append(verified_place)

    stats["VERIFIED"] += 1

    print("✅ VERIFIED")

    # --------------------------------------------------
    # Save progress every 10 records
    # --------------------------------------------------

    if index % 10 == 0:

        verified_df = pd.DataFrame(verified_places)

        verified_df.to_csv(
            output_path,
            index=False
        )

        print(f"💾 Progress saved ({index}/{total_to_process})")

    # --------------------------------------------------
    # Be nice to the API
    # --------------------------------------------------

    time.sleep(0.5)

# --------------------------------------------------
# Final Save
# --------------------------------------------------

verified_df = pd.DataFrame(verified_places)

verified_df.to_csv(
    output_path,
    index=False
)

# --------------------------------------------------
# Final Summary
# --------------------------------------------------

print("\n")
print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

print(f"Total Places:       {total_to_process}")
print(f"Verified:           {stats['VERIFIED']}")
print(f"Not Found:          {stats['NOT_FOUND']}")
print(f"API Errors:         {stats['API_ERROR']}")
print(f"Review Required:    {stats['REVIEW_REQUIRED']}")

print("-" * 70)

success_rate = (
    (stats["VERIFIED"] / total_to_process) * 100
    if total_to_process > 0 else 0
)

print(f"Success Rate:       {success_rate:.1f}%")

print("-" * 70)

print(f"\nCSV exported successfully:")
print(output_path)

print("\n🎉 Pangia verification pipeline finished successfully.")