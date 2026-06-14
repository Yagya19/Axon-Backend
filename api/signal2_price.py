import requests
import json
import os

RESEND_API_KEY = "re_jVYQbLUF_3Fephioo2GH3gcjq9aMvFKDg"
ALERT_EMAIL = "yagyadeepsharma19@gmail.com"

def get_shopify_price(store_url, product_handle):
    """
    Shopify exposes product data as JSON at /products/HANDLE.json
    This works on ANY Shopify store — no blocking, no JavaScript needed.
    """
    url = f"{store_url}/products/{product_handle}.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"Could not fetch product data — status {response.status_code}")
        return None
    
    data = response.json()
    product = data.get('product', {})
    variants = product.get('variants', [])
    
    if not variants:
        return None
    
    prices = {}
    for variant in variants:
        title = variant.get('title', 'Default')
        price = variant.get('price', '0')
        compare_price = variant.get('compare_at_price')
        prices[title] = {
            'price': price,
            'compare_at_price': compare_price
        }
    
    return {
        'product_title': product.get('title', ''),
        'prices': prices
    }

def check_price_change(store_url, product_handle):
    snapshot_file = f'price_{product_handle}.json'
    print(f"Checking prices for {product_handle}...")
    
    new_data = get_shopify_price(store_url, product_handle)
    
    if not new_data:
        print("Could not fetch product data")
        return
    
    print(f"Product: {new_data['product_title']}")
    for variant, info in new_data['prices'].items():
        print(f"  {variant}: ${info['price']}")
    
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            old_data = json.load(f)
        
        changes = []
        for variant, info in new_data['prices'].items():
            old_price = old_data['prices'].get(variant, {}).get('price')
            new_price = info['price']
            if old_price and old_price != new_price:
                changes.append(f"{variant}: ${old_price} → ${new_price}")
        
        if changes:
            print(f"PRICE CHANGES DETECTED:")
            for change in changes:
                print(f"  {change}")
            send_price_alert(store_url, product_handle, changes)
        else:
            print("No price changes detected")
    else:
        print("First scan complete — baseline saved")
    
    with open(snapshot_file, 'w') as f:
        json.dump(new_data, f)

def send_price_alert(store_url, product_handle, changes):
    changes_text = "\n".join(changes)
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AXON <onboarding@resend.dev>',
            'to': ALERT_EMAIL,
            'subject': f'⚡ AXON Price Signal — {product_handle} price changed',
            'text': f'''
AXON Price Signal Detected
--------------------------
Store: {store_url}
Product: {product_handle}

Price changes:
{changes_text}

The signal reaches you first.

— AXON
            '''
        }
    )
    print(f"Alert sent — status: {response.status_code}")

# Test with a real Shopify store
check_price_change(
    'https://www.allbirds.com/',
    'anytime-crew-sock-sheep'
)
