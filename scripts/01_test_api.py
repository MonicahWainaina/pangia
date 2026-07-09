from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

place_name = "Ngong Hills Kenya"

payload = {
    "textQuery": place_name
}

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": api_key,
    "X-Goog-FieldMask": (
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.rating,"
        "places.id,"
        "places.primaryType"
    )
}

response = requests.post(
    "https://places.googleapis.com/v1/places:searchText",
    headers=headers,
    json=payload
)

print(response.status_code)
print(response.text)