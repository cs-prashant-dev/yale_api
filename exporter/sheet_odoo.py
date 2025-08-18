import requests
import pandas as pd
from django.conf import settings
import os
import json

BASE_URL = "https://allisticapi.confidosoftsolutions.com"
COOKIE = 'color_scheme=light; frontend_lang=en_US; session_id=c33110f96f62b8f20cd1de5a0b1983265dd9d4a9'

def update_cookie():
    global COOKIE  # <-- Allow modification of the global variable

    url = f"{BASE_URL}/api/v1/Auth/login"
    payload = json.dumps({
        "email": "admin@confidosoft.com",
        "password": "Test@123",
        "clientType": 0,
        "deviceId": "string",
        "rememberMe": True
        })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} {response.text}")

    # Extract session_id from response cookies
    access_token = response.json().get('data').get('access_token')
    if not access_token:
        raise Exception("Access Token not found in cookies")
    # Update the global COOKIE variable
    COOKIE = f'{access_token}'

def getUnitsList():
    url = f"{BASE_URL}/api/v1/Unit"
    headers = {
        'Authorization': f'Bearer {COOKIE}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('data').get('items')
        if data is not None:
            # units = data.get("units", [])
            return data
        else:
            print("API returned failure status.")
            return []
    else:
        print(f"Request failed with status code {response.status_code}")
        return []

def get_lock_info_url(data, lock_id):
    services = data.get("services", [])
    filtered = list(filter(lambda s: s.get("name") == "lock_info", services))
    if filtered:
        template = filtered[0].get("api_endpoint", "")
        return template.format(lockId=lock_id)
    return None

def get_thermostate_summary_info_url(data, serial_no):
    services = data.get("services", [])
    filtered = list(filter(lambda s: s.get("name") == "lock_info", services))
    if filtered:
        template = filtered[0].get("summary_thermostate", "")
        return template.format(lockId=serial_no)
    return None

def extract_august_tokens(data):
    credentials = data.get("credentials_ids", {})
    api_key = credentials.get("x_august_api_key")
    access_token = credentials.get("august_access_token")
    return api_key, access_token

def ecobee_client_secret(data):
    credentials = data.get("credentials_ids", {})
    api_key = credentials.get("ecobee_jwt_token")
    access_token = credentials.get("ecobee_client_id")
    return api_key, access_token

import requests

def checkBrandAndCollectResponse(data):
    serial_no = data.get("serial_no")
    brand_raw = data.get("brand", "")
    clean_brand = brand_raw.replace('\\', '')

    # Check for target brand
    if clean_brand == 'Master Lock Company LLC ("Yale")':
        deviceBaseUrl = data.get('base_url')
        if not deviceBaseUrl or not serial_no:
            return {
                "status": "error",
                "reason": "Missing base_url or serial_no",
                "serial_no": serial_no
            }

        # Get API credentials
        api_key, access_token = extract_august_tokens(data)
        if not api_key or not access_token:
            return {
                "status": "error",
                "reason": "Missing API key or access token",
                "serial_no": serial_no
            }

        # Generate full endpoint URL
        lock_info_path = get_lock_info_url(data, serial_no)
        if not lock_info_path:
            return {
                "status": "error",
                "reason": "Missing lock_info service URL",
                "serial_no": serial_no
            }

        full_url = f"{deviceBaseUrl}{lock_info_path}"
        headers = {
            'x-august-api-key': api_key,
            'x-august-access-token': access_token
        }

        try:
            response = requests.get(full_url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "serial_no": serial_no,
                    "url_called": full_url,
                    "status_code": response.status_code,
                    "api_response_data": response.json()
                }
            else:
                return {
                    "status": "api_error",
                    "reason": f"API call failed with status {response.status_code}",
                    "serial_no": serial_no,
                    "url_called": full_url,
                    "status_code": response.status_code
                }
        except requests.RequestException as e:
            return {
                "status": "exception",
                "reason": f"Request exception: {str(e)}",
                "serial_no": serial_no,
                "url_called": full_url
            }
    elif clean_brand.lower() == 'ecobee':
        deviceBaseUrl = data.get('base_url')
        if not deviceBaseUrl or not serial_no:
            return {
                "status": "error",
                "reason": "Missing base_url or serial_no",
                "serial_no": serial_no
            }

        # Get API credentials
        api_key, access_token = ecobee_client_secret(data)
        if not api_key or not access_token:
            return {
                "status": "error",
                "reason": "Missing API key or access token",
                "serial_no": serial_no
            }

        # Generate full endpoint URL
        info_path = get_thermostate_summary_info_url(data, serial_no)
        if not info_path:
            return {
                "status": "error",
                "reason": "Missing summary_thermostate service URL",
                "serial_no": serial_no
            }

        full_url = f"{deviceBaseUrl}{info_path}"
        headers = {
            'authorization': f'Bearer {api_key}'
        }

        try:
            response = requests.get(full_url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "serial_no": serial_no,
                    "url_called": full_url,
                    "status_code": response.status_code,
                    "api_response_data": response.json()
                }
            else:
                return {
                    "status": "api_error",
                    "reason": f"API call failed with status {response.status_code}",
                    "serial_no": serial_no,
                    "url_called": full_url,
                    "status_code": response.status_code
                }
        except requests.RequestException as e:
            return {
                "status": "exception",
                "reason": f"Request exception: {str(e)}",
                "serial_no": serial_no,
                "url_called": full_url
            }

def getSmartHQResponse(serialNo, accessToken):
    url = f"https://client.mysmarthq.com/v2/device/{serialNo}"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {accessToken}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def getUnitById(data):
    # unit_id = data.get("id")
    # name = data.get("name")
    # code = data.get("propertyId")
    # url = f"{BASE_URL}/validate/user/{unit_id}"
    # headers = {
    #     'Authorization': f'Bearer {COOKIE}'
    # }

    result = []
    serialNo = data
    brandResponse = getSmartHQResponse(serialNo, 'ue1cpzabo957d4aoiu0zjebfor88rh44')
    if brandResponse is not None:
        deviceType = brandResponse.get('deviceType')
        deviceName = deviceType.split(".")[-1].capitalize()
        services = brandResponse.get("services", [])
        for service in services:
            result.append({
                                            "deviceType": deviceType,
                                            "deviceName": deviceName,
                                            "serviceType": service.get('serviceType'),
                                            "domainType": service.get('domainType'),
                                            "supportedCommands": service.get('supportedCommands'),
                                            "state": service.get('state'),
                                            "serviceId": service.get("serviceId"),
                                            "serviceDeviceType": service.get("serviceDeviceType"),
                                            "config": service.get("config"),
                                        })

    return result

def getUnitsDataList():
    # update_cookie()
    # devices = getUnitsList()
    all_unit_data = []

    # unit_data = getUnitById({
    #         "id": 541,
    #         "name": "548",
    #         "code": "67813b3124919e25abe9008d"
    #     })
    # if unit_data:
    #     all_unit_data.extend(unit_data)
    df = pd.read_excel("smart_hq_devices_2025-08-14_10-17-22.xlsx", usecols=["deviceId"])
    devices = df["deviceId"].tolist()
    for d in devices:
        unit_data = getUnitById(d)
        if unit_data:
            all_unit_data.extend(unit_data)

    print(all_unit_data)

    if all_unit_data:
        df = pd.DataFrame(all_unit_data)
        # file_path = "unit_device_data.xlsx"
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        OUTPUT_FILE = f"odoo_devices_{timestamp}.xlsx"
        file_path = os.path.join(settings.BASE_DIR, 'exports', OUTPUT_FILE)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False)
        print(f"✅ Data exported to {file_path}")
        return file_path
    else:
        print("⚠️ No data to export.")
        return None

# if __name__ == "__main__":
#     getUnitsDataList()
    # devices = getUnitsList()
    # all_unit_data = []
    # # unit_data = getUnitById({
    # #         "id": 541,
    # #         "name": "548",
    # #         "code": "67813b3124919e25abe9008d"
    # #     })
    # # if unit_data:
    # #     all_unit_data.extend(unit_data)
    # for d in devices:
    #     unit_data = getUnitById(d)
    #     if unit_data:
    #         all_unit_data.extend(unit_data)
    # print(all_unit_data)
    # if all_unit_data:
    #     df = pd.DataFrame(all_unit_data)
    #     df.to_excel("unit_device_data.xlsx", index=False)
    #     print("✅ Data exported to unit_device_data.xlsx")
    # else:
    #     print("⚠️ No data to export.")