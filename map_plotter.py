import pandas as pd
import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
)
from qgis.PyQt.QtCore import QVariant


class MapPlotter:
    def __init__(self, layer_name="Stop and Search Data"):
        self.layer_name = layer_name

    def plot_data_from_csv(self, csv_path):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Load data from CSV
        df = pd.read_csv(csv_path)

        if df.empty:
            raise ValueError("CSV file is empty")

        # Create an in-memory point layer with EPSG:4326 CRS (WGS 84)
        layer = QgsVectorLayer("Point?crs=EPSG:4326", self.layer_name, "memory")

        # Check if the layer is valid
        if not layer.isValid():
            print(f"Layer {self.layer_name} is invalid!")
            return

        # Get the data provider for the layer
        provider = layer.dataProvider()

        # Add fields (attributes) to the layer
        provider.addAttributes(
            [
                QgsField("type", QVariant.String),
                QgsField("involved_person", QVariant.String),
                QgsField("datetime", QVariant.String),
                QgsField("operation", QVariant.String),
                QgsField("operation_name", QVariant.String),
                QgsField("street_name", QVariant.String),
                QgsField("gender", QVariant.String),
                QgsField("age_range", QVariant.String),
                QgsField("self_defined_ethnicity", QVariant.String),
                QgsField("officer_defined_ethnicity", QVariant.String),
                QgsField("legislation", QVariant.String),
                QgsField("object_of_search", QVariant.String),
                QgsField("outcome", QVariant.String),
                QgsField("outcome_linked", QVariant.String),
                QgsField("outer_clothing_removal", QVariant.String),
            ]
        )
        layer.updateFields()

        # Prepare the list of features (points) to be added to the layer
        features = []
        for _, row in df.iterrows():
            lat = row.get("latitude")
            lon = row.get("longitude")

            # Only add valid points with both latitude and longitude
            if pd.notna(lat) and pd.notna(lon):
                try:
                    lat, lon = float(lat), float(lon)
                    # Create a new feature
                    feature = QgsFeature()

                    # Set the geometry (point) for the feature
                    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))

                    # Set the attributes for the feature
                    feature.setAttributes(
                        [
                            row.get("type", ""),
                            row.get("involved_person", ""),
                            row.get("datetime", ""),
                            row.get("operation", ""),
                            row.get("operation_name", ""),
                            row.get("street_name", ""),
                            row.get("gender", ""),
                            row.get("age_range", ""),
                            row.get("self_defined_ethnicity", ""),
                            row.get("officer_defined_ethnicity", ""),
                            row.get("legislation", ""),
                            row.get("object_of_search", ""),
                            row.get("outcome", ""),
                            row.get("outcome_linked_to_object_of_search", ""),
                            row.get("outer_clothing_removal", ""),
                        ]
                    )

                    features.append(feature)
                except ValueError:
                    print(f"Skipping invalid coordinates: {lat}, {lon}")

        if features:
            # Add features to the layer
            provider.addFeatures(features)
            layer.updateExtents()

            # Add the layer to the project (QGIS map)
            QgsProject.instance().addMapLayer(layer)
            print(f"Layer '{self.layer_name}' added with {len(features)} points.")
        else:
            print("No valid features to add to the map.")
