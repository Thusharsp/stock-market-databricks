
import requests
import json
import base64
from datetime import datetime
from databricks.sdk import WorkspaceClient
from pyspark.sql.types import (StructType, StructField,StringType, DoubleType, LongType, TimestampType)
from pyspark.sql.functions import col


def get_secrets():
    """Retrieve the API key from Databricks secrets."""
    w = WorkspaceClient(profile="DEFAULT")

    secret = w.secrets.get_secret(
        scope="sm_api_secret_key",
        key="twelve-data-api-key"
    )

    api_key = base64.b64decode(secret.value).decode("utf-8").strip()
    return api_key


def get_data():
    """Fetch AAPL daily stock data from Twelve Data."""

    URL = "https://api.twelvedata.com/time_series"
    api_key = get_secrets()

    params = {
        "symbol": "AAPL",
        "interval": "1day",
        "outputsize": 5,
        "apikey": api_key
    }

    try:
        response = requests.get(URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get("status") == "error":
            print("Twelve Data API Error:", data.get("message"))
            print("Error code:", data.get("code"))
            return None

        if "values" not in data:
            print("Unexpected API response:", json.dumps(data, indent=4))
            return None

        print("Data retrieved successfully!")

        return data["values"]

    except requests.exceptions.Timeout:
        print("Error: The API request timed out.")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Twelve Data.")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    return None


def process_data(stock_data):
    if not stock_data:
        print("No stock's data available")
        return None
    
    # DataFrame schema
    schema = StructType([
        StructField("datetime", TimestampType(), True),
        StructField("open", DoubleType(), True),
        StructField("high", DoubleType(), True),
        StructField("low", DoubleType(), True),
        StructField("close", DoubleType(), True),
        StructField("volume", LongType(), True)
    ])

    processed_data = [
        {
            "datetime": datetime.strptime(row["datetime"], "%Y-%m-%d"),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row["volume"])
        }
        for row in stock_data
    ]

    df = spark.createDataFrame(processed_data, schema=schema)
    #selected_df = df.select("datetime","close","high")
    df = df.withColumn("price Exchange",col("Close")- col("open"))
    df = df.filter(col("price Exchange")>0)

    display(df)
    df.printSchema()


# Function calls
stock_data = get_data()
df = process_data(stock_data)