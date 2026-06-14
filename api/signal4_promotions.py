import requests
from bs4 import BeautifulSoup
import json
import os
import re

RESEND_API_KEY = "re_jVYQbLUF_3Fephioo2GH3gcjq9aMvFKDg"
ALERT_EMAIL = "yagyadeepsharma19@gmail.com"

def get_promotions(store_url):
    """Detect promotions, discounts and offers on a Shopify store."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    promotions = []
    
    # Check homepage for promotional banners
    try:
        response = requests.get(store_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for discount patterns in page text
        page_text = soup.get_text(separator=' ', strip=True)
        
        patterns = [
            r'\d+%\s*off',
            r'buy\s*\d+\s*get\s*\d+',
            r'free\s*shipping',
            r'save\s*\$?\d+',
            r'sale',
            r'discount',
            r'promo',
            r'limited\s*time',
            r'special\s*offer',
            r'coupon',
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, page_text.lower())
            if matches:
                found.extend(matches)
        
        if found:
            promotions.extend(list(set(found)))
            
    except Exception as e:
        print(f"Error checking homepage: {e}")
    
    # Check Shopify discounts endpoint
    try:
        discount_url = f"{store_url}/discount"
        response = requests.get(discount_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            if len(text) > 100:
                promotions.append('active_discount_page')
    except:
        pass
    
    return list(set(promotions))

def check_promotions(store_url, store_name):
    snapshot_file = f'promos_{store_name}.json'
    print(f"Checking promotions for {store_name}...")
    
    new_promos = get_promotions(store_url)
    
    if not new_promos:
        print("No promotions detected")
    else:
        print(f"Promotions found: {new_promos}")
    
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            old_promos = json.load(f)
        
        new_items = set(new_promos) - set(old_promos)
        removed_items = set(old_promos) - set(new_promos)
        
        if new_items:
            print(f"NEW PROMOTIONS DETECTED: {new_items}")
            send_promo_alert(store_url, store_name, list(new_items))
        elif removed_items:
            print(f"Promotions ended: {removed_items}")
        else:
            print("No promotion changes detected")
    else:
        print(f"First scan complete — baseline saved")
    
    with open(snapshot_file, 'w') as f:
        json.dump(new_promos, f)

def send_promo_alert(store_url, store_name, new_promos):
    promo_list = "\n".join([f"• {p}" for p in new_promos])
    
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AXON <onboarding@resend.dev>',
            'to': ALERT_EMAIL,
            'subject': f'⚡ AXON Promotion Signal — {store_name} running new offers',
            'text': f'''
AXON Promotion Signal
---------------------
Competitor: {store_url}

New promotions detected:
{promo_list}

The signal reaches you first.

— AXON
            '''
        }
    )
    print(f"Alert sent — status: {response.status_code}")

check_promotions('https://www.allbirds.com', 'allbirds')
