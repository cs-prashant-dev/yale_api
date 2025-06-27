
import requests

BASE_URL = 'https://api.august.com'
AUGUST_API_KEY = '9b4c5068-34c5-43af-90e8-d9a31c04565b'
AUGUST_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NDgwMDI5NzgsImV4cCI6MTc1ODM3MDk3OCwiZXhwaXJlc0F0IjoiMjAyNS0wOS0yMFQxMjoyMjo1OC44OTVaIiwiaW5zdGFsbElkIjoiIiwicmVnaW9uIjoiIiwiYXBwbGljYXRpb25JZCI6IiIsInVzZXJJZCI6IjE3ZmIxZGFjLTZkMWItNDY5MC1iZWU0LTZmMzcwMWUzOTg1NSIsInZJbnN0YWxsSWQiOmZhbHNlLCJ2UGFzc3dvcmQiOnRydWUsInZFbWFpbCI6dHJ1ZSwidlBob25lIjp0cnVlLCJoYXNJbnN0YWxsSWQiOmZhbHNlLCJoYXNQYXNzd29yZCI6ZmFsc2UsImhhc0VtYWlsIjpmYWxzZSwiaGFzUGhvbmUiOmZhbHNlLCJpc0xvY2tlZE91dCI6ZmFsc2UsImNhcHRjaGEiOiIiLCJlbWFpbCI6W10sInBob25lIjpbXSwidGVtcG9yYXJ5QWNjb3VudENyZWF0aW9uUGFzc3dvcmRMaW5rIjoiIiwiaGFzQXBwbGVVc2VySUQiOmZhbHNlLCJ2QXBwbGVVc2VySUQiOmZhbHNlLCJvYXV0aCI6eyJhcHBfbmFtZSI6IklvVCBDb250cm9sbGVyIEFTU0EiLCJjbGllbnRfaWQiOiI1NTJmMmMyNi01MjQ4LTRjMTctODc2NS05YTM3ZmM5YTBjNDciLCJyZWRpcmVjdF91cmkiOiJodHRwczovL2V4YW1wbGUuY29tL2NhbGxiYWNrIiwicGFydG5lcl9pZCI6IjY0YmQzNzVlMzJjYTk0MDAxNDYyNzlkYyJ9fQ.4NnOd3Qu_-z2-a0LFT-PGQMYSCbCdfbHz_IsMKIoJDg'

def getLocksDetails(data):
    unit_id = data.get("id")
    name = data.get("name")
    code = data.get("code")
    url = f"{BASE_URL}/get/unit/info?unitId={unit_id}"
    headers = {
        'x-august-api-key': AUGUST_API_KEY,
        'x-august-access-token': AUGUST_ACCESS_TOKEN
    }

    response = requests.request("GET", url, headers=headers)
    if (response.status_code != 200):
        return []

    locks = []

    for lock_id, lock_info in response.json():
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
                if json_data.get("status") == "success":
                    unitId_data = json_data.get("data", [])
                    for unit in unitId_data:
                        devices = unit.get("devices", [])
                        if devices:
                            for device in devices:
                                # brandResponse = checkBrandAndCollectResponse(device)
                                services = device.get("services", [])
                                result.append({
                                    "unit_id": unit_id,
                                    "unit_name": name,
                                    "unit_code": code,
                                    "available": "Yes",
                                    "serial_no": device.get("serial_no"),
                                    "model": device.get("model"),
                                    "brand": device.get("brand"),
                                    "category": device.get("category"),
                                    "location": device.get("location"),
                                    "name": device.get("name"),
                                    # 'api_response': brandResponse,
                                    "isServiceAvailable": True if services else False,
                                })
                        else:
                            result.append({
                                "unit_id": unit_id,
                                "unit_name": name,
                                "unit_code": code,
                                "available": "No",
                                "serial_no": None,
                                "model": None,
                                "brand": None,
                                "category": None,
                                "location": None,
                                "name": None,
                                "isServiceAvailable": None,
                                'api_response': {
                                    "status": "no_devices",
                                    "reason": "Unit has no devices"
                                },
                            })
                else:
                    result.append({
                        "unit_id": unit_id,
                        "unit_name": name,
                        "unit_code": code,
                        "available": "No",
                        "serial_no": None,
                        "model": None,
                        "brand": None,
                        "category": None,
                        "location": None,
                        "name": None,
                        "isServiceAvailable":  None,
                        'api_response': {
                            "status": "api_error",
                            "reason": f"API response status != success {json_data}"
                        },
                    })
            else:
                result.append({
                    "unit_id": unit_id,
                    "unit_name": name,
                    "unit_code": code,
                    "available": "No",
                    "serial_no": None,
                    "model": None,
                    "brand": None,
                    "category": None,
                    "location": None,
                    "name": None,
                    "isServiceAvailable":  None,
                    'api_response': {
                        "status": "http_error",
                        "reason": f"HTTP status {response.status_code}"
                    },
                })
        except requests.RequestException as e:
            result.append({
                "unit_id": unit_id,
                "unit_name": name,
                "unit_code": code,
                "available": "No",
                "serial_no": None,
                "model": None,
                "brand": None,
                "category": None,
                "location": None,
                "name": None,
                "isServiceAvailable":  None,
                'api_response': {
                    "status": "exception",
                    "reason": str(e)
                },
            })

    return result