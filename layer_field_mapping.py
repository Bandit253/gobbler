from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import (QAction, QDialog, QVBoxLayout, QHBoxLayout,
                                    QListWidget, QTableWidget, QTableWidgetItem,
                                    QPushButton, QApplication, QMainWindow)
from qgis.core import QgsMessageLog, Qgis
import sys

class FieldMapper(QDialog):
    def __init__(self, src_lyr, dest_lyr, mappings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Mapper")
        self.resize(600, 400)
        self.src_lyr = src_lyr 
        self.dest_lyr = dest_lyr
        self.mapping = mappings
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
        list_layout.addLayout(button_layout)
        main_layout.addLayout(list_layout)
        main_layout.addWidget(self.mappingTable)
        main_layout.addLayout(self.exit_button_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals and slots
        # self.loadLayersButton.clicked.connect(self.load_layers)
        self.addButton.clicked.connect(self.add_mapping)
        self.removeButton.clicked.connect(self.remove_mapping)
        
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
            rowcnt = 0
            for src, dest in self.mapping.items():
                QgsMessageLog.logMessage(f"{rowcnt} = {src} : {dest}", "Gobbler", Qgis.Info)
                self.mappingTable.insertRow(rowcnt)
                self.mappingTable.setItem(rowcnt, 0, QTableWidgetItem(src))
                self.mappingTable.setItem(rowcnt, 1, QTableWidgetItem(dest))
                rowcnt += 1

    
    def get_mappings(self):
        tab = self.mappingTable
        mappings = {}
        for row in range(0, tab.rowCount()):
            mappings[tab.item(row, 0).text()] = tab.item(row, 1).text()
            # QgsMessageLog.logMessage(f"row: {row}", "MM_Updater", Qgis.Info)
            # QgsMessageLog.logMessage(f"{tab.item(row, 0).text()}: {tab.item(row, 1).text()}", "MM_Updater", Qgis.Info)
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

# class FieldMapperPlugin:
#     def __init__(self, iface):
#         self.iface = iface
#         self.action = QAction("Field Mapper", self.iface.mainWindow())
#         self.iface.addPluginToMenu("Field Mapper", self.action)
#         self.action.triggered.connect(self.run)
#         self.dialog = None
        
#     def run(self):
#         if self.dialog is None:
#             self.dialog = FieldMapper(self.iface.mainWindow())
            
#         self.dialog.show()
        
#         self.dialog.raise_()
#         self.dialog.activateWindow()

# def classFactory(iface):
#     return FieldMapperPlugin(iface)
