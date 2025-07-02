import requests
import pandas as pd
import json
import os
from django.conf import settings

ECOBEE_URL = "https://api.sb.ecobee.com"
BASE_URL = f"{ECOBEE_URL}/api/v1"
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik56QkZRVGM1TlRWRU1qVTVOak5GTXpVek5rUkRRems1TVRFME1VWTNOVUV3TmtVek1EQTJOQSJ9.eyJodHRwczovL2FwaS5zYi5lY29iZWUuY29tL3NtYXJ0YnVpbGRpbmdzLWNvbXBhbnkiOiI2ODM3MmY1NTcwODg4YTQ1YzZiOTMwZTMiLCJpc3MiOiJodHRwczovL2Vjb2JlZS1zYi1kZXYuYXV0aDAuY29tLyIsInN1YiI6InFscGZ0Mk1TY20wQ3B3eWI4RzRkZUpuOFBPSkptU3VyQGNsaWVudHMiLCJhdWQiOiJodHRwczovL2FwaS5zYi5lY29iZWUuY29tIiwiaWF0IjoxNzUxMDEzNTI4LCJleHAiOjE3NTEwMjA3MjgsInNjb3BlIjoiY3JlYXRlOmJ1aWxkaW5nIGNyZWF0ZTp0aGVybW9zdGF0IGRlbGV0ZTpidWlsZGluZyBkZWxldGU6dGhlcm1vc3RhdCByZWFkOmJ1aWxkaW5nIHJlYWQ6YnVpbGRpbmdzIHJlYWQ6dGhlcm1vc3RhdCByZWFkOnRoZXJtb3N0YXRzIHdyaXRlOmJ1aWxkaW5nIHdyaXRlOnRlbmFudG1vZGUgd3JpdGU6dGhlcm1vc3RhdCIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyIsImF6cCI6InFscGZ0Mk1TY20wQ3B3eWI4RzRkZUpuOFBPSkptU3VyIn0.C9u69rmsemNBaWLn3TNbEFAmjNJ1rFhoFWjeUhBe4ano7_0IW81-OxoJTVL2L1HMJtxtHY9KeVWVzggA1jR7v0N5PcLWcPKYjYQCCmuQcQ34ixyCvbeVPghDUXw9yPVKPB-sqxBn5yKwDUaGZgB1Ne9qbPnn7y_ir53bihnkzsgwPcRs4clIY9bAtaTEUEx-jeu3K2RYSnk7Qnwk3VZVWg8htNun5l4PAs_d-CA4PikNKv34Hj7Lj7LPHPsQz_c0hjfXRrUhOju5hSU2W45Ym4Iaxc-KKwZkquuK3870ObMb05tospatYQjoSoLlBnm2njd-dXQvpnSa0ILBg58_kA"

def get_ecobee_device_status():
    payload = json.dumps({
  "audience": "https://api.sb.ecobee.com",
  "grant_type": "client_credentials",
  "client_id": "qlpft2MScm0Cpwyb8G4deJn8POJJmSur",
  "client_secret": "ZrH4BmMQY4OJ8hRbZuQvXnec_qQoXBtZJPBQVeV09S7yFU53LQsljaSj_wQQ9gvR"
})
    url = f"{ECOBEE_URL}/token"
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    if response.status_code != 200:
        return None
    ACCESS_TOKEN = response.json().get('access_token', None)
    if not ACCESS_TOKEN:
        print("Failed to get access token:", response.text)
        return None
    headers = {
        'Authorization': 'Bearer' + ' ' + ACCESS_TOKEN,
    }
    # Step 1: Get the list of thermostats
    # url_thermostats = f"{BASE_URL}/thermostatIds"
    # response = requests.request("GET", url_thermostats, headers=headers)
    # if response.status_code != 200:
    #     print("Failed to fetch thermostat IDs:", response.text)
    #     return

    # data = response.json()
    # thermostat_items = data.get("data", {}).get("items", [])
    # if not thermostat_items:
    #     print("No thermostats found.")
    #     return

    # thermostat_ids = [item.get("serial_no") for item in thermostate_datas]
    # Step 2: For each thermostat, get its status
    # excel_file_path = "ecobee_device_with_unit.xlsx"  # Change to your file path
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Current file directory
    excel_file_path = os.path.join(base_dir, 'ecobee_device_with_unit.xlsx')
    df = pd.read_excel(excel_file_path)
    thermostate_datas = df.to_dict(orient='records')
    results = []
    for thermostat_data in thermostate_datas:
        thermostat_id = thermostat_data.get("serial_no", None)
        if not thermostat_id:
            print("Thermostat ID not found in data:", thermostat_data)
            continue
        else:
            status_url = f"{BASE_URL}/thermostats/{thermostat_id}/status"
            status_response = requests.get(status_url, headers=headers)
            if status_response.status_code != 200:
                print(f"Failed to fetch status for thermostat {thermostat_id}")
                results.append({
                "serial_no": f'{thermostat_data.get("serial_no")}',
                "unit": thermostat_data.get("unit"),
                "part_number": thermostat_data.get("part_number"),
                "model": thermostat_data.get("model"),
                "location": thermostat_data.get("location"),
                "brand": thermostat_data.get("brand"),
                "device": thermostat_data.get("device"),
                "isConnected": "API Error - " + status_response.text
            })
                continue
            status_data = status_response.json().get("data", {})
            is_connected = status_data.get("isConnected", False)
            results.append({
                "serial_no": f'{thermostat_data.get("serial_no")}',
                "unit": thermostat_data.get("unit"),
                "part_number": thermostat_data.get("part_number"),
                "model": thermostat_data.get("model"),
                "location": thermostat_data.get("location"),
                "brand": thermostat_data.get("brand"),
                "device": thermostat_data.get("device"),
                "isConnected": is_connected
            })

    if results:
        df = pd.DataFrame(results)
        file_path = os.path.join(settings.BASE_DIR, 'exports', 'ecobee_device_status.xlsx')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False)
        print(f"✅ Data exported to {file_path}")
        # output_file = "ecobee_device_status.xlsx"
        # df.to_excel(output_file, index=False)
        print("✅ Data exported to ecobee_device_status.xlsx")
        return file_path
    else:
        print("⚠️ No data to export.")
        return None

if __name__ == "__main__":
    # print("Serial numbers from Excel:", json_data)
    get_ecobee_device_status()