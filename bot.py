import os
import time
import requests
import re

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PAGE_URL = "https://public.tiketa.eus/gaztelugatxe/?lang=en"
ENDPOINT = "https://public.tiketa.eus/gaztelugatxe/wp-admin/admin-ajax.php"

TARGET_DATES = {"2026-08-29", "2026-08-30"}

session = requests.Session()

def check_slots():
    page = session.get(PAGE_URL, timeout=30)
    page.raise_for_status()

    match = re.search(r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)', page.text)

    if not match:
        raise Exception("Could not find CSRF token")

    csrf = match.group(1)

    params = {
        "lang": "en",
        "action": "bookly_render_time",
        "form_id": "6a82d5558bbe0",
        "csrf_token": csrf,
    }

    response = session.get(ENDPOINT, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    found = []

    for date in TARGET_DATES:
        slots = data.get("slots_data", {}).get(date, {}).get("slots", [])
        if slots:
            found.append((date, slots))

    return found


found = check_slots()

if found:
    message = "🚨 GAZTELUGATXE SLOTS FOUND!\n\n"

    for date, slots in found:
        message += f"{date}: {slots}\n"

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=30,
    )

    print(message)
else:
    print("No slots for Aug 29–30.")
