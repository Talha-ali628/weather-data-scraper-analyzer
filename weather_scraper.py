import requests
import pandas as pd
from datetime import datetime


# Indian cities with fixed coordinates
# This prevents the geocoder from selecting the wrong city.
CITIES = {
    "Hyderabad": {
        "country": "India",
        "latitude": 17.3850,
        "longitude": 78.4867
    },
    "Mumbai": {
        "country": "India",
        "latitude": 19.0760,
        "longitude": 72.8777
    },
    "Delhi": {
        "country": "India",
        "latitude": 28.6139,
        "longitude": 77.2090
    },
    "Bengaluru": {
        "country": "India",
        "latitude": 12.9716,
        "longitude": 77.5946
    },
    "Chennai": {
        "country": "India",
        "latitude": 13.0827,
        "longitude": 80.2707
    },
    "Kolkata": {
        "country": "India",
        "latitude": 22.5726,
        "longitude": 88.3639
    },
    "Pune": {
        "country": "India",
        "latitude": 18.5204,
        "longitude": 73.8567
    },
    "Ahmedabad": {
        "country": "India",
        "latitude": 23.0225,
        "longitude": 72.5714
    },
    "Jaipur": {
        "country": "India",
        "latitude": 26.9124,
        "longitude": 75.7873
    },
    "Lucknow": {
        "country": "India",
        "latitude": 26.8467,
        "longitude": 80.9462
    }
}


def get_weather_data(city, details):
    """Collect approximately 30 days of hourly weather data."""

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": details["latitude"],
        "longitude": details["longitude"],

        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "rain,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "surface_pressure,"
            "cloud_cover"
        ),

        "past_days": 30,
        "forecast_days": 1,

        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    hourly = data["hourly"]

    city_df = pd.DataFrame({
        "City": city,
        "Country": details["country"],
        "Date": pd.to_datetime(hourly["time"]).date,
        "Time": pd.to_datetime(hourly["time"]).time,
        "Temperature (°C)": hourly["temperature_2m"],
        "Feels Like (°C)": hourly["apparent_temperature"],
        "Humidity (%)": hourly["relative_humidity_2m"],
        "Precipitation (mm)": hourly["precipitation"],
        "Rain (mm)": hourly["rain"],
        "Wind Speed (km/h)": hourly["wind_speed_10m"],
        "Wind Direction (°)": hourly["wind_direction_10m"],
        "Pressure (hPa)": hourly["surface_pressure"],
        "Cloud Cover (%)": hourly["cloud_cover"],
        "Weather Code": hourly["weather_code"]
    })

    return city_df


def get_weather_condition(code):
    """Convert WMO weather codes into readable descriptions."""

    weather_codes = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Heavy Drizzle",
        56: "Light Freezing Drizzle",
        57: "Heavy Freezing Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Light Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Light Rain Showers",
        81: "Moderate Rain Showers",
        82: "Heavy Rain Showers",
        85: "Light Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Thunderstorm with Heavy Hail"
    }

    return weather_codes.get(code, "Unknown")


def scrape_all_cities():
    """Collect weather data from all cities."""

    all_data = []

    print("\nStarting weather data collection...\n")

    for city, details in CITIES.items():

        try:
            print(f"Collecting data for {city}...")

            city_data = get_weather_data(city, details)

            all_data.append(city_data)

            print(
                f"✓ {city}: "
                f"{len(city_data):,} hourly records collected"
            )

        except requests.RequestException as error:

            print(
                f"✗ Error collecting data for {city}: {error}"
            )

        except Exception as error:

            print(
                f"✗ Unexpected error for {city}: {error}"
            )

    if not all_data:
        print("\nNo weather data was collected.")
        return

    # Combine all cities
    final_df = pd.concat(
        all_data,
        ignore_index=True
    )

    # Convert weather codes to descriptions
    final_df["Weather Condition"] = (
        final_df["Weather Code"]
        .apply(get_weather_condition)
    )

    # Sort data
    final_df = final_df.sort_values(
        by=["City", "Date", "Time"]
    )

    # Save CSV
    final_df.to_csv(
        "weather_data.csv",
        index=False
    )

    print("\n----------------------------------------")
    print("Weather data collection completed!")
    print("----------------------------------------")

    print(f"\nTotal records: {len(final_df):,}")
    print(f"Total cities: {final_df['City'].nunique()}")
    print(
        f"Date range: "
        f"{final_df['Date'].min()} → "
        f"{final_df['Date'].max()}"
    )

    print("\nRecords by city:")
    print(
        final_df.groupby("City")
        .size()
        .sort_values(ascending=False)
    )

    print("\nCSV file created:")
    print("weather_data.csv")


if __name__ == "__main__":
    scrape_all_cities()