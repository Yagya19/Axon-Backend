import requests
import json
import os

RESEND_API_KEY = "re_jVYQbLUF_3Fephioo2GH3gcjq9aMvFKDg"
ALERT_EMAIL = "yagyadeepsharma19@gmail.com"

def get_all_products(store_url):
    """Get all product handles from a Shopify store."""
    url = f"{store_url}/products.json?limit=250"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"Could not fetch products — status {response.status_code}")
        return None
    
    data = response.json()
    products = data.get('products', [])
    
    return {p['handle']: p['title'] for p in products}

def check_new_products(store_url, store_name):
    snapshot_file = f'products_{store_name}.json'
    print(f"Checking for new products at {store_url}...")
    
    new_products = get_all_products(store_url)
    
    if not new_products:
        print("Could not fetch product list")
        return
    
    print(f"Found {len(new_products)} products currently")
    
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            old_products = json.load(f)
        
        new_handles = set(new_products.keys()) - set(old_products.keys())
        
        if new_handles:
            print(f"NEW PRODUCTS DETECTED: {len(new_handles)}")
            for handle in new_handles:
                print(f"  → {new_products[handle]}")
            send_new_product_alert(store_url, store_name, new_handles, new_products)
        else:
            print("No new products detected")
    else:
        print(f"First scan complete — {len(new_products)} products saved as baseline")
    
    with open(snapshot_file, 'w') as f:
        json.dump(new_products, f)

def send_new_product_alert(store_url, store_name, new_handles, products):
    product_list = "\n".join([f"• {products[h]}" for h in new_handles])
    
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AXON <onboarding@resend.dev>',
            'to': ALERT_EMAIL,
            'subject': f'⚡ AXON Product Signal — {store_name} launched new products',
            'text': f'''
AXON New Product Signal
-----------------------
Store: {store_url}

New products detected:
{product_list}

The signal reaches you first.

— AXON
            '''
        }
    )
    print(f"Alert sent — status: {response.status_code}")

check_new_products('https://www.allbirds.com', 'allbirds')
