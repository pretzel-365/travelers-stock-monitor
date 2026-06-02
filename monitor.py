import json
import os
import requests

SHOP_URL = "https://shop.travelerscompanyusa.com"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

if not WEBHOOK:
    raise Exception("DISCORD_WEBHOOK secret is missing")

STATE_FILE = "known_products.json"

KEYWORDS = [
    "olive",
    "camel",
    "factory",
    "traveler's factory",
    "tokyo",
    "brass",
    "limited",
    "love and trip",
    "airline",
    "train",
    "hotel",
    "records",
    "partner shop"
]


def send(message):
    requests.post(WEBHOOK, json={"content": message}, timeout=30)


def normalize(text):
    return text.lower().replace("'", "").replace("’", "")


def matches_keywords(title):
    title = normalize(title)
    return any(normalize(k) in title for k in KEYWORDS)


url = f"{SHOP_URL}/products.json?limit=250"

response = requests.get(url, timeout=30)
response.raise_for_status()

products = response.json()["products"]

current = {}

for product in products:
    title = product["title"]

    available = any(v["available"] for v in product["variants"])

    current[title] = {
        "available": available,
        "url": f"{SHOP_URL}/products/{product['handle']}"
    }

try:
    with open(STATE_FILE, "r") as f:
        previous = json.load(f)
except:
    previous = {}

for title in current:
    if not matches_keywords(title):
        continue

    if title not in previous:
        send(f"🚨 NEW PRODUCT\n\n{title}\n{current[title]['url']}")

for title in current:
    if not matches_keywords(title):
        continue

    if title not in previous:
        continue

    if not previous[title]["available"] and current[title]["available"]:
        send(f"✅ RESTOCK\n\n{title}\n{current[title]['url']}")

for title in previous:
    if not matches_keywords(title):
        continue

    if title not in current:
        send(f"❌ PRODUCT REMOVED\n\n{title}")

with open(STATE_FILE, "w") as f:
    json.dump(current, f, indent=2)
