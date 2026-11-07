# 🍦 Ice Cream Sales Predictor (version 2)

Pick a city and a date. The app gets the weather forecast, gives it to a trained model, and shows how many ice cream cones you can expect to sell, with a short business message.

**Live app:** https://predictingicecreamsales-t92vkpwwftwdasiuoysy2y.streamlit.app/

**GitHub repo:** https://github.com/preetham13181/predicting_icecream_sales

## What's new in this version

This project retrains the class example model with more information and updates the app to use it.

| | Version 1 (class example) | Version 2 (this app) |
|---|---|---|
| Predictors | Temperature | Temperature + **Weekend** + **Rainfall** |
| Number of model inputs | 1 | 3 |

### The predictors

| Predictor | Original or new? | Why it affects sales | Effect in the model |
|---|---|---|---|
| Temperature (°F) | Original | Hot days make people want ice cream | About +5 cones per °F |
| Weekend | 🆕 New | More people are out and free on Saturdays and Sundays | About +37 cones |
| Rainfall (mm) | 🆕 New | Rain keeps people at home | About -3 cones per mm |

## How to use it

1. Choose a **city**.
2. Choose a **date** (today up to 16 days ahead, the range of the forecast).
3. Click **Predict sales**.

You don't type in the weather. The app finds the model's three inputs for you.

## What you see

| Result | Meaning |
|---|---|
| Forecast high | The expected high temperature for that day (°F) |
| Predicted sales | The number of cones the model expects you to sell |
| Day type | Weekday or weekend, taken from the date |
| Expected rain | The forecast rainfall for that day (mm) |

Below the numbers, a message tells you whether to expect a **busy day** (more than 300 cones), a **normal day**, or a **slow day** (200 cones or fewer). The app also shows a warning if the temperature or rainfall is outside what the model learned from, so you know to treat the number with caution.

## How it works

```
City + Date ──► Weather API (Open-Meteo) ──► forecast high + rainfall
        │
        └──────► Calendar ──► weekday or weekend
                                   │
        temperature, weekend, rainfall
                                   ▼
                       model.pkl (linear regression)
                                   ▼
                          Predicted cones sold
```

1. The app asks the free [Open-Meteo](https://open-meteo.com) forecast API for the daily high temperature and the total expected rain. No API key is needed.
2. The app checks whether the chosen date is a Saturday or Sunday.
3. The saved model receives the three values and predicts sales.

Example (Tuesday, 63 °F, no rain): roughly 4.9 × 63 − 87 ≈ 221 cones.

## The model

- Type: linear regression (scikit-learn)
- Inputs: `temperature`, `is_weekend`, `precipitation`
- Training data: 400 days of **made-up data**, created in the notebook to demonstrate the steps. Hotter days, weekends, and dry days sell more.
- Saved with `pickle` as `model.pkl`

Because the data is simulated, the predictions show how the workflow works but are not real sales forecasts. A real business would train on its own sales records.

## Files

| File | Purpose |
|---|---|
| `app.py` | The Streamlit app |
| `model.pkl` | The retrained model, saved from the notebook |
| `Week3-Train-and-Save-Model-v2.ipynb` | Notebook that creates the data, retrains the model, and saves `model.pkl` |
| `requirements.txt` | Packages that Streamlit Cloud installs |

## Retrain the model

1. Open `Week3-Train-and-Save-Model-v2.ipynb` in Google Colab or Jupyter.
2. Choose **Run all**. The notebook saves a new `model.pkl`.
3. Upload that file to this repository, replacing the old one.

Keep the column names and their order (`temperature`, `is_weekend`, `precipitation`) the same in the notebook and in `app.py`, or the model will not accept the inputs.

## Run it locally

You need Python 3.10 or newer and an internet connection for the forecast.

```bash
git clone https://github.com/preetham13181/predicting_icecream_sales.git
cd predicting_icecream_sales
python -m pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Deploy on Streamlit Cloud

1. Put the files in a public GitHub repository, with `app.py` and `model.pkl` side by side.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create an app from the repository with `app.py` as the main file.
3. No secrets or API keys are required.

## Troubleshooting

| Problem | Fix |
|---|---|
| App is asleep | Click the button to wake it and wait about 30 seconds |
| "Could not get the forecast" | The weather service may be busy. Wait a minute and try again |
| Error loading `model.pkl` | Make sure it is next to `app.py`, and that `scikit-learn` is in `requirements.txt`. If it still fails, rerun the notebook and upload the new file |

## Built with

Streamlit, scikit-learn, pandas, requests, and the Open-Meteo weather API.
