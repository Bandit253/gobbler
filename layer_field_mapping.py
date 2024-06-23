import json
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,QMessageBox,
                                    QListWidget, QTableWidget, QTableWidgetItem,
                                    QPushButton, QFileDialog, QSpacerItem, QSizePolicy)
from qgis.core import QgsMessageLog, Qgis
import sys

class FieldMapper(QDialog):
    def __init__(self, src_lyr, dest_lyr, mappings, iface, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Mapper")
        self.resize(600, 400)
        self.src_lyr = src_lyr 
        self.dest_lyr = dest_lyr
        self.mapping = mappings
        self.iface = iface
        # Layouts
        main_layout = QVBoxLayout()
        list_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        # List Widgets
        self.layer1List = QListWidget()
        self.layer2List = QListWidget()
        # Buttons
        # self.loadLayersButton = QPushButton("Load Layers")
        self.addButton = QPushButton("Add Mapping")
        self.removeButton = QPushButton("Remove Mapping")
        self.saveMapping = QPushButton("Export Mapping")
        self.loadMapping = QPushButton("Import Mapping")
        # Table Widget
        self.mappingTable = QTableWidget(0, 2)
        self.mappingTable.setHorizontalHeaderLabels([f"src: {self.src_lyr.name()}", f"Dest: {self.dest_lyr.name()}"])

        self.exit_button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.exit_button_layout.addWidget(self.ok_button)
        self.exit_button_layout.addWidget(self.cancel_button)
        # Adding widgets to layouts
        list_layout.addWidget(self.layer1List)
        list_layout.addWidget(self.layer2List)
        # button_layout.addWidget(self.loadLayersButton)
        button_layout.addWidget(self.addButton)
        button_layout.addWidget(self.removeButton)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.saveMapping)
        button_layout.addWidget(self.loadMapping)
        list_layout.addLayout(button_layout)
        main_layout.addLayout(list_layout)
        main_layout.addWidget(self.mappingTable)
        main_layout.addLayout(self.exit_button_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals and slots
        # self.loadLayersButton.clicked.connect(self.load_layers)
        self.addButton.clicked.connect(self.add_mapping)
        self.removeButton.clicked.connect(self.remove_mapping)
        self.saveMapping.clicked.connect(self.save_field_mapping)
        self.loadMapping.clicked.connect(self.load_field_mapping)
        
        
    def load_layers(self):
        # Clear existing items
        self.layer1List.clear()
        self.layer2List.clear()

        srcflds = self.src_lyr.fields()
        for field in srcflds:
            self.layer1List.addItem(f"{field.name()}")
        destflds = self.dest_lyr.fields()
        for field in destflds:
            self.layer2List.addItem(f"{field.name()}")
        if self.mapping:
            # QgsMessageLog.logMessage(f"if self.mapping: {self.mapping}", "Gobbler", Qgis.Info)
            self.add_to_map_tab()
        return

    def add_to_map_tab(self):
        # QgsMessageLog.logMessage(f"add to mapping tab: {self.mapping}", "Gobbler", Qgis.Info)
        self.mappingTable.clearContents()
        self.mappingTable.setRowCount(0)
        rowcnt = 0
        for src, dest in self.mapping.items():
            # QgsMessageLog.logMessage(f"{rowcnt} = {src} : {dest}", "Gobbler", Qgis.Info)
            self.mappingTable.insertRow(rowcnt)
            self.mappingTable.setItem(rowcnt, 0, QTableWidgetItem(src))
            self.mappingTable.setItem(rowcnt, 1, QTableWidgetItem(dest))
            rowcnt += 1
        return

    def save_field_mapping(self):
        data = self.mapping
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_path, _ = file_dialog.getSaveFileName(None, "Save field mapping file", "", "JSON Files (*.json);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=4)              
                self.iface.messageBar().pushMessage("Info", f"File saved field mapping successfully at {file_path}", level=Qgis.Info)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to save file: {e}")
        return

    def load_field_mapping(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_path, _ = QFileDialog.getOpenFileName(None, "Open field mapping file", "", "JSON Files (*.json);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                # QMessageBox.information(None, f"Success {data}", f"File loaded successfully from {file_path}")
                self.iface.messageBar().pushMessage("Info",  f"Field mapping loaded successfully from {file_path}", level=Qgis.Info)
                self.mapping = data
                self.add_to_map_tab()
                return data
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to load file: {e}")
                return None

    
    def get_mappings(self):

        tab = self.mappingTable
        mappings = {}
        for row in range(0, tab.rowCount()):
            mappings[tab.item(row, 0).text()] = tab.item(row, 1).text()
        return mappings
            
    def add_mapping(self):
        # Get selected items
        if not self.layer1List.currentItem() or not self.layer1List.currentItem():
            return
        layer1_field = self.layer1List.currentItem().text()
        layer2_field = self.layer2List.currentItem().text()
        # Add to the table
        rowPosition = self.mappingTable.rowCount()
        self.mappingTable.insertRow(rowPosition)
        self.mappingTable.setItem(rowPosition, 0, QTableWidgetItem(layer1_field))
        self.mappingTable.setItem(rowPosition, 1, QTableWidgetItem(layer2_field))
        
    def remove_mapping(self):
        # Remove selected row
        currentRow = self.mappingTable.currentRow()
        self.mappingTable.removeRow(currentRow)
