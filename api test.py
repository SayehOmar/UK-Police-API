import requests
import csv


# Function to fetch stop and search data
def fetch_stop_and_search_data(force, date=None):
    url = f"https://data.police.uk/api/stops-force?force={force}"
    if date:
        url += f"&date={date}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "type",
            "involved_person",
            "datetime",
            "operation",
            "operation_name",
            "location",
            "latitude",
            "longitude",
            "street_id",
            "street_name",
            "gender",
            "age_range",
            "self_defined_ethnicity",
            "officer_defined_ethnicity",
            "legislation",
            "object_of_search",
            "outcome",
            "outcome_linked_to_object_of_search",
            "removal_of_more_than_outer_clothing",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in data:
            location = item.get("location", {})
            street = location.get("street") if location else {}

            writer.writerow(
                {
                    "type": item.get("type"),
                    "involved_person": item.get("involved_person"),
                    "datetime": item.get("datetime"),
                    "operation": item.get("operation"),
                    "operation_name": item.get("operation_name"),
                    "location": (
                        f"{location.get('latitude', '')}, {location.get('longitude', '')}"
                        if location
                        else ""
                    ),
                    "latitude": location.get("latitude", "") if location else "",
                    "longitude": location.get("longitude", "") if location else "",
                    "street_id": street.get("id", "") if street else "",
                    "street_name": street.get("name", "") if street else "",
                    "gender": item.get("gender", ""),
                    "age_range": item.get("age_range", ""),
                    "self_defined_ethnicity": item.get("self_defined_ethnicity", ""),
                    "officer_defined_ethnicity": item.get(
                        "officer_defined_ethnicity", ""
                    ),
                    "legislation": item.get("legislation", ""),
                    "object_of_search": item.get("object_of_search", ""),
                    "outcome": item.get("outcome", ""),
                    "outcome_linked_to_object_of_search": item.get(
                        "outcome_linked_to_object_of_search", ""
                    ),
                    "removal_of_more_than_outer_clothing": item.get(
                        "removal_of_more_than_outer_clothing", ""
                    ),
                }
            )


# Example usage
force_id = "suffolk"
date = "2024-01"
filename = "stop_and_search_data.csv"

# Fetch the data
data = fetch_stop_and_search_data(force_id, date)

# Save the data to CSV
save_to_csv(data, filename)

print(f"Data saved to {filename}")
