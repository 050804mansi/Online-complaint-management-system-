"""Generate the demo rental listings used by Rent Insights.

All rows are simulated for this portfolio demo. They are not scraped listings
and should not be used as current market quotes.
"""

import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "rent_listings.csv"
RNG = random.Random(53245)

# City-level rent multipliers and original demo locality labels.
CITIES = {
    "Mumbai": (1.65, ["Harbor View", "Palm Grove", "Cedar Park", "Lakefront", "Green Avenue", "Sunrise Enclave"]),
    "Delhi": (1.18, ["Rosewood", "Metro Heights", "Shanti Vihar", "Civic Greens", "Riverbend", "Pearl Residency"]),
    "Bengaluru": (1.25, ["Tech Park West", "Orchid Lane", "Mango Grove", "Skyline Layout", "Maple Cross", "Garden Square"]),
    "Hyderabad": (0.93, ["Charminar Gardens", "Pearl City", "Cloud Nine", "Olive District", "Meadow Walk", "Bluebell Enclave"]),
    "Pune": (0.92, ["University Circle", "Silver Springs", "Hillview", "Aster Park", "Central Grove", "Crescent Bay"]),
    "Chennai": (0.90, ["Marina Vista", "Coral Gardens", "Temple Town", "Rain Tree Park", "Coastal Enclave", "Jasmine Square"]),
    "Kolkata": (0.72, ["Victoria Greens", "Lake Gardens", "Banyan Court", "Eastbank", "Orchid Residency", "Crescent Park"]),
    "Ahmedabad": (0.70, ["Sabarmati View", "Lotus Enclave", "Heritage Square", "Riverstone", "Amber Park", "Clover Court"]),
    "Jaipur": (0.65, ["Pink City Heights", "Aravali View", "Moti Enclave", "Royal Gardens", "Amber Residency", "Desert Bloom"]),
    "Lucknow": (0.60, ["Gomti Greens", "Nawabi Enclave", "Hazratganj Heights", "Rose Garden", "Crown Residency", "Cedar Court"]),
    "Indore": (0.57, ["Palasia Park", "Central Avenue", "Lotus Lake", "Vijay Nagar Greens", "Maple Residency", "Silver Oak"]),
    "Bhopal": (0.52, ["Lakeview Enclave", "Van Vihar Greens", "Saffron Square", "Upper Lake Park", "Cedar Residency", "Sunset Court"]),
}

FURNISHING = [("Unfurnished", 1.0), ("Semi-Furnished", 1.13), ("Furnished", 1.28)]
HOUSE_TYPES = {1: "1 BHK Apartment", 2: "2 BHK Apartment", 3: "3 BHK Apartment", 4: "4 BHK Apartment", 5: "Independent House"}


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["house_type", "locality", "city", "area", "beds", "bathrooms", "balconies", "furnishing", "area_rate", "rent"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for city, (city_factor, localities) in CITIES.items():
            for locality_index, locality in enumerate(localities):
                locality_factor = 0.84 + locality_index * 0.065
                for _ in range(72):
                    beds = RNG.choices([1, 2, 3, 4, 5], weights=[18, 38, 27, 12, 5])[0]
                    area = max(350, int(RNG.gauss(430 + beds * 390, 100 + beds * 42) / 10) * 10)
                    bathrooms = max(1, min(5, beds + RNG.choice([-1, 0, 0, 0, 1])))
                    balconies = max(0, min(4, round(beds * 0.55 + RNG.choice([-1, 0, 0, 1]))))
                    furnishing, furnishing_factor = RNG.choice(FURNISHING)
                    base_rate = 18.5 * city_factor * locality_factor * furnishing_factor
                    area_rate = round(base_rate * RNG.uniform(0.78, 1.24), 1)
                    size_factor = 0.83 + 0.17 * (area / (430 + beds * 390))
                    rent = max(4500, int(area * area_rate * size_factor / 100) * 100)
                    writer.writerow({
                        "house_type": HOUSE_TYPES[beds], "locality": locality, "city": city,
                        "area": area, "beds": beds, "bathrooms": bathrooms,
                        "balconies": balconies, "furnishing": furnishing,
                        "area_rate": area_rate, "rent": rent,
                    })
    print(f"Wrote 5,184 simulated rows to {OUTPUT}")


if __name__ == "__main__":
    main()
