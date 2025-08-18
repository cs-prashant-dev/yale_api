import requests
import pandas as pd
import os
from django.conf import settings
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = f"smarthq_devices_{timestamp}.xlsx"

def export_to_excel(devices, filename):
    """Export device data to Excel file"""
    if not devices:
        print("No devices to export")
        return False
    try:
        # Create DataFrame
        df = pd.DataFrame(devices)
        # Export to Excel
        file_path = os.path.join(settings.BASE_DIR, 'exports', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False)
        # df.to_excel(filename, index=False)
        print(f"Successfully exported {len(df)} devices to {filename}")
        return file_path
    except Exception as e:
        print(f"Export failed: {e}")
        return None

def getAccessPoint():
    url = "https://admin.swiftlane.com/api/v1/sites/"

    payload = {}
    headers = {
    'api-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiNzQ3OTg2NjgwOTkyMjkyOTA2IiwidXVpZCI6Ijk0YzU3N2NlLThkZmMtNGM5OS05NzY5LWQ4YTJiYzA0MWJlMyIsImV4cCI6MjA1NDYzNjQ1NH0.JYXZLmkia52p0hAxhaiy4da-IUH2tB__2v_-c-XZrFA'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

    if response.status_code == 200:
        data = response.json()
        all_access_points = []
        for site in data.get("data", {}).get("sites", []):
            for ap in site.get("access_points", []):
                ap["site_id"] = site.get("site_id")  # keep reference to site
                all_access_points.append(ap)

        return export_to_excel(all_access_points, OUTPUT_FILE)
        # return all_access_points
    else:
        print(f"❌ Failed to fetch data. Status code: {response.status_code}")
        print(response.text)
        return None
