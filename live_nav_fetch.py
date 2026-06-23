import requests
import pandas as pd
import os

os.makedirs("data/raw/live_nav", exist_ok=True)

funds = {
    "HDFC_Top100_Direct": 125497,
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_LargeCap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

print("fetching live nav data...\n")

for fund_name, amfi_code in funds.items():
    url = f"https://api.mfapi.in/mf/{amfi_code}"

    try:
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            data = r.json()
            scheme = data["meta"]["scheme_name"]
            df = pd.DataFrame(data["data"])
            path = f"data/raw/live_nav/{fund_name}.csv"
            df.to_csv(path, index=False)
            print(f"{scheme} -> {len(df)} records saved")
        else:
            print(f"failed: {fund_name} (status {r.status_code})")

    except Exception as e:
        print(f"error: {fund_name} - {e}")

print("\ndone.")