import requests
import os
from django.conf import settings

BASE_URL = "https://login.smarthqm.com"
API_BASE_URL = "https://api.smarthqm.com"
CLIENT_SMARTHQ_BASE_URL = "https://client.mysmarthq.com"
CLIENT_ID = 'NsR5cN87qncA26osqWUMNvOSyWrSriwe'
REFRESH_TOKEN = '-19Ce3YqWXrWmoMLVhXLhU7o4uO3mxezeWT-7R2C0p-gv'
CLIENT_SECRET = 'j4lsqDQZ2ysignuapxTrXPZhpa1tmtewKuSc1W1KneCWQ61Y_shyQNb6KxtA8v3p'
# Configuration
OUTPUT_FILE = "smarthq_devices.xlsx"

def getExchangeSmartHqAccessToken():
    try:
        url = f'{BASE_URL}/oauth/token'  # Fixed f-string (removed '$')
        payload = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': REFRESH_TOKEN
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=10  # Prevent hanging requests
        )
        response.raise_for_status()  # Raise exception for 4xx/5xx status

        token_data = response.json()
        if 'access_token' not in token_data:
            print("Access token missing in response")
            return None
        return token_data['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
    except ValueError as e:  # Covers JSON decode errors
        print(f"Invalid JSON response: {str(e)}")
    except KeyError:
        print("Access token key not found in response")
    return None

def getExchangeManagementToken():
    access_token = getExchangeSmartHqAccessToken()
    if not access_token:
        print("Failed to get access token")
        return None

    try:
        url = f"{API_BASE_URL}/v1/token"
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        # Validate and return management token
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Management token request failed: {str(e)}")
    except ValueError as e:
        print(f"Invalid management token response: {str(e)}")
    return None

import requests
import pandas as pd
from time import sleep

def fetch_all_devices(token):
    """Fetch all devices through paginated API requests"""
    base_url = f"{CLIENT_SMARTHQ_BASE_URL}/v2/device"
    page = 1
    perpage = 100
    all_devices = []
    while True:
        try:
            # Make API request with pagination parameters
            response = requests.get(
                url=base_url,
                headers={
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                params={
                    'page': page,
                    'perpage': perpage
                },
                timeout=30
            )
            # Check for HTTP errors
            response.raise_for_status()
            data = response.json()
            # Check if devices key exists
            if 'devices' not in data:
                print(f"Unexpected response format on page {page}")
                break
            # Add devices to collection
            all_devices.extend(data['devices'])
            # Pagination control
            total_items = data.get('total', 0)
            current_count = page * perpage
            print(f"Fetched page {page}: {len(data['devices'])} devices (Total: {len(all_devices)}/{total_items})")
            if current_count >= total_items:
                break
            page += 1
            sleep(0.5)  # Add short delay to avoid rate limiting
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
        except ValueError as e:
            print(f"JSON parsing error: {e}")
            break
    return all_devices

def export_to_excel(devices, filename):
    """Export device data to Excel file"""
    if not devices:
        print("No devices to export")
        return False
    try:
        # Create DataFrame
        df = pd.DataFrame(devices)
        # Export to Excel
        file_path = os.path.join(settings.BASE_DIR, 'exports', 'unit_device_data.xlsx')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False)
        # df.to_excel(filename, index=False)
        print(f"Successfully exported {len(df)} devices to {filename}")
        return file_path
    except Exception as e:
        print(f"Export failed: {e}")
        return None

def getSmartHqData():
    management_token = getExchangeManagementToken()
    if management_token is None:
        return None
    else:
        # Fetch and export data
        devices = fetch_all_devices(management_token)
        if devices:
            return export_to_excel(devices, OUTPUT_FILE)
        else:
            return None