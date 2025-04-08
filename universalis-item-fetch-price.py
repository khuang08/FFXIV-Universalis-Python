import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Config
ITEMS = {
    45984: "Hydrophobic Preservative",
    45985: "Shaaloani Coke",
    45986: "Neo abrasive",
    45987: "Cronopio skin",
    45988: "Diatryma Pelt"
}

WORLDS = [
    "Adamantoise", "Cactuar", "Faerie", "Gilgamesh", "Jenova", "Midgardsormr", "Sargatanas", "Siren",
    "Behemoth", "Excalibur", "Exodus", "Famfrit", "Hyperion", "Lamia", "Leviathan", "Ultros",
    "Balmung", "Brynhildr", "Coeurl", "Diabolos", "Goblin", "Malboro", "Mateus", "Zalera"
]

THREADS = 15
DELAY = 1.0 / 15  # ~0.066s delay (15 RPS)
last_request_time = 0

def rate_limited_get(url):
    """Ensure we respect the delay between requests"""
    global last_request_time
    elapsed = time.time() - last_request_time
    if elapsed < DELAY:
        time.sleep(DELAY - elapsed)
    last_request_time = time.time()
    return requests.get(url)

def fetch_world_prices(world, item_ids):
    """Fetch prices for a batch of items in one world"""
    item_str = ",".join(map(str, item_ids))
    url = f"https://universalis.app/api/v2/{world}/{item_str}?listings=1"
    try:
        response = rate_limited_get(url)
        return world, response.json()
    except Exception as e:
        print(f"Error fetching {world}: {e}")
        return world, None

def process_results(all_results):
    """Print the cheapest prices for each item"""
    print("\n=== Cheapest Prices in North America ===")
    for item_id, item_name in ITEMS.items():
        if item_id in all_results and all_results[item_id]["world"]:
            data = all_results[item_id]
            print(f"{item_name} (ID: {item_id}): {data['price']} gil on {data['world']}")
        else:
            print(f"{item_name} (ID: {item_id}): No listings found")

def main():
    all_results = {}
    item_ids = list(ITEMS.keys())
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        for world in WORLDS:
            # Split items into batches of 5 to avoid long URLs
            for i in range(0, len(item_ids), 5):
                batch = item_ids[i:i + 5]
                futures.append(executor.submit(fetch_world_prices, world, batch))

        for future in as_completed(futures):
            world, data = future.result()
            if data and "items" in data:
                for item_id_str, item_data in data["items"].items():
                    item_id = int(item_id_str)
                    listings = item_data.get("listings", [])
                    if listings:
                        price = listings[0]["pricePerUnit"]
                        # Update if cheaper than current record
                        if item_id not in all_results or price < all_results[item_id]["price"]:
                            all_results[item_id] = {
                                "world": data.get("worldName", world),
                                "price": price
                            }
    
    process_results(all_results)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"\nCompleted in {time.time() - start_time:.2f} seconds")