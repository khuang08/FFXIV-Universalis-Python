import requests
import json
import time
import csv
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Configuration
WORLDS = [
    "Adamantoise", "Cactuar", "Faerie", "Gilgamesh", "Jenova", "Midgardsormr", "Sargatanas", "Siren",
    "Behemoth", "Excalibur", "Exodus", "Famfrit", "Hyperion", "Lamia", "Leviathan", "Ultros",
    "Balmung", "Brynhildr", "Coeurl", "Diabolos", "Goblin", "Malboro", "Mateus", "Zalera"
]

PRIORITY_WORLDS = [
    "Brynhildr", "Balmung", "Coeurl", "Diabolos", "Goblin", "Malboro", "Mateus", "Zalera"
]

DELAY_BETWEEN_REQUESTS = 1/15
MAX_OUTPUT_LINES = 1000
ENTRIES_PER_WORLD = 200
OUTPUT_CSV = "frequently_updated_items.csv"

def load_item_database():
    """Load the local item database JSON file"""
    items_json_path = Path(__file__).parent / "items.json"
    try:
        with open(items_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: items.json not found in the script's directory.")
        exit(1)

def fetch_world_data(world):
    """Fetch data for a single world with error handling"""
    try:
        url = f"https://universalis.app/api/v2/extra/stats/most-recently-updated?dcName={world}&entries={ENTRIES_PER_WORLD}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch data for {world}. Error: {e}")
        return None

def process_world_data(world_data, items_db, results):
    """Process data from a single world and merge into results"""
    if not world_data or "items" not in world_data:
        return
        
    for item in world_data["items"]:
        item_id = str(item["itemID"])
        if item_id in items_db:
            item_name = items_db[item_id].get("en", f"Unknown (ID: {item_id})")
            results[item_name]["count"] += 1
            results[item_name]["worlds"].add(world_data["world"])
            # Keep the most recent timestamp
            if item["lastUploadTime"] > results[item_name]["last_updated"]:
                results[item_name]["last_updated"] = item["lastUploadTime"]

def format_timestamp(timestamp_ms):
    """Format timestamp as 'YYYY-MM-DD HH:MM AM/PM'"""
    if timestamp_ms == 0:
        return "Unknown"
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime("%Y-%m-%d %I:%M %p")

def format_worlds_list(worlds_set, priority_worlds):
    """Format worlds list with priority worlds first"""
    priority = [w for w in priority_worlds if w in worlds_set]
    non_priority = [w for w in worlds_set if w not in priority_worlds]
    return ", ".join(priority + non_priority)

def generate_output(all_items, max_lines, priority_worlds):
    """Generate both console and CSV output"""
    sorted_items = sorted(
        all_items.items(),
        key=lambda x: (-x[1]["count"], x[0])
    )

    output_data = []
    for item_name, data in sorted_items[:max_lines]:
        output_data.append({
            "Item Name": item_name,
            "Count": data["count"],
            "Last Updated": format_timestamp(data["last_updated"]),
            "Worlds": format_worlds_list(data["worlds"], priority_worlds)
        })
    return output_data

def write_csv(output_data, filename):
    """Write data to CSV file with custom header"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, 
                              fieldnames=["Item Name", "Count", "Last Updated", "Worlds"])
        writer.writeheader()
        writer.writerows(output_data)

def print_console_output(output_data):
    """Print formatted output to console"""
    print("\nTop 1000 frequently updated items across all worlds:")
    print("Item Name, Count, Last Updated, Worlds")
    for item in output_data:
        print(f"{item['Item Name']}, {item['Count']}, {item['Last Updated']}, {item['Worlds']}")

def main():
    print("Starting data collection...")
    items_db = load_item_database()
    print(f"Successfully loaded items database with {len(items_db)} entries.")

    all_items = defaultdict(lambda: {
        "count": 0,
        "worlds": set(),
        "last_updated": 0
    })

    for i, world in enumerate(WORLDS):
        if i > 0:
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        print(f"Processing {world} ({i+1}/{len(WORLDS)})...", end="\r")
        world_data = fetch_world_data(world)
        if world_data:
            world_data["world"] = world
            process_world_data(world_data, items_db, all_items)

    print("\nData collection complete. Preparing results...")
    output_data = generate_output(all_items, MAX_OUTPUT_LINES, PRIORITY_WORLDS)
    
    write_csv(output_data, OUTPUT_CSV)
    print(f"Results saved to {OUTPUT_CSV}")
    
    print_console_output(output_data)

if __name__ == "__main__":
    main()