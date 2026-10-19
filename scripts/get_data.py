import requests
import json

URL = "https://api.twelvedata.com/time_series"

payload = {
    "symbol" : "AAPL",
    "interval" : "1day",
    "apikey" : "f8a206c64585466fad5387eb02126054"
}

file_path = "output/response_json.json"   

try:
    response = requests.get(URL, params=payload, timeout=30)

    # 1. Check HTTP status code
    if not response.ok:
        print(f"HTTP Error: {response.status_code}")
        print(response.text)
    else:
        # 2. Parse the JSON response
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Error: Response is not valid JSON.")
            raise SystemExit

        # 3. Check for an API-level error
        if data.get("status") == "error" or "code" in data and "message" in data and "values" not in data:
            print("API Error:", data.get("message", "Unknown API error"))
            print("Error code:", data.get("code"))

        # 4. Check that expected data exists
        elif "values" not in data:
            print("Unexpected response:", json.dumps(data, indent=4))

        else:
            data = response.json()
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False)
            print("Data retrieved successfully!")

except requests.exceptions.Timeout:
    print("Error: The API request timed out.")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to Twelve Data.")

except requests.exceptions.RequestException as e:
    print("Request error:", e)
