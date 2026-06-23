import requests
import pandas as pd
import os

# Create output folder if it doesn't exist
os.makedirs("data/raw/live_nav", exist_ok=True)

# AMFI Codes
funds = {
    "HDFC_Top100_Direct": 125497,
    "SBI_Bluechip": 119551,
    "ICICI_Bluechip": 120503,
    "Nippon_LargeCap": 118632,
    "Axis_Bluechip": 119092,
    "Kotak_Bluechip": 120841
}

print("=" * 60)
print("LIVE NAV FETCH")
print("=" * 60)

for fund_name, amfi_code in funds.items():

    url = f"https://api.mfapi.in/mf/{amfi_code}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:

            data = response.json()

            # Scheme Information
            scheme_name = data["meta"]["scheme_name"]

            print(f"\nFetching: {scheme_name}")

            nav_df = pd.DataFrame(data["data"])

            file_path = f"data/raw/live_nav/{fund_name}.csv"

            nav_df.to_csv(file_path, index=False)

            print(f"Saved -> {file_path}")
            print(f"Records -> {len(nav_df)}")

        else:
            print(f"Failed: {fund_name}")

    except Exception as e:
        print(f"Error fetching {fund_name}: {e}")

print("\nLIVE NAV FETCH COMPLETED")