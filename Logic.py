import requests
import csv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os


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
        self.start_date = datetime.strptime(start_date, "%m/%Y")
        self.end_date = datetime.strptime(end_date, "%m/%Y")

        if self.start_date > self.end_date:
            raise ValueError("Start date must be earlier than end date.")

    def fetch_data(self):
        current_date = self.start_date
        all_data = []

        while current_date <= self.end_date:
            formatted_date = current_date.strftime("%Y-%m")
            url = f"https://data.police.uk/api/stops-force?date={formatted_date}&force={self.force}"

            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                all_data.extend(data)
                print(f"Fetched {len(data)} records for {formatted_date}.")
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data for {formatted_date}: {e}")

            # Increment by one month
            current_date += relativedelta(months=1)

        return all_data


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
        # Extract folder path from filename
        folder_path = os.path.dirname(self.filename)

        # Check if the folder exists; if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

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
