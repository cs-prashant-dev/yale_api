
import requests
import pandas as pd
import os
from django.conf import settings

BASE_URL = 'https://api.august.com'
AUGUST_API_KEY = '9b4c5068-34c5-43af-90e8-d9a31c04565b'
AUGUST_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDgwMDI5NzgsImV4cCI6MTc1ODM3MDk3OCwiZXhwaXJlc0F0IjoiMjAyNS0wOS0yMFQxMjoyMjo1OC44OTVaIiwiaW5zdGFsbElkIjoiIiwicmVnaW9uIjoiIiwiYXBwbGljYXRpb25JZCI6IiIsInVzZXJJZCI6IjE3ZmIxZGFjLTZkMWItNDY5MC1iZWU0LTZmMzcwMWUzOTg1NSIsInZJbnN0YWxsSWQiOmZhbHNlLCJ2UGFzc3dvcmQiOnRydWUsInZFbWFpbCI6dHJ1ZSwidlBob25lIjp0cnVlLCJoYXNJbnN0YWxsSWQiOmZhbHNlLCJoYXNQYXNzd29yZCI6ZmFsc2UsImhhc0VtYWlsIjpmYWxzZSwiaGFzUGhvbmUiOmZhbHNlLCJpc0xvY2tlZE91dCI6ZmFsc2UsImNhcHRjaGEiOiIiLCJlbWFpbCI6W10sInBob25lIjpbXSwidGVtcG9yYXJ5QWNjb3VudENyZWF0aW9uUGFzc3dvcmRMaW5rIjoiIiwiaGFzQXBwbGVVc2VySUQiOmZhbHNlLCJ2QXBwbGVVc2VySUQiOmZhbHNlLCJvYXV0aCI6eyJhcHBfbmFtZSI6IklvVCBDb250cm9sbGVyIEFTU0EiLCJjbGllbnRfaWQiOiI1NTJmMmMyNi01MjQ4LTRjMTctODc2NS05YTM3ZmM5YTBjNDciLCJyZWRpcmVjdF91cmkiOiJodHRwczovL2V4YW1wbGUuY29tL2NhbGxiYWNrIiwicGFydG5lcl9pZCI6IjY0YmQzNzVlMzJjYTk0MDAxNDYyNzlkYyJ9fQ.4NnOd3Qu_-z2-a0LFT-PGQMYSCbCdfbHz_IsMKIoJDg'

def getLocksDetails():
    url = f"{BASE_URL}/users/locks/mine"
    headers = {
        'x-august-api-key': AUGUST_API_KEY,
        'x-august-access-token': AUGUST_ACCESS_TOKEN
    }

    response = requests.request("GET", url, headers=headers)
    if (response.status_code != 200):
        return []

    locks = []

    for lock_id, lock_info in response.json().items():
        lock = {
            'LockID': lock_id,
            'LockName': lock_info['LockName'],
            'UserType': lock_info['UserType'],
            'macAddress': lock_info['macAddress'],
            'HouseID': lock_info['HouseID'],
            'HouseName': lock_info['HouseName'],
        }
        locks.append(lock)

    result = []
    for lock in locks:
        try:
            lock_id = lock.get("LockID")
            url = f"{BASE_URL}/locks/{lock_id}/status"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                lock_status = json_data.get("status", "")
                door_status = json_data.get("doorState", "")
                result.append({
                "lock_id": lock_id,
                "lock_name": lock.get('LockName', ''),
                "user_type": lock.get('UserType', ''),
                "mac_address": lock.get('macAddress', ''),
                "house_id": lock.get('HouseID', ''),
                "house_name": lock.get('HouseName', ''),
                "status": lock_status,
                "door_status": door_status
            })
            else:
                result.append({
                "lock_id": lock_id,
                "lock_name": lock.get('LockName', ''),
                "user_type": lock.get('UserType', ''),
                "mac_address": lock.get('macAddress', ''),
                "house_id": lock.get('HouseID', ''),
                "house_name": lock.get('HouseName', ''),
                "status":  f"Error code: {response.status_code} response: {response.text}",
                "door_status": ""
            })
        except requests.RequestException as e:
            result.append({
                "lock_id": lock_id,
                "lock_name": lock.get('LockName', ''),
                "user_type": lock.get('UserType', ''),
                "mac_address": lock.get('macAddress', ''),
                "house_id": lock.get('HouseID', ''),
                "house_name": lock.get('HouseName', ''),
                "status": "error_fetching_status" + str(e),
                "door_status": ""
            })

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
    df = pd.DataFrame(data)
    file_path = os.path.join(settings.BASE_DIR, 'exports', 'unit_device_data.xlsx')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_excel(file_path, index=False)
    # file_path = os.path.abspath(file_name)  # Get full absolute path
    return file_path