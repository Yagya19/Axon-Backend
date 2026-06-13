# AXON Backend

Competitor monitoring engine for AXON intelligence platform.

## What it does
- Monitors competitor websites for changes
- Detects pricing, messaging, and content changes
- Sends email alerts when changes are detected
- Runs every 4 hours automatically

## Stack
- Python
- Supabase (database)
- Resend (email alerts)

## Files
- `api/monitor.py` — scrapes competitor pages and detects changes
- `api/alerts.py` — sends email alerts via Resend
- `api/scheduler.py` — runs monitoring cycle every 4 hours
- `requirements.txt` — Python dependencies

## Environment Variables needed
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `RESEND_API_KEY`
