"""
03_auto_enrich.py

Automatically enriches verified_places.csv with
fields that can be derived without AI.

Input:
    verified_places.csv

Output:
    auto_enriched_places.csv

Project: Pangia
Author: Monicah Wainaina
"""

from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Locate project
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent

input_csv = project_root / "data" / "verified_places.csv"

output_csv = project_root / "data" / "auto_enriched_places.csv"

# --------------------------------------------------
# Read verified dataset
# --------------------------------------------------

df = pd.read_csv(input_csv)

print("\n" + "=" * 70)
print("PANGIA AUTO ENRICHMENT")
print("=" * 70)
print(f"Loaded {len(df)} verified places.\n")

# ==================================================
# EXPERIENCE CATEGORY
# ==================================================

CATEGORY_MAP = {

    # Accommodation
    "resort_hotel": "Resort",
    "hotel": "Resort",
    "lodging": "Staycation",
    "farmstay": "Farm Stay",

    # Dining
    "restaurant": "Dining",
    "fine_dining_restaurant": "Date Night",
    "cafe": "Cafe",
    "coffee_shop": "Cafe",
    "deli": "Dining",
    "bakery": "Cafe",

    # Nature
    "park": "Nature",
    "nature_preserve": "Nature",
    "national_park": "Wildlife",

    # Adventure
    "mountain_peak": "Adventure",
    "sports_activity_location": "Adventure",

    # Scenic
    "bridge": "Scenic",

    # Entertainment
    "bowling_alley": "Fun Activities",
    "amusement_center": "Fun Activities",

    # Shopping
    "shopping_mall": "Shopping",
    "market": "Shopping",

    # Culture
    "museum": "Culture",
    "historical_place": "Culture",

    # Wellness
    "spa": "Wellness"

}

# ==================================================
# TAG KEYWORDS
# ==================================================

TAG_KEYWORDS = {

    "Adventure": [
        "adventure",
        "zipline",
        "zip line",
        "quad",
        "horse",
        "horseback",
        "cycling",
        "bike",
        "archery"
    ],

    "Hidden Gem": [
        "hidden",
        "secret",
        "undiscovered"
    ],

    "Scenic": [
        "scenic",
        "view",
        "views",
        "panorama",
        "beautiful",
        "overlook",
        "sunset"
    ],

    "Nature": [
        "forest",
        "nature",
        "garden",
        "lake",
        "river",
        "waterfall",
        "hill"
    ],

    "Luxury": [
        "luxury",
        "premium",
        "exclusive",
        "5-star"
    ],

    "Pet Friendly": [
        "pet"
    ],

    "Kid Friendly": [
        "kids",
        "children",
        "playground",
        "family"
    ],

    "Swimming": [
        "swimming",
        "pool"
    ],

    "Camping": [
        "camp",
        "camping"
    ],

    "Hiking": [
        "hiking",
        "trail",
        "trek",
        "walk"
    ]

}

# ==================================================
# CATEGORY FUNCTION
# ==================================================

def get_category(primary_type):

    if pd.isna(primary_type):
        return "Other"

    return CATEGORY_MAP.get(primary_type, "Other")

# ==================================================
# TAG FUNCTION
# ==================================================

def get_tags(notes, primary_type):

    tags = set()

    notes = str(notes).lower()

    for tag, keywords in TAG_KEYWORDS.items():

        for keyword in keywords:

            if keyword in notes:
                tags.add(tag)

    # Google assisted tags

    if primary_type == "bridge":
        tags.add("Scenic")

    if primary_type == "nature_preserve":
        tags.add("Nature")

    if primary_type == "park":
        tags.add("Nature")

    if primary_type == "mountain_peak":
        tags.add("Adventure")
        tags.add("Hiking")
        tags.add("Scenic")

    if primary_type == "resort_hotel":
        tags.add("Luxury")

    if primary_type == "farmstay":
        tags.add("Nature")

    return "|".join(sorted(tags))
# ==================================================
# VISIT DURATION
# ==================================================

def get_visit_duration(category):

    duration_map = {

        "Nature": "2-4 Hours",
        "Adventure": "Half Day",
        "Wildlife": "Full Day",
        "Dining": "1-2 Hours",
        "Date Night": "2-3 Hours",
        "Cafe": "1-2 Hours",
        "Resort": "Full Day / Overnight",
        "Farm Stay": "Half Day / Overnight",
        "Staycation": "Overnight",
        "Fun Activities": "2-4 Hours",
        "Shopping": "2-4 Hours",
        "Culture": "2-3 Hours",
        "Scenic": "1-2 Hours",
        "Wellness": "2-4 Hours"

    }

    return duration_map.get(category, "Flexible")


# ==================================================
# TRANSPORT OPTIONS
# ==================================================

def get_transport(primary_type, notes):

    text = f"{primary_type} {notes}".lower()

    transport = ["Road"]

    if any(word in text for word in [
        "island",
        "boat",
        "lake",
        "ferry"
    ]):
        transport.append("Boat")

    if any(word in text for word in [
        "flight",
        "airstrip",
        "airport"
    ]):
        transport.append("Air")

    if any(word in text for word in [
        "railway",
        "train",
        "sgr"
    ]):
        transport.append("Rail")

    return "|".join(transport)


# ==================================================
# COUNTY EXTRACTION
# ==================================================

COUNTIES = [

    "Nairobi",
    "Kiambu",
    "Kajiado",
    "Nakuru",
    "Nyeri",
    "Laikipia",
    "Machakos",
    "Makueni",
    "Murang'a",
    "Kirinyaga",
    "Embu",
    "Meru",
    "Nyandarua",
    "Bomet",
    "Narok",
    "Kisumu",
    "Mombasa",
    "Kilifi",
    "Kwale",
    "Taita Taveta",
    "Uasin Gishu",
    "Nandi",
    "Kericho",
    "Samburu",
    "Isiolo",
    "Turkana"
]


def extract_county(address, rough_county):

    if pd.notna(address):

        address_lower = address.lower()

        for county in COUNTIES:

            if county.lower() in address_lower:
                return county

    return rough_county


# ==================================================
# AUTO ENRICHMENT
# ==================================================

auto_enriched = []

total = len(df)

for index, (_, place) in enumerate(df.iterrows(), start=1):

    progress = (index / total) * 100

    print(
        f"[{index}/{total}] "
        f"{progress:.1f}% "
        f"{place['place_name']}"
    )

    category = get_category(place["primary_type"])

    tags = get_tags(
        place["notes"],
        place["primary_type"]
    )

    duration = get_visit_duration(category)

    transport = get_transport(
        place["primary_type"],
        place["notes"]
    )

    county = extract_county(
        place["address"],
        place["rough_county"]
    )

    enriched_place = place.to_dict()

    enriched_place["verified_county"] = county

    enriched_place["experience_category"] = category

    enriched_place["tags"] = tags

    enriched_place["visit_duration"] = duration

    enriched_place["transport_options"] = transport

    auto_enriched.append(enriched_place)

# ==================================================
# EXPORT
# ==================================================

auto_df = pd.DataFrame(auto_enriched)

auto_df.to_csv(
    output_csv,
    index=False
)

print("\n" + "=" * 70)
print("AUTO ENRICHMENT COMPLETE")
print("=" * 70)

print(f"Places processed : {len(auto_df)}")

print(f"CSV exported to:\n{output_csv}")

print("\nNext step:")
print("04_ai_enrich.py")