import requests
import pandas as pd

BASE_URL = "https://staging.allistic.co"
COOKIE = 'color_scheme=light; frontend_lang=en_US; session_id=f9f106ac670cf0173904a551f13637e3fa0e2dde'

def getUnitsList():
    url = f"{BASE_URL}/get/units"
    headers = {
        'Cookie': COOKIE
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            units = data.get("units", [])
            return units
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

# def getUnitById(data):
#     unit_id = data.get("id")
#     name = data.get("name")
#     code = data.get("code")
#     url = f"{BASE_URL}/get/unit/info?unitId={unit_id}"
#     headers = {
#         'Cookie': COOKIE
#     }

#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         data = response.json()
#         if data.get("status") == "success":
#             result = []
#             unitId_data = data.get("data", [])
#             for unit in unitId_data:
#                 devices = unit.get("devices", [])
#                 if devices:
#                     for device in devices:
#                         brandResponse = checkBrandAndCollectResponse(device)
#                         result.append({
#                             "unit_id": unit_id,
#                             "unit_name": name,
#                             "unit_code": code,
#                             "available": "Yes",
#                             "serial_no": device.get("serial_no"),
#                             "model": device.get("model"),
#                             "brand": device.get("brand"),
#                             "category": device.get("category"),
#                             "location": device.get("location"),
#                             "name": device.get("name"),
#                             'api_response': brandResponse if brandResponse else None,
#                         })
#                 else:
#                     result.append({
#                             "unit_id": unit_id,
#                             "unit_name": name,
#                             "unit_code": code,
#                             "available": "No",
#                             "serial_no": None,
#                             "model": None,
#                             "brand": None,
#                             "category": None,
#                             "location": None,
#                             "name": None,
#                             'api_response': {
#                                 "status": "no_devices",
#                                 "reason": "Unit has no devices"
#                             },
#                         })
#             return result
#         else:
#             print("API returned failure status.")
#             return None
#     else:
#         print(f"Request failed with status code {response.status_code}")
#         return None

def getUnitById(data):
    unit_id = data.get("id")
    name = data.get("name")
    code = data.get("code")
    url = f"{BASE_URL}/get/unit/info?unitId={unit_id}"
    headers = {
        'Cookie': COOKIE
    }

    result = []

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("status") == "success":
                unitId_data = json_data.get("data", [])
                for unit in unitId_data:
                    devices = unit.get("devices", [])
                    if devices:
                        for device in devices:
                            brandResponse = checkBrandAndCollectResponse(device)
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
                                'api_response': brandResponse,
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

if __name__ == "__main__":
    devices = getUnitsList()
    all_unit_data = []
    # unit_data = getUnitById({
    #         "id": 541,
    #         "name": "548",
    #         "code": "67813b3124919e25abe9008d"
    #     })
    # if unit_data:
    #     all_unit_data.extend(unit_data)
    for d in devices:
        unit_data = getUnitById(d)
        if unit_data:
            all_unit_data.extend(unit_data)
    print(all_unit_data)
    if all_unit_data:
        df = pd.DataFrame(all_unit_data)
        df.to_excel("unit_device_data.xlsx", index=False)
        print("✅ Data exported to unit_device_data.xlsx")
    else:
        print("⚠️ No data to export.")