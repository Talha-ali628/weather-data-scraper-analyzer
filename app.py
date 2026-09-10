import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from weather_scraper import scrape_all_cities
# --------------------------------------------------
# CUSTOM DASHBOARD STYLE
# --------------------------------------------------

st.markdown("""
<style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.10);
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricValue"] {
        font-size: 30px;
        font-weight: 700;
    }

    h1 {
        font-size: 42px !important;
        font-weight: 800 !important;
    }

    h2 {
        margin-top: 25px !important;
    }

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Weather Data Analyzer",
    page_icon="🌦️",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("weather_data.csv")

    # Convert date column to datetime
    df["Date"] = pd.to_datetime(df["Date"])

    return df


df = load_data()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.markdown(
    """
    <h1 style="text-align: center;">
        🌦️ Weather Data Scraper & Analyzer
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="text-align: center; font-size: 18px;">
        Explore hourly weather patterns across major Indian cities
        using historical weather data.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.markdown(
    """
    <h2 style="margin-bottom: 0;">🔎 Filters</h2>
    <p style="font-size: 14px;">
        Customize the weather analysis below.
    </p>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown("### 🏙️ Location")
# City filter
cities = sorted(df["City"].unique())

selected_city = st.sidebar.selectbox(
    "Select City",
    ["All Cities"] + cities
)


# Date filter
st.sidebar.markdown("### 📅 Date Range")
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if st.sidebar.button("🔄 Refresh Latest weather data",
                     use_container_width= True):

    with st.spinner("Collecting latest weather data..."):
        scrape_all_cities()

    st.cache_data.clear()

    st.success("Weather data refreshed successfully!")

    st.rerun()


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()


# City filter
if selected_city != "All Cities":
    filtered_df = filtered_df[
        filtered_df["City"] == selected_city
    ]


# Date filter
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        &
        (filtered_df["Date"].dt.date <= end_date)
    ]

if filtered_df.empty:
    st.warning("⚠️ No weather records found for the selected filters.")



# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

if filtered_df.empty:
    avg_temperature = 0
    max_temperature = 0
    avg_humidity = 0
    avg_wind_speed = 0
else:
    avg_temperature = filtered_df["Temperature (°C)"].mean()
    max_temperature = filtered_df["Temperature (°C)"].max()
    avg_humidity = filtered_df["Humidity (%)"].mean()
    avg_wind_speed = filtered_df["Wind Speed (km/h)"].mean()


# --------------------------------------------------
# DATASET SUMMARY
# --------------------------------------------------

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric(
        "🏙️ Cities",
        filtered_df["City"].nunique()
    )

with summary_col2:
    st.metric(
        "📋 Records",
        f"{len(filtered_df):,}"
    )

with summary_col3:
    st.metric(
        "📅 Start Date",
        filtered_df["Date"].min().strftime("%d %b %Y")
        if not filtered_df.empty else "N/A"
    )

with summary_col4:
    st.metric(
        "📅 End Date",
        filtered_df["Date"].max().strftime("%d %b %Y")
        if not filtered_df.empty else "N/A"
    )

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.markdown("---")
st.subheader("📊 Weather Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "🌡️ Average Temperature",
        f"{avg_temperature:.1f} °C"
    )


with col2:
    st.metric(
        "🔥 Maximum Temperature",
        f"{max_temperature:.1f} °C"
    )


with col3:
    st.metric(
        "💧 Average Humidity",
        f"{avg_humidity:.1f} %"
    )


with col4:
    st.metric(
        "💨 Average Wind Speed",
        f"{avg_wind_speed:.1f} km/h"
    )

# --------------------------------------------------
# TEMPERATURE TREND
# --------------------------------------------------
st.markdown("---")
st.subheader("📈 Temperature Analysis")

temperature_df = (
    filtered_df
    .groupby("Date", as_index=False)["Temperature (°C)"]
    .mean()
)

fig_temp = px.line(
    temperature_df,
    x="Date",
    y="Temperature (°C)",
    markers=True,
    title="Average Daily Temperature"
)

fig_temp.update_layout(
    xaxis_title="Date",
    yaxis_title="Temperature (°C)",
    hovermode="x unified"
)

st.plotly_chart(
    fig_temp,
    use_container_width=True
)


# --------------------------------------------------
# CITY TEMPERATURE COMPARISON
# --------------------------------------------------

st.subheader("🏙️ City Temperature Comparison")

city_temp = (
    filtered_df
    .groupby("City", as_index=False)["Temperature (°C)"]
    .mean()
    .sort_values(
        "Temperature (°C)",
        ascending=False
    )
)

fig_city = px.bar(
    city_temp,
    x="City",
    y="Temperature (°C)",
    title="Average Temperature by City",
    text_auto=".1f"
)

fig_city.update_layout(
    xaxis_title="City",
    yaxis_title="Average Temperature (°C)"
)

st.plotly_chart(
    fig_city,
    use_container_width=True
)
# --------------------------------------------------
# HUMIDITY AND WIND ANALYSIS
# --------------------------------------------------
st.markdown("---")
st.subheader("🌬️ Atmospheric Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("💧 Humidity Analysis")

    humidity_df = (
        filtered_df
        .groupby("Date", as_index=False)["Humidity (%)"]
        .mean()
    )

    fig_humidity = px.line(
        humidity_df,
        x="Date",
        y="Humidity (%)",
        markers=True,
        title="Average Daily Humidity"
    )

    fig_humidity.update_layout(
        xaxis_title="Date",
        yaxis_title="Humidity (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_humidity,
        use_container_width=True
    )


with col2:
    st.subheader("💨 Wind Speed Analysis")

    wind_df = (
        filtered_df
        .groupby("Date", as_index=False)["Wind Speed (km/h)"]
        .mean()
    )

    fig_wind = px.line(
        wind_df,
        x="Date",
        y="Wind Speed (km/h)",
        markers=True,
        title="Average Daily Wind Speed"
    )

    fig_wind.update_layout(
        xaxis_title="Date",
        yaxis_title="Wind Speed (km/h)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_wind,
        use_container_width=True
    )


# --------------------------------------------------
# RAINFALL ANALYSIS
# --------------------------------------------------
st.markdown("---")
st.subheader("🌧️ Rainfall Analysis")

rain_df = (
    filtered_df
    .groupby("Date", as_index=False)["Rain (mm)"]
    .sum()
)

fig_rain = px.bar(
    rain_df,
    x="Date",
    y="Rain (mm)",
    title="Daily Rainfall"
)

fig_rain.update_layout(
    xaxis_title="Date",
    yaxis_title="Rainfall (mm)"
)

st.plotly_chart(
    fig_rain,
    use_container_width=True
)


# --------------------------------------------------
# WEATHER CONDITIONS
# --------------------------------------------------
st.markdown("---")
st.subheader("☁️ Weather Conditions")

condition_df = (
    filtered_df["Weather Condition"]
    .value_counts()
    .reset_index()
)

condition_df.columns = [
    "Weather Condition",
    "Count"
]

fig_condition = px.pie(
    condition_df,
    names="Weather Condition",
    values="Count",
    title="Weather Condition Distribution",
    hole=0.4
)

st.plotly_chart(
    fig_condition,
    use_container_width=True
)
# --------------------------------------------------
# CITY WEATHER SUMMARY
# --------------------------------------------------
st.markdown("---")
st.subheader("🏙️ City Weather Summary")

city_summary = (
    filtered_df
    .groupby("City")
    .agg(
        Average_Temperature=("Temperature (°C)", "mean"),
        Maximum_Temperature=("Temperature (°C)", "max"),
        Average_Humidity=("Humidity (%)", "mean"),
        Total_Rainfall=("Rain (mm)", "sum"),
        Average_Wind_Speed=("Wind Speed (km/h)", "mean")
    )
    .reset_index()
)

city_summary = city_summary.round(2)

st.dataframe(
    city_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "City": st.column_config.TextColumn(
            "City"
        ),
        "Average_Temperature": st.column_config.NumberColumn(
            "Avg Temperature (°C)",
            format="%.2f °C"
        ),
        "Maximum_Temperature": st.column_config.NumberColumn(
            "Max Temperature (°C)",
            format="%.2f °C"
        ),
        "Average_Humidity": st.column_config.NumberColumn(
            "Avg Humidity (%)",
            format="%.2f %%"
        ),
        "Total_Rainfall": st.column_config.NumberColumn(
            "Total Rainfall (mm)",
            format="%.2f mm"
        ),
        "Average_Wind_Speed": st.column_config.NumberColumn(
            "Avg Wind Speed (km/h)",
            format="%.2f km/h"
        )
    }
)

# --------------------------------------------------
# WEATHER INSIGHTS
# --------------------------------------------------
st.markdown("---")
st.subheader("💡 Weather Insights")

if not filtered_df.empty:

    hottest_city = (
        filtered_df
        .groupby("City")["Temperature (°C)"]
        .mean()
        .idxmax()
    )

    coolest_city = (
        filtered_df
        .groupby("City")["Temperature (°C)"]
        .mean()
        .idxmin()
    )

    wettest_city = (
        filtered_df
        .groupby("City")["Rain (mm)"]
        .sum()
        .idxmax()
    )

    most_humid_city = (
        filtered_df
        .groupby("City")["Humidity (%)"]
        .mean()
        .idxmax()
    )

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:

        st.info(
            f"🌡️ **Hottest City:** {hottest_city}"
        )

        st.info(
            f"❄️ **Coolest City:** {coolest_city}"
        )

    with insight_col2:

        st.info(
            f"🌧️ **Wettest City:** {wettest_city}"
        )

        st.info(
            f"💧 **Most Humid City:** {most_humid_city}"
        )
# --------------------------------------------------
# DOWNLOAD FILTERED DATA
# --------------------------------------------------
st.markdown("---")
st.subheader("⬇️ Download Weather Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_weather_data.csv",
    mime="text/csv"
)
# --------------------------------------------------
# FILTERED DATA INFORMATION
# --------------------------------------------------
st.markdown("---")
st.subheader("📋 Filtered Weather Data")

st.write(
    f"Showing **{len(filtered_df):,} records** "
    f"across **{filtered_df['City'].nunique()} cities**."
)


st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)




# --------------------------------------------------
# ABOUT THE PROJECT
# --------------------------------------------------

st.markdown("---")

st.subheader("ℹ️ About This Project")

st.write(
    """
    This Weather Data Scraper & Analyzer collects hourly weather
    data for major Indian cities and converts the collected data
    into an interactive analytics dashboard.

    The dashboard allows users to explore temperature, humidity,
    rainfall, wind speed, atmospheric pressure, cloud cover,
    and weather conditions.

    ### Technology Stack

    Python • Requests • Pandas • NumPy • Plotly • Streamlit

    ### Data Coverage

    10 Indian Cities • Approximately 30 Days • Hourly Weather Data

    ### Key Features

    Interactive filters • Weather analysis • City comparison
    • Data visualization • Weather insights • CSV download
    """
)
st.info(
    "💡 Use the sidebar filters to explore weather patterns, "
    "compare cities, analyze rainfall and humidity, and download "
    "the filtered dataset."
)