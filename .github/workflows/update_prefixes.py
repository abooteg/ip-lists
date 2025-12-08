import ipaddress
import json
import os
import requests
from requests.auth import HTTPBasicAuth

API_URL = os.getenv("API_URL")
API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")

CUSTOMER_ID = "4fb17593-8f67-4fb9-bb91-7d2e84d2e0e3"

UUID_WHITELIST = "204bd5b5-5f0b-4c08-be57-e562ca49e51e"
UUID_BLACKLIST = "059a2d7e-eeb4-4d1d-bc0d-db010f9773de"


def parse_file(filename):
    """Парсим CIDR из файла"""
    entries = []
    print(f"Processing file: {filename}")

    with open(filename, "r") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Комментарии и пустые строки — игнор
            if not line or line.startswith("#"):
                continue

            # Если нет маски — добавляем /32
            if "/" not in line:
                line = f"{line}/32"

            try:
                ipaddress.ip_network(line, strict=False)
                entries.append(line)
            except ValueError:
                print(f"[SKIP] Invalid entry in {filename}: {raw_line.strip()}")

    return entries


def upload(list_type, entries):
    """Формируем JSON и отправляем по API"""

    if list_type == "whitelist":
        uuid = UUID_WHITELIST
    else:
        uuid = UUID_BLACKLIST

    payload = {
        "customer": CUSTOMER_ID,
        "friendlyname": list_type,
        "prefix": entries,
        "service": "",
        "uuid": uuid
    }

    print(f"Uploading {list_type}: {len(entries)} prefixes")

    resp = requests.put(
        API_URL,
        json=payload,
        auth=HTTPBasicAuth(API_USER, API_PASS),
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

    resp.raise_for_status()


def main():
    if not API_USER or not API_PASS:
        raise SystemExit("ERROR: API_USER or API_PASS is missing")

    # WL
    if os.path.exists("wl.txt"):
        wl_entries = parse_file("wl.txt")
        upload("whitelist", wl_entries)
    else:
        print("wl.txt not found")

    # BL
    if os.path.exists("botnet.txt"):
        bl_entries = parse_file("botnet.txt")
        upload("blacklist", bl_entries)
    else:
        print("botnet.txt not found")


if __name__ == "__main__":
    main()
