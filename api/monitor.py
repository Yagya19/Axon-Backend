import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os

RESEND_API_KEY = "re_jVYQbLUF_3Fephioo2GH3gcjq9aMvFKDg"
ALERT_EMAIL = "yagyadeepsharma19@gmail.com"

def get_snapshot(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    return {
        'title': soup.title.string if soup.title else '',
        'hash': hashlib.md5(response.text.encode()).hexdigest()
    }

def send_alert(url, old_title, new_title):
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AXON <onboarding@resend.dev>',
            'to': ALERT_EMAIL,
            'subject': f'⚡ AXON Signal — Competitor change detected',
            'text': f'''
AXON Signal Detected
--------------------
Competitor: {url}

What changed:
Title changed from: {old_title}
Title changed to: {new_title}

The signal reaches you first.

— AXON
            '''
        }
    )
    print(f"Resend response: {response.status_code} — {response.text}")
    return response.status_code

def check_for_changes(url):
    snapshot_file = 'last_snapshot.json'
    new_snapshot = get_snapshot(url)

    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r') as f:
            old_snapshot = json.load(f)

        if old_snapshot['hash'] != new_snapshot['hash']:
            print(f"CHANGE DETECTED on {url}")
            status = send_alert(url, old_snapshot['title'], new_snapshot['title'])
            print(f"Alert email sent — status: {status}")
        else:
            print(f"No changes detected on {url}")
    else:
        print(f"First scan complete for {url}")

    with open(snapshot_file, 'w') as f:
        json.dump(new_snapshot, f)

check_for_changes('https://www.shopify.com')
