
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Weather Big Data Analytics",
    page_icon="🌦️",
    layout="wide"
)

# ========== COLOURFUL UI ==========
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f0f9ff, #f8fafc, #f0fdfa);
}
h1 {
    color: #172554 !important;
    font-weight: 800 !important;
}
h2, h3 {
    color: #1e40af !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172554, #1e3a5f);
}
[data-testid="stSidebar"] * {
    color: white;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #eff6ff);
    border: 1px solid #bfdbfe;
    border-left: 5px solid #38bdf8;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.08);
}
[data-testid="stMetricLabel"] {
    color: #475569 !important;
}
[data-testid="stMetricValue"] {
    color: #1d4ed8 !important;
    font-weight: 800;
}
.stDownloadButton button {
    background: linear-gradient(90deg, #2563eb, #0891b2);
    color: white;
    border-radius: 9px;
    border: none;
    font-weight: 600;
}
hr {
    border-color: #cbd5e1;
}
</style>
""", unsafe_allow_html=True)

# ========== PROJECT PATHS ==========
PROJECT_DIR = Path(__file__).resolve().parent
CSV_PATH = PROJECT_DIR / "data" / "weather_data.csv"

# ========== DASHBOARD HEADER ==========
st.title("🌦️ Weather Big Data Analytics")
st.caption(
    "Historical weather analysis using Apache Spark and Python"
)

# ========== LIVE WEATHER API ==========
st.divider()
st.header("🌍 Live Weather Across Indian Cities")
st.caption("Current conditions from the Open-Meteo weather API")

CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Delhi": (28.6139, 77.2090),
    "Chennai": (13.0827, 80.2700),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Nagpur": (21.1458, 79.0882),
    "Nashik": (19.9975, 73.7898),
    "Bhopal": (23.2599, 77.4126),
    "Chandigarh": (30.7333, 76.7794),
    "Kochi": (9.9312, 76.2673),
    "Indore": (22.7196, 75.8577),
    "Surat": (21.1702, 72.8311),
    "Vadodara": (22.3072, 73.1812),
    "Rajkot": (22.3039, 70.8022),
    "Amritsar": (31.6340, 74.8723),
    "Dehradun": (30.3165, 78.0322),
    "Patna": (25.5941, 85.1376),
    "Ranchi": (23.3441, 85.3096),
    "Bhubaneswar": (20.2961, 85.8245),
    "Guwahati": (26.1445, 91.7362),
    "Srinagar": (34.0837, 74.7973),
    "Visakhapatnam": (17.6868, 83.2185),
    "Coimbatore": (11.0168, 76.9558),
    "Mysuru": (12.2958, 76.6394),
    "Thiruvananthapuram": (8.5241, 76.9366),
}


@st.cache_data(ttl=600, show_spinner=False)
def fetch_live_weather(selected_city_names):
    records = []

    for city in selected_city_names:
        latitude, longitude = CITY_COORDINATES[city]
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation,"
                    "wind_speed_10m,"
                    "weather_code"
                ),
                "timezone": "Asia/Kolkata"
            },
            timeout=15
        )

        response.raise_for_status()
        current = response.json()["current"]

        records.append({
            "City": city,
            "Temperature (°C)": current["temperature_2m"],
            "Humidity (%)": current["relative_humidity_2m"],
            "Precipitation (mm)": current["precipitation"],
            "Wind Speed (km/h)": current["wind_speed_10m"],
            "Weather Code": current["weather_code"],
            "Observed Time": current["time"]
        })

    return pd.DataFrame(records)


selected_live_cities = st.multiselect(
    "Choose cities to display",
    options=list(CITY_COORDINATES.keys()),
    default=["Mumbai"],
    key="live_city_selector",
    help="Mumbai is selected by default. Choose any other cities if you want to compare them."
)

if st.button("🔄 Refresh Live Weather"):
    fetch_live_weather.clear()

try:
    if not selected_live_cities:
        st.info("Select at least one city to view its live weather.")
        st.stop()

    with st.spinner(f"Fetching live weather for {len(selected_live_cities)} selected cities..."):
        live_df = fetch_live_weather(tuple(selected_live_cities))

    st.caption(
        "API observation time: "
        + str(live_df["Observed Time"].max())
        + " (India local time)"
    )

    # Display all live-weather city cards in rows of four
    for start in range(0, len(live_df), 4):
        weather_columns = st.columns(4)
        batch = live_df.iloc[start:start + 4]

        for column, (_, weather) in zip(weather_columns, batch.iterrows()):
            with column:
                st.subheader(f"🌤️ {weather['City']}")
                st.metric(
                    "Temperature",
                    f"{weather['Temperature (°C)']:.1f} °C"
                )
                st.caption(
                    f"💧 Humidity: {weather['Humidity (%)']:.0f}%"
                )
                st.caption(
                    f"🌧️ Precipitation: "
                    f"{weather['Precipitation (mm)']:.1f} mm"
                )
                st.caption(
                    f"💨 Wind: {weather['Wind Speed (km/h)']:.1f} km/h"
                )

    # Live temperature comparison
    st.subheader("🌡️ Live Temperature Comparison")

    live_temp_chart = px.bar(
        live_df,
        x="City",
        y="Temperature (°C)",
        color="City",
        color_discrete_sequence=[
            "#2563eb", "#14b8a6", "#f59e0b", "#8b5cf6"
        ],
        title="Current Temperature by City",
    )
    live_temp_chart.update_traces(texttemplate="%{y:.1f}", textposition="outside")
    live_temp_chart.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(live_temp_chart, use_container_width=True)

    st.subheader("📋 Live Weather Data")
    st.dataframe(
        live_df.drop(columns=["Weather Code"]),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Live Weather CSV",
        data=live_df.to_csv(index=False).encode("utf-8"),
        file_name="live_weather_data.csv",
        mime="text/csv"
    )

except requests.RequestException as e:
    st.warning(
        "Live weather API could not be reached. "
        "Check your internet connection and try refreshing."
    )
    st.caption(f"Technical details: {e}")

except (KeyError, ValueError) as e:
    st.error(f"Unexpected live weather response: {e}")

except Exception as e:
    st.error(f"Live weather error: {e}")


# ========== HISTORICAL WEATHER DATA ==========
st.divider()
st.header("📊 Historical Weather Analytics")
st.caption(
    "This section uses data from data/weather_data.csv. "
    "The 30-city historical dataset is synthetic sample data for "
    "demonstration, not actual recorded weather observations."
)


@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "Date", "City", "Temperature",
        "Humidity", "Rainfall", "WindSpeed"
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing CSV columns: " + ", ".join(missing)
        )

    df["Date"] = pd.to_datetime(df["Date"])
    return df


try:
    df = load_data()

    st.sidebar.header("🎛️ Dashboard Filters")
    st.sidebar.caption("Historical dataset filters")

    cities = sorted(df["City"].dropna().unique().tolist())

    historical_default = ["Mumbai"] if "Mumbai" in cities else cities[:1]
    selected_cities = st.sidebar.multiselect(
        "Select cities",
        cities,
        default=historical_default
    )

    filtered_df = df[df["City"].isin(selected_cities)]

    if filtered_df.empty:
        st.warning("Please select at least one city.")
        st.stop()

    # Historical summary cards
    st.subheader("Weather Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Weather Records",
        len(filtered_df)
    )
    c2.metric(
        "Avg Temperature",
        f"{filtered_df['Temperature'].mean():.1f} °C"
    )
    c3.metric(
        "Avg Humidity",
        f"{filtered_df['Humidity'].mean():.1f}%"
    )
    c4.metric(
        "Total Rainfall",
        f"{filtered_df['Rainfall'].sum():.1f} mm"
    )

    st.divider()

    # Temperature trend and average temperature
    left, right = st.columns(2)

    with left:
        st.subheader("🌡️ Temperature by Date")

        fig = px.line(
            filtered_df.sort_values("Date"),
            x="Date",
            y="Temperature",
            color="City",
            markers=True,
            title="Daily Temperature Trends",
            color_discrete_sequence=[
                "#2563eb", "#14b8a6", "#f59e0b", "#8b5cf6"
            ]
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("🏙️ City-wise Average Temperature")

        city_avg = (
            filtered_df.groupby("City", as_index=False)
            ["Temperature"].mean()
        )

        fig2 = px.bar(
            city_avg,
            x="City",
            y="Temperature",
            color="City",
            title="Average Temperature (°C)",
            color_discrete_sequence=[
                "#2563eb", "#14b8a6", "#f59e0b", "#8b5cf6"
            ],
            )

        fig2.update_traces(texttemplate="%{y:.1f}", textposition="outside")
        fig2.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Rainfall and humidity charts
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("🌧️ Rainfall by City")

        rainfall = (
            filtered_df.groupby("City", as_index=False)
            ["Rainfall"].sum()
        )

        fig3 = px.bar(
            rainfall,
            x="City",
            y="Rainfall",
            color="City",
            title="Total Rainfall (mm)",
            color_discrete_sequence=[
                "#0ea5e9", "#14b8a6", "#f59e0b", "#8b5cf6"
            ],
            )

        fig3.update_traces(texttemplate="%{y:.1f}", textposition="outside")
        fig3.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with right2:
        st.subheader("💧 Humidity Comparison")

        humidity = (
            filtered_df.groupby("City", as_index=False)
            ["Humidity"].mean()
        )

        fig4 = px.bar(
            humidity,
            x="City",
            y="Humidity",
            color="City",
            title="Average Humidity (%)",
            color_discrete_sequence=[
                "#0ea5e9", "#14b8a6", "#f59e0b", "#8b5cf6"
            ],
            )

        fig4.update_traces(texttemplate="%{y:.1f}", textposition="outside")
        fig4.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Historical data table
    st.subheader("📁 Historical Weather Dataset")
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Filtered Historical Data",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="weather_analysis.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error(
        "Historical dataset not found. "
        "Check that data/weather_data.csv exists."
    )

except Exception as e:
    st.error(f"Historical dashboard error: {e}")
