import requests
import os

def send_alert(competitor_url, changes, user_email):
    """Send email alert when competitor changes are detected."""
    
    if not changes:
        return
    
    # Build email content
    change_list = ""
    for change in changes:
        if change['type'] == 'title_change':
            change_list += f"• Homepage title changed\n  From: {change['old']}\n  To: {change['new']}\n\n"
        elif change['type'] == 'messaging_change':
            change_list += f"• Messaging changed\n  From: {change['old']}\n  To: {change['new']}\n\n"
        elif change['type'] == 'page_change':
            change_list += f"• Page content updated significantly\n\n"
    
    email_body = f"""
AXON Signal Detected
--------------------
Competitor: {competitor_url}

What changed:
{change_list}

The signal reaches you first.

— AXON
    """
    
    # Send via Resend
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f"Bearer {os.environ.get('RESEND_API_KEY')}",
            'Content-Type': 'application/json'
        },
        json={
            'from': 'AXON <alerts@yourdomain.com>',
            'to': user_email,
            'subject': f'⚡ Competitor signal detected — {competitor_url}',
            'text': email_body
        }
    )
    
    return response.status_code == 200
