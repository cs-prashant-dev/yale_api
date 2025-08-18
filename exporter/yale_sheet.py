
import requests
import pandas as pd
import os
from django.conf import settings

BASE_URL = 'https://api.august.com'
AUGUST_API_KEY = '9b4c5068-34c5-43af-90e8-d9a31c04565b'
AUGUST_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDgwMDI5NzgsImV4cCI6MTc1ODM3MDk3OCwiZXhwaXJlc0F0IjoiMjAyNS0wOS0yMFQxMjoyMjo1OC44OTVaIiwiaW5zdGFsbElkIjoiIiwicmVnaW9uIjoiIiwiYXBwbGljYXRpb25JZCI6IiIsInVzZXJJZCI6IjE3ZmIxZGFjLTZkMWItNDY5MC1iZWU0LTZmMzcwMWUzOTg1NSIsInZJbnN0YWxsSWQiOmZhbHNlLCJ2UGFzc3dvcmQiOnRydWUsInZFbWFpbCI6dHJ1ZSwidlBob25lIjp0cnVlLCJoYXNJbnN0YWxsSWQiOmZhbHNlLCJoYXNQYXNzd29yZCI6ZmFsc2UsImhhc0VtYWlsIjpmYWxzZSwiaGFzUGhvbmUiOmZhbHNlLCJpc0xvY2tlZE91dCI6ZmFsc2UsImNhcHRjaGEiOiIiLCJlbWFpbCI6W10sInBob25lIjpbXSwidGVtcG9yYXJ5QWNjb3VudENyZWF0aW9uUGFzc3dvcmRMaW5rIjoiIiwiaGFzQXBwbGVVc2VySUQiOmZhbHNlLCJ2QXBwbGVVc2VySUQiOmZhbHNlLCJvYXV0aCI6eyJhcHBfbmFtZSI6IklvVCBDb250cm9sbGVyIEFTU0EiLCJjbGllbnRfaWQiOiI1NTJmMmMyNi01MjQ4LTRjMTctODc2NS05YTM3ZmM5YTBjNDciLCJyZWRpcmVjdF91cmkiOiJodHRwczovL2V4YW1wbGUuY29tL2NhbGxiYWNrIiwicGFydG5lcl9pZCI6IjY0YmQzNzVlMzJjYTk0MDAxNDYyNzlkYyJ9fQ.4NnOd3Qu_-z2-a0LFT-PGQMYSCbCdfbHz_IsMKIoJDg'

import requests

def getLocksDetails():
    url = f"{BASE_URL}/users/locks/mine"
    headers = {
        'x-august-api-key': AUGUST_API_KEY,
        'x-august-access-token': AUGUST_ACCESS_TOKEN
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching locks: {e}")
        return []

    locks_data = response.json()
    result = []

    for lock_id, lock_info in locks_data.items():
        lock_details = {
            "lock_id": lock_id,
            "lock_name": lock_info.get("LockName", ""),
            "user_type": lock_info.get("UserType", ""),
            "mac_address": lock_info.get("macAddress", ""),
            "house_id": lock_info.get("HouseID", ""),
            "house_name": lock_info.get("HouseName", ""),
            "status": "",
            "door_status": "",
            "battery_status": None
        }

        try:
            # Fetch lock status
            status_url = f"{BASE_URL}/locks/{lock_id}/status"
            status_response = requests.get(status_url, headers=headers, timeout=10)
            if status_response.status_code == 200:
                status_json = status_response.json()
                lock_details["status"] = status_json.get("status", "")
                lock_details["door_status"] = status_json.get("doorState", "")
            else:
                lock_details["status"] = f"Error {status_response.status_code}: {status_response.text}"

            # Fetch lock info (battery, etc.)
            info_url = f"{BASE_URL}/locks/{lock_id}"
            info_response = requests.get(info_url, headers=headers, timeout=10)
            if info_response.status_code == 200:
                info_json = info_response.json()
                battery_status = None
                if isinstance(info_json, dict) and "battery" in info_json:
                    battery_value = info_json["battery"]
                    battery_status = float(battery_value) * 100 if battery_value <= 1 else float(battery_value)
                elif isinstance(info_json, list) and len(info_json) > 0 and "battery" in info_json[0]:
                    battery_value = info_json[0]["battery"]
                    battery_status = float(battery_value) * 100 if battery_value <= 1 else float(battery_value)
                lock_details["battery_status"] = battery_status
        except requests.RequestException as e:
            lock_details["status"] = f"error_fetching_status: {e}"

        result.append(lock_details)

    return result


def getYaleData():
    lock_details = getLocksDetails()
    if lock_details:
        file_path = export_to_excel(lock_details)
        print(f"Data exported successfully to {file_path}")
        return file_path
    else:
        print("No lock data found or API error.")
        return None

def export_to_excel(data, file_name='locks_details.xlsx'):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    OUTPUT_FILE = f"yale_devices_{timestamp}.xlsx"
    df = pd.DataFrame(data)
    file_path = os.path.join(settings.BASE_DIR, 'exports', OUTPUT_FILE)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_excel(file_path, index=False)
    return file_path