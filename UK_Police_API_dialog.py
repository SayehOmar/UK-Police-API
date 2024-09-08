# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UK_Police_APIDialog
                                 A QGIS plugin
 This plugin connect Qgis to UK Police API
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-08-24
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Sayeh Omar 
        email                : sayehomar@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from .map_plotter import MapPlotter
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.gui import (
    QgsCheckableComboBox,
)
from qgis.PyQt import QtCore, QtGui, QtWidgets
from .Logic import PoliceDataFetcher, CSVDataSaver, convert_date_format


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "UK_Police_API_dialog_base.ui")
)


class UK_Police_APIDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(UK_Police_APIDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.force_id_map = {
            # "Select All": "Select All",
            "Avon and Somerset Constabulary": "avon-and-somerset",
            "Bedfordshire Police": "bedfordshire",
            "British Transport Police": "btp",
            "Cambridgeshire Constabulary": "cambridgeshire",
            "Cheshire Constabulary": "cheshire",
            "City of London Police": "city-of-london",
            "Cleveland Police": "cleveland",
            "Cumbria Constabulary": "cumbria",
            "Derbyshire Constabulary": "derbyshire",
            "Devon and Cornwall Police": "devon-and-cornwall",
            "Dorset Police": "dorset",
            "Durham Constabulary": "durham",
            "Dyfed-Powys Police": "dyfed-powys",
            "Essex Police": "essex",
            "Gloucestershire Constabulary": "gloucestershire",
            "Greater Manchester Police": "greater-manchester",
            "Gwent Police": "gwent",
            "Hampshire Constabulary": "hampshire",
            "Hertfordshire Constabulary": "hertfordshire",
            "Humberside Police": "humberside",
            "Kent Police": "kent",
            "Lancashire Constabulary": "lancashire",
            "Leicestershire Police": "leicestershire",
            "Lincolnshire Police": "lincolnshire",
            "Merseyside Police": "merseyside",
            "Metropolitan Police Service": "metropolitan",
            "Norfolk Constabulary": "norfolk",
            "North Wales Police": "north-wales",
            "North Yorkshire Police": "north-yorkshire",
            "Northamptonshire Police": "northamptonshire",
            "Northumbria Police": "northumbria",
            "Nottinghamshire Police": "nottinghamshire",
            "Police Service of Northern Ireland": "northern-ireland",
            "South Wales Police": "south-wales",
            "South Yorkshire Police": "south-yorkshire",
            "Staffordshire Police": "staffordshire",
            "Suffolk Constabulary": "suffolk",
            "Surrey Police": "surrey",
            "Sussex Police": "sussex",
            "Thames Valley Police": "thames-valley",
            "Warwickshire Police": "warwickshire",
            "West Mercia Police": "west-mercia",
            "West Midlands Police": "west-midlands",
            "West Yorkshire Police": "west-yorkshire",
            "Wiltshire Police": "wiltshire",
        }

        # Ensure that the combo box is a QgsCheckableComboBox and set up its items
        self.setup_combo_box()

        # Connect the QPushButton named BrowserBtn to the method
        self.BrowserBtn.clicked.connect(self.open_file_dialog)

        # Connect the QPushButton named FetchRequest to the method
        self.FetchRequest.clicked.connect(self.on_fetch_request_clicked)

    def handle_selection_change(self, index):
        """Handle changes in the combobox selection."""
        combo_box = self.findChild(QgsCheckableComboBox, "mComboBox")
        if combo_box:
            # Get the text of the selected item
            selected_text = combo_box.itemText(index)

            # Check if 'Select All' is selected
            if selected_text == "Select All":
                # Check or uncheck all items based on the current state of 'Select All'
                check_all = not combo_box.isItemChecked(index)
                for i in range(combo_box.count()):
                    if i != index:  # Skip 'Select All' item itself
                        combo_box.setItemChecked(i, check_all)
                combo_box.setItemChecked(index, check_all)  # Update 'Select All' state

    def setup_combo_box(self):
        """Initialize the QgsCheckableComboBox with force names and the 'Select All' option."""
        combo_box = self.findChild(QgsCheckableComboBox, "mComboBox")
        if combo_box:
            # Add 'Select All' option
            combo_box.addItem("Select All", QtCore.Qt.Unchecked)

            # Add items to the combobox with check states
            for force_name in self.force_id_map.keys():
                combo_box.addItem(force_name, QtCore.Qt.Unchecked)

            # Connect the currentIndexChanged signal to handle the 'Select All' logic
            combo_box.currentIndexChanged.connect(self.handle_selection_change)
        else:
            raise Exception("QgsCheckableComboBox widget 'mComboBox' not found.")

    def get_selected_forces(self):
        """Fetch the selected forces from the QgsCheckableComboBox."""
        combo_box = self.findChild(QgsCheckableComboBox, "mComboBox")
        if combo_box:
            selected_forces = combo_box.checkedItems()  # Get the selected display names
            selected_ids = [
                self.force_id_map.get(force)
                for force in selected_forces
                if force in self.force_id_map
            ]
            return selected_ids
        else:
            raise Exception("QgsCheckableComboBox widget 'mComboBox' not found.")

    def get_end_date(self):
        """Fetch the date from the QDateEdit widget."""
        end_date_widget = self.findChild(QtWidgets.QDateEdit, "EndDate")
        if end_date_widget:
            # Retrieve the selected date from the widget
            selected_date = end_date_widget.date()
            # Convert to string if needed
            return selected_date.toString("MM/yyyy")  # Format as YYYY-MM-DD
        else:
            raise Exception("QDateEdit widget 'EndDate' not found.")

    def get_start_date(self):
        """Fetch the date from the QDateEdit widget."""
        start_date_widget = self.findChild(QtWidgets.QDateEdit, "StartDate")
        if start_date_widget:
            # Retrieve the selected date from the widget
            selected_date = start_date_widget.date()
            # Convert to string if needed
            return selected_date.toString("MM/yyyy")  # Format as YYYY-MM-DD
        else:
            raise Exception("QDateEdit widget 'StartDate' not found.")

    def on_fetch_request_clicked(self):
        """Slot method executed when FetchRequest button is clicked."""
        start_date = self.get_start_date()
        print(f"start date: {start_date}")
        ############################
        end_date = self.get_end_date()
        print(f"End date: {end_date}")
        ############################
        selected_forces = self.get_selected_forces()
        print(f"Selected forces: {selected_forces}")

        # Here you can add the logic to fetch data, send requests, or perform any other operation
        # For example, you can integrate the data fetching logic here.

    # Example function to handle the fetch request
    def fetch_data_and_save(self):
        start_date = self.startDateEdit.text()  # Assuming 'MM/YYYY'
        end_date = self.endDateEdit.text()  # Assuming 'MM/YYYY'

        # Convert dates to the format needed by the API
        formatted_start_date = convert_date_format(start_date)
        formatted_end_date = convert_date_format(end_date)

        # Fetch the data
        fetcher = PoliceDataFetcher(
            self.selected_force, formatted_start_date, formatted_end_date
        )
        try:
            data = fetcher.fetch_data()

            # Save the data to CSV
            saver = CSVDataSaver(self.folderPathEdit.text())
            saver.save_to_csv(data)

            print(f"Data saved to {self.folderPathEdit.text()}")
        except Exception as e:
            print(e)
            # Handle errors as needed

    def open_file_dialog(self):
        """Open a file dialog to select a folder and set it in the QLineEdit."""
        options = QtWidgets.QFileDialog.Options()
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            options=options,
        )
        if folder_path:
            # Set the selected folder path to the QLineEdit named FolderPath
            self.FolderPath.setText(folder_path)

    def on_fetch_request_clicked(self):
        """Slot method executed when FetchRequest button is clicked."""
        # Get selected dates and forces
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        selected_forces = self.get_selected_forces()
        save_path = self.FolderPath.text()  # Path where to save the CSV

        if not selected_forces:
            QtWidgets.QMessageBox.warning(
                self,
                "No Forces Selected",
                "Please select at least one police force.",
            )
            return

        if not save_path:
            QtWidgets.QMessageBox.warning(
                self,
                "No Save Path",
                "Please specify a folder path where to save the CSV file.",
            )
            return

        # Iterate through selected forces and fetch data
        for force in selected_forces:
            # Create fetcher instance
            fetcher = PoliceDataFetcher(force, start_date, end_date)
            try:
                # Fetch data from API
                data = fetcher.fetch_data()

                if data is None:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "No Data",
                        f"No data available for {force}.",
                    )
                    continue  # Skip to the next force

                # Construct filename
                filename = os.path.join(save_path, f"{force}_stop_and_search_data.csv")

                # Create saver instance
                saver = CSVDataSaver(filename)

                # Save data to CSV
                saver.save_to_csv(data)

                # Notify user of success
                print(f"Data for {force} saved to {filename}")

                # Plot data from CSV
                try:
                    map_plotter = MapPlotter(f"Police Stop and Search Data - {force}")
                    map_plotter.plot_data_from_csv(filename)
                    print(f"Data from {filename} plotted successfully.")
                except Exception as e:
                    print(f"Failed to plot data from CSV1: {e}")
                    QtWidgets.QMessageBox.critical(
                        self,
                        "Plotting Error",
                        f"Failed to plot data from CSV2: {e}",
                    )

            except Exception as e:
                # Notify user of any errors during fetching or saving
                print(f"Failed to fetch or save data for {force}: {e}")
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to fetch or save data for {force}: {e}",
                )


# Example usage
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = UK_Police_APIDialog()
    dialog.show()
    app.exec_()
