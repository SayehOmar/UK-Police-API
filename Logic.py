import requests
import csv
from datetime import datetime


def convert_date_format(date_str):
    try:
        # Convert 'MM/YYYY' to 'YYYY-MM'
        date_obj = datetime.strptime(date_str, "%m/%Y")
        return date_obj.strftime("%Y-%m")
    except ValueError:
        raise ValueError(f"Incorrect date format: {date_str}. Expected MM/YYYY.")


class PoliceDataFetcher:
    def __init__(self, force, start_date=None, end_date=None):
        self.force = force
        self.start_date = start_date
        self.end_date = end_date
        self.url = f"https://data.police.uk/api/stops-force?force={self.force}"
        if self.start_date:
            self.url += f"&start_date={self.start_date}"
        if self.end_date:
            self.url += f"&end_date={self.end_date}"

    def fetch_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 502:
                # Handle 502 Bad Gateway error
                raise Exception(f"HTTP error occurred: {http_err}")
            else:
                raise Exception(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise Exception(f"Other error occurred: {err}")


class CSVDataSaver:
    def __init__(self, filename):
        self.filename = filename
        self.fieldnames = [
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

    def save_to_csv(self, data):
        with open(self.filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
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
                        "self_defined_ethnicity": item.get(
                            "self_defined_ethnicity", ""
                        ),
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


"""# Main script
if __name__ == "__main__":
    # Define parameters
    force_id = "suffolk"
    date = "2022-01"
    filename = "stop_and_search_data.csv"

    # Fetch the data
    fetcher = PoliceDataFetcher(force_id, date)
    data = fetcher.fetch_data()

    # Save the data to CSV
    saver = CSVDataSaver(filename)
    saver.save_to_csv(data)

    print(f"Data saved to {filename}")
"""
