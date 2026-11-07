import pickle
from datetime import date, timedelta

import pandas as pd
import requests
import streamlit as st

# ---- Settings ----------------------------------------------------------
CITIES = {
    "Pittsburgh": (40.44, -79.99),
    "New York": (40.71, -74.01),
    "Chicago": (41.88, -87.63),
    "Miami": (25.76, -80.19),
    "Los Angeles": (34.05, -118.24),
}

LOW_TEMP, HIGH_TEMP = 50, 100   # the temperatures (F) the model learned from
LOW_SALES, HIGH_SALES = 200, 300  # below LOW_SALES is a slow day, above HIGH_SALES is a busy one
MAX_RAIN = 25                   # the most rain (mm) the model saw in training

URL = "https://api.open-meteo.com/v1/forecast"

# ------------------------------------------------------------------------
# Load the trained model (trained once in Colab, saved to a file).
# Version 2 uses three inputs: temperature, is_weekend, precipitation.
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

st.set_page_config(page_title="Ice Cream Sales Predictor", page_icon="🍦")
st.title("🍦 Ice Cream Sales Predictor")
st.caption("Pick a city and a date. The app gets the weather forecast and predicts how many cones you will sell.")
st.caption("The prediction uses three things: the forecast high, whether the day is a weekend, and the expected rain.")

city = st.selectbox("City", list(CITIES))
selected_date = st.date_input(
    "Date",
    value=date.today() + timedelta(days=1),
    min_value=date.today(),
    max_value=date.today() + timedelta(days=16),  # the forecast reaches about 16 days ahead
)

if st.button("Predict sales", type="primary"):
    # 1. Ask the weather API for the forecast (temperature AND rain)
    latitude, longitude = CITIES[city]
    try:
        response = requests.get(
            URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,precipitation_sum",
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
                "start_date": str(selected_date),
                "end_date": str(selected_date),
            },
            timeout=30,
        )
        response.raise_for_status()
        daily = response.json()["daily"]
        temperature = daily["temperature_2m_max"][0]
        precipitation = daily["precipitation_sum"][0] or 0.0   # mm; None means no data
    except Exception:
        st.error("Could not get the forecast. The weather service may be busy. Wait a minute and try again.")
        st.stop()

    # 2. The weekend flag comes from the date (Monday = 0 ... Sunday = 6)
    is_weekend = 1 if selected_date.weekday() >= 5 else 0

    # 3. Give the model the same inputs it was trained on, then predict
    features = pd.DataFrame({
        "temperature": [temperature],
        "is_weekend": [is_weekend],
        "precipitation": [precipitation],
    })
    prediction = max(0, model.predict(features)[0])

    # 4. Show the result
    col1, col2 = st.columns(2)
    col1.metric("Forecast high", f"{temperature:.0f} °F")
    col2.metric("Predicted sales", f"{prediction:.0f} cones")

    col3, col4 = st.columns(2)
    col3.metric("Day type", "Weekend" if is_weekend else "Weekday")
    col4.metric("Expected rain", f"{precipitation:.1f} mm")

    if temperature < LOW_TEMP or temperature > HIGH_TEMP:
        st.warning(f"This temperature is outside the range the model learned from ({LOW_TEMP} to {HIGH_TEMP} °F). "
                   "Treat the number with caution.")
    if precipitation > MAX_RAIN:
        st.warning(f"This much rain is more than the model saw in training (up to {MAX_RAIN} mm). "
                   "Treat the number with caution.")

    if prediction > HIGH_SALES:
        st.info("Busy day: make sure you are fully stocked.")
    elif prediction > LOW_SALES:
        st.info("A normal day is expected.")
    else:
        st.info("A slow day: consider a promotion, or order less.")
