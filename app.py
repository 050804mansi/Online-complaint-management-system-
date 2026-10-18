"""Rent Insights: a fresh Flask implementation for exploring rental estimates."""

from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request
from urllib.parse import quote
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "rent_listings.csv"
NUMERIC = ["area", "beds", "bathrooms", "balconies"]
CATEGORICAL = ["city", "locality", "furnishing"]
FEATURES = NUMERIC + CATEGORICAL

app = Flask(__name__)


def load_listings():
    data = pd.read_csv(DATA_PATH)
    needed = FEATURES + ["rent"]
    data = data[needed].copy()
    for column in NUMERIC + ["rent"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=needed)
    data = data[(data["rent"] > 0) & (data["area"] > 0) & (data["beds"] > 0)]
    for column in CATEGORICAL:
        data[column] = data[column].astype(str).str.strip()
    return data


listings = load_listings()
encoder = ColumnTransformer(
    [("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)],
    remainder="passthrough",
)
model = Pipeline(
    [
        ("encode", encoder),
        ("forest", RandomForestRegressor(
            n_estimators=140, min_samples_leaf=2, random_state=42, n_jobs=-1
        )),
    ]
)
model.fit(listings[FEATURES], listings["rent"])

CITY_LOCALITIES = {
    city: sorted(group["locality"].dropna().unique().tolist())
    for city, group in listings.groupby("city")
}
CITIES = sorted(CITY_LOCALITIES)
FURNISHINGS = sorted(listings["furnishing"].dropna().unique().tolist())
HOME_STATS = {
    "dataset_count": len(listings),
    "city_count": len(CITIES),
    "locality_count": sum(len(items) for items in CITY_LOCALITIES.values()),
}


@app.get("/")
def home():
    return render_template(
        "index.html", cities=CITIES, localities=CITY_LOCALITIES,
        furnishings=FURNISHINGS, **HOME_STATS,
    )


@app.get("/api/localities/<path:city>")
def localities(city):
    return jsonify(CITY_LOCALITIES.get(city, []))


@app.post("/estimate")
def estimate():
    try:
        city = request.form["city"]
        locality = request.form["locality"]
        furnishing = request.form["furnishing"]
        values = {
            "area": float(request.form["area"]),
            "beds": int(request.form["beds"]),
            "bathrooms": int(request.form["bathrooms"]),
            "balconies": int(request.form["balconies"]),
            "city": city,
            "locality": locality,
            "furnishing": furnishing,
        }
        if values["area"] <= 0 or values["beds"] <= 0 or values["bathrooms"] <= 0 or values["balconies"] < 0:
            raise ValueError("Enter a positive area and room count, and a non-negative balcony count.")
        if city not in CITY_LOCALITIES or locality not in CITY_LOCALITIES[city]:
            raise ValueError("Choose a city and locality from the available options.")
        if furnishing not in FURNISHINGS:
            raise ValueError("Choose a furnishing option from the list.")

        estimate_input = pd.DataFrame([values], columns=FEATURES)
        predicted = max(0, round(float(model.predict(estimate_input)[0])))
        comparison = listings[(listings["city"] == city) & (listings["beds"] == values["beds"])]
        median = round(float(comparison["rent"].median())) if not comparison.empty else round(float(listings["rent"].median()))
        lower = round(float(comparison["rent"].quantile(0.25))) if not comparison.empty else median
        upper = round(float(comparison["rent"].quantile(0.75))) if not comparison.empty else median
        rent_per_sqft = round(float((comparison["rent"] / comparison["area"]).median()), 1) if not comparison.empty else 0
        difference = round((predicted - median) / median * 100) if median else 0
        label = "Below typical" if difference < -15 else "Above typical" if difference > 15 else "Near typical"
        bhk_market = []
        for bedrooms in range(1, 6):
            segment = listings[(listings["city"] == city) & (listings["beds"] == bedrooms)]
            if not segment.empty:
                bhk_market.append({
                    "beds": bedrooms,
                    "median": round(float(segment["rent"].median())),
                    "selected": bedrooms == values["beds"],
                })
        highest_bhk_median = max((item["median"] for item in bhk_market), default=1)
        for item in bhk_market:
            item["width"] = max(5, round(item["median"] / highest_bhk_median * 100))
        map_url = "https://www.google.com/maps/search/?api=1&query=" + quote(f"{locality}, {city}")
        map_embed_url = "https://maps.google.com/maps?q=" + quote(f"{locality}, {city}") + "&output=embed"
        return render_template(
            "result.html", estimate=predicted, median=median, difference=difference,
            label=label, values=values, lower=lower, upper=upper,
            rent_per_sqft=rent_per_sqft, sample_count=len(comparison),
            bhk_market=bhk_market, map_url=map_url, map_embed_url=map_embed_url,
        )
    except (KeyError, TypeError, ValueError) as error:
        return render_template(
            "index.html", cities=CITIES, localities=CITY_LOCALITIES,
            furnishings=FURNISHINGS, error=str(error), **HOME_STATS,
        ), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
