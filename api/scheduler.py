import time
import os
from monitor import get_page_snapshot, detect_changes
from alerts import send_alert
from supabase import create_client

# Initialize Supabase
supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

def run_monitoring_cycle():
    """Check all tracked competitors for changes."""
    
    # Get all tracked competitors from database
    result = supabase.table('competitors').select('*').execute()
    competitors = result.data
    
    for competitor in competitors:
        url = competitor['url']
        user_email = competitor['user_email']
        last_snapshot = competitor['last_snapshot']
        
        # Get fresh snapshot
        new_snapshot = get_page_snapshot(url)
        
        if not new_snapshot:
            continue
            
        # Compare with last snapshot
        if last_snapshot:
            changes = detect_changes(last_snapshot, new_snapshot)
            
            if changes:
                send_alert(url, changes, user_email)
                print(f"Alert sent for {url} — {len(changes)} changes detected")
        
        # Update snapshot in database
        supabase.table('competitors').update({
            'last_snapshot': new_snapshot
        }).eq('id', competitor['id']).execute()
        
        print(f"Checked {url}")
        time.sleep(2)

if __name__ == '__main__':
    print("AXON monitoring started...")
    while True:
        run_monitoring_cycle()
        print("Cycle complete. Sleeping 4 hours...")
        time.sleep(14400)  # 4 hours
