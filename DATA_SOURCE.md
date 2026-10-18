# Data source and dataset notes

`data/rent_listings.csv` is a deterministic, synthetic demo dataset generated for Rent Insights by `scripts/generate_dataset.py` with Python's standard library. It contains 5,184 simulated rows across 12 Indian city labels and 72 locality labels. Locality names and rents are generated for demonstration; they do not represent verified addresses, active listings, or current market prices.

On Windows, regenerate the CSV from this folder with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\generate_dataset.ps1
```

The CSV and generator are original project demo materials. Keep the synthetic-data description with the dataset if you redistribute it so readers do not mistake generated values for real rental offers.

