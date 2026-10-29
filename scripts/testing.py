import requests
import base64
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEFAULT")

secret = w.secrets.get_secret(
    scope="sm_api_secret_key",
    key="twelve-data-api-key"
)

api_key = secret.value.strip()
api = base64.b64decode(secret.value).decode("utf-8").strip()

print(api)
print(api_key)
#
# print(api_key)response = requests.get("https://api.twelvedata.com/price",params={"symbol": "AAPL", "apikey": api_key},timeout=30)
#
# print(api_key)print("HTTP status:", response.status_code)
#print("Response:", response.text)