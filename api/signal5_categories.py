import requests
import json
import os

RESEND_API_KEY = "re_jVYQbLUF_3Fephioo2GH3gcjq9aMvFKDg"
ALERT_EMAIL = "yagyadeepsharma19@gmail.com"

def get_categories(store_url):
    """Get all product categories from a Shopify store."""
    url = f"{store_url}/collections.json?limit=250"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"Could not fetch collections — status {response.status_code}")
        return None
    
    data = response.json()
    collections = data.get('collections', [])
    
    return {c['handle']: c['title'] for c in collections}

def check_categories(store_url, store_name):
    snapshot_file = f'categories_{store_name}.json'
    print(f"Checking categories for {store_name}...")
    
    new_categories = get_categories(store_url)
    
    if not new_categories:
        print("Could not fetch categories")
        return
    
    print(f"Found {len(new_categories)} categories")
    for handle, title in new_categories.items():
        print(f"  • {title}")
    
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            old_categories = json.load(f)
        
        new_handles = set(new_categories.keys()) - set(old_categories.keys())
        removed_handles = set(old_categories.keys()) - set(new_categories.keys())
        
        if new_handles:
            print(f"NEW CATEGORIES DETECTED: {len(new_handles)}")
            for handle in new_handles:
                print(f"  → {new_categories[handle]}")
            send_category_alert(store_url, store_name, new_handles, new_categories, 'added')
        elif removed_handles:
            print(f"CATEGORIES REMOVED: {len(removed_handles)}")
            for handle in removed_handles:
                print(f"  → {old_categories[handle]}")
        else:
            print("No category changes detected")
    else:
        print(f"First scan complete — {len(new_categories)} categories saved as baseline")
    
    with open(snapshot_file, 'w') as f:
        json.dump(new_categories, f)

def send_category_alert(store_url, store_name, handles, categories, change_type):
    category_list = "\n".join([f"• {categories[h]}" for h in handles])
    
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AXON <onboarding@resend.dev>',
            'to': ALERT_EMAIL,
            'subject': f'⚡ AXON Category Signal — {store_name} expanding into new territory',
            'text': f'''
AXON Category Intelligence
--------------------------
Competitor: {store_url}

New categories detected:
{category_list}

This tells you where your competitor is betting their future.

The signal reaches you first.

— AXON
            '''
        }
    )
    print(f"Alert sent — status: {response.status_code}")

check_categories('https://www.allbirds.com', 'allbirds')
