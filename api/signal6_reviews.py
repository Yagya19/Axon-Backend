import requests
from bs4 import BeautifulSoup
import json
import os

RESEND_API_KEY = "re_jVYQbLUF_3Fephioo2GH3gcjq9aMvFKDg"
ALERT_EMAIL = "yagyadeepsharma19@gmail.com"

def get_reviews(store_url, product_handle):
    """Get reviews from a Shopify product page."""
    url = f"{store_url}/products/{product_handle}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    review_data = {
        'count': 0,
        'rating': None,
        'snippets': []
    }
    
    # Common review selectors
    rating_selectors = [
        {'class': 'rating'},
        {'class': 'review-rating'},
        {'itemprop': 'ratingValue'},
        {'class': 'stamped-badge-caption'},
        {'class': 'jdgm-prev-badge'},
    ]
    
    for selector in rating_selectors:
        element = soup.find(attrs=selector)
        if element:
            review_data['rating'] = element.get_text(strip=True)
            break
    
    # Count review mentions
    page_text = soup.get_text()
    import re
    review_counts = re.findall(r'(\d+)\s*reviews?', page_text.lower())
    if review_counts:
        review_data['count'] = int(review_counts[0])
    
    return review_data

def check_reviews(store_url, product_handle, store_name):
    snapshot_file = f'reviews_{store_name}_{product_handle}.json'
    print(f"Checking reviews for {store_name} — {product_handle}...")
    
    new_data = get_reviews(store_url, product_handle)
    print(f"Reviews found: {new_data}")
    
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            old_data = json.load(f)
        
        changes = []
        
        if old_data['count'] != new_data['count']:
            diff = new_data['count'] - old_data['count']
            changes.append(f"Review count changed: {old_data['count']} → {new_data['count']} ({'+' if diff > 0 else ''}{diff} new reviews)")
        
        if old_data['rating'] != new_data['rating']:
            changes.append(f"Rating changed: {old_data['rating']} → {new_data['rating']}")
        
        if changes:
            print(f"REVIEW CHANGES DETECTED:")
            for change in changes:
                print(f"  → {change}")
            send_review_alert(store_url, store_name, product_handle, changes)
        else:
            print("No review changes detected")
    else:
        print(f"First scan complete — baseline saved")
    
    with open(snapshot_file, 'w') as f:
        json.dump(new_data, f)

def send_review_alert(store_url, store_name, product_handle, changes):
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
            'subject': f'⚡ AXON Review Signal — {store_name} customer sentiment changing',
            'text': f'''
AXON Customer Intelligence
--------------------------
Competitor: {store_url}
Product: {product_handle}

Changes detected:
{changes_text}

The signal reaches you first.

— AXON
            '''
        }
    )
    print(f"Alert sent — status: {response.status_code}")

check_reviews(
    'https://www.allbirds.com',
    'mens-tree-runner-nz-medium-grey',
    'allbirds'
)
