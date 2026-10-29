import requests
import json
from pathlib import Path
import base64
from databricks.sdk import WorkspaceClient

# Connect to Databricks and retrieve the secret
w = WorkspaceClient(profile="DEFAULT")

secret = w.secrets.get_secret(
    scope="sm_api_secret_key",
    key="twelve-data-api-key"
)

api_key = base64.b64decode(secret.value).decode("utf-8").strip()

# Twelve Data API
URL = "https://api.twelvedata.com/time_series"

params = {
    "symbol": "AAPL",
    "interval": "1day",
    "outputsize": 5,
    "apikey": api_key
}

file_path = Path("output/response_json.json")

try:
    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if data.get("status") == "error":
        print("Twelve Data API Error:", data.get("message"))
        print("Error code:", data.get("code"))

    elif "values" not in data:
        print("Unexpected API response:", json.dumps(data, indent=4))

    else:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Data retrieved successfully!")
        print(f"Stock: {data['meta']['symbol']}")
        print(f"Records received: {len(data['values'])}")
        print(f"Saved to: {file_path}")

except requests.exceptions.Timeout:
    print("Error: The API request timed out.")

except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to Twelve Data.")

except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")

