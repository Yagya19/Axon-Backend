import requests
from bs4 import BeautifulSoup
import hashlib

def get_page_snapshot(url):
    """Visit a competitor URL and return a snapshot of its content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract key content
        content = {
            'title': soup.title.string if soup.title else '',
            'meta_description': '',
            'body_text': soup.get_text(separator=' ', strip=True)[:5000],
            'hash': hashlib.md5(response.text.encode()).hexdigest()
        }
        
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            content['meta_description'] = meta.get('content', '')
            
        return content
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def detect_changes(old_snapshot, new_snapshot):
    """Compare two snapshots and return what changed."""
    changes = []
    
    if old_snapshot['hash'] != new_snapshot['hash']:
        if old_snapshot['title'] != new_snapshot['title']:
            changes.append({
                'type': 'title_change',
                'old': old_snapshot['title'],
                'new': new_snapshot['title'],
                'urgency': 'high'
            })
            
        if old_snapshot['meta_description'] != new_snapshot['meta_description']:
            changes.append({
                'type': 'messaging_change',
                'old': old_snapshot['meta_description'],
                'new': new_snapshot['meta_description'],
                'urgency': 'high'
            })
            
        changes.append({
            'type': 'page_change',
            'description': 'Page content changed significantly',
            'urgency': 'medium'
        })
        
    return changes
