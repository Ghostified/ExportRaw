import json
import logging
from datetime import datetime, timedelta
from urllib import request, parse, error
from config import ENDPOINT, API_KEY

# --- Configuration ---
api_endpoint = ENDPOINT
api_key = API_KEY
OUTPUT_FILE = "exported_tickets.json"

# Date range: Oct 6 to Oct 27, 2025 (inclusive)
START_DATE = datetime(2025, 10, 6)
END_DATE = datetime(2025, 10, 27)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ticket_export.log"),
        logging.StreamHandler()
    ]
)

def datetime_to_millis(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def make_post_request(date_start_ms: int, date_end_ms: int):
    payload = {
        "API": api_key,
        "module": "Helpdesk",
        "ticket_id": "",
        "route": "",
        "email_subject": "",
        "responsible_employee": "",
        "age": "",
        "location": "",
        "status": "",
        "source": "",
        "category": "",
        "disposition": "",
        "sub_disposition": "",
        "comments": "",
        "date_start": str(date_start_ms),
        "date_end": str(date_end_ms),
        "created_by": "",
        "assigned_to": "",
        "asset_name": ""
    }

    data = json.dumps(payload).encode('utf-8')
    req = request.Request(api_endpoint, data=data, headers={
        'Content-Type': 'application/json'
    })

    try:
        with request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except error.HTTPError as e:
        logging.error(f"HTTP error for {date_start_ms}–{date_end_ms}: {e.code} {e.reason}")
        try:
            err_body = e.read().decode()
            logging.error(f"Response: {err_body}")
        except:
            pass
        return None
    except Exception as e:
        logging.error(f"Request failed for {date_start_ms}–{date_end_ms}: {e}")
        return None

def main():
    all_tickets = []
    current = START_DATE

    while current <= END_DATE:
        start_of_day = current.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = current.replace(hour=23, minute=59, second=59, microsecond=999999)

        date_start_ms = datetime_to_millis(start_of_day)
        date_end_ms = datetime_to_millis(end_of_day)

        logging.info(f"Fetching tickets for {current.strftime('%Y-%m-%d')} ({date_start_ms} to {date_end_ms})")

        result = make_post_request(date_start_ms, date_end_ms)

        if result and isinstance(result, dict):
            # The API seems to return a single ticket object, not a list
            # But based on your example, it's one ticket per call
            all_tickets.append(result)
            logging.info(f"✅ Success: Got 1 ticket (ID: {result.get('ticket_id', 'N/A')})")
        elif result is None:
            logging.warning(f"⚠️ No data or error for {current.strftime('%Y-%m-%d')}")
        else:
            logging.warning(f"⚠️ Unexpected response format for {current.strftime('%Y-%m-%d')}")

        current += timedelta(days=1)

    # Save all results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_tickets, f, indent=2, ensure_ascii=False)

    logging.info(f"✅ Export complete! {len(all_tickets)} tickets saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()