import json
import requests
from bs4 import BeautifulSoup
import os

URL = "https://shop.travelerscompanyusa.com/pages/all-products"

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

response = requests.get(URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

products = {}

for link in soup.find_all("a", href=True):
    href = link["href"]

    if "/products/" not in href:
        continue

    name = link.get_text(strip=True)

    if len(name) < 5:
        continue

    full_url = f"https://shop.travelerscompanyusa.com{href}"

    products[name] = full_url

try:
    with open("known_products.json", "r") as f:
        known = set(json.load(f))
except:
    known = set()

current = set(products.keys())

new_items = current - known

for item in sorted(new_items):
    requests.post(
        WEBHOOK,
        json={
            "content":
            f"🚨 NEW TRAVELER'S COMPANY PRODUCT\n\n{item}\n{products[item]}"
        }
    )

with open("known_products.json", "w") as f:
    json.dump(sorted(current), f, indent=2)
