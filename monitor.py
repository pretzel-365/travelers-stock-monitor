import json
import os
import requests

SHOP_URL = "https://shop.travelerscompanyusa.com"

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

STATE_FILE = "known_products.json"


def send(msg):
    requests.post(
        WEBHOOK,
        json={"content": msg},
        timeout=30
    )


# Shopify product feed
url = f"{SHOP_URL}/products.json?limit=250"

r = requests.get(url, timeout=30)
r.raise_for_status()

products = r.json()["products"]

current = {}

for product in products:

    title = product["title"]

    available = any(
        variant["available"]
        for variant in product["variants"]
    )

    current[title] = {
        "available": available,
        "url": f"{SHOP_URL}/products/{product['handle']}"
    }

try:
    with open(STATE_FILE, "r") as f:
        previous = json.load(f)
except:
    previous = {}

# NEW PRODUCTS

for title in current:

    if title not in previous:

        send(
            f"🚨 **NEW PRODUCT**\n\n"
            f"{title}\n"
            f"{current[title]['url']}"
        )

# RESTOCKS

for title in current:

    if title not in previous:
        continue

    was_available = previous[title]["available"]
    now_available = current[title]["available"]

    if not was_available and now_available:

        send(
            f"✅ **RESTOCK**\n\n"
            f"{title}\n"
            f"{current[title]['url']}"
        )

# REMOVED PRODUCTS

for title in previous:

    if title not in current:

        send(
            f"❌ **PRODUCT REMOVED**\n\n"
            f"{title}"
        )

with open(STATE_FILE, "w") as f:
    json.dump(current, f, indent=2)
