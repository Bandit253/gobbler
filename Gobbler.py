# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Gobbler
                                 A QGIS plugin
 Multi-attribute copy tool
 
                              -------------------
        begin                : 2024-06-16
        git sha              : $Format:%H$
        copyright            : (C) 2024 by OrataMedia
        email                : pots253@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QColor, QFont
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QTableWidgetItem, QDialog, QMenu
from qgis.gui import QgsMapToolPan

from qgis.core import QgsMessageLog, QgsProject, QgsWkbTypes, Qgis, QgsFeature
# Initialize Qt resources from file resources.py
from .resources import *
import os.path
import datetime
import json
# Import the code for the DockWidget
from .Gobbler_dockwidget import GobblerDockWidget
from .layer_field_mapping import FieldMapper
from .layer_selection_dialog import LayerSelectionDialog
from .identifier import IdentifyTool


def loggingtime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

src_button_css = """
            QPushButton {
                background-color: #20ff0000; /* #f0f0f0;  light gray background */
                border: 1px solid #bfbfbf; /* gray border */
                border-radius: 3px;
                padding: 5px;
                color: black;
                font: bold 14px;
            }
            QPushButton:hover {
                background-color: #ff6666; /* slightly darker gray when hovered */
            }
            QPushButton:pressed {
                background-color: #d9d9d9; /* darker gray when pressed */
            }
        """
dest_button_css = """
            QPushButton {
                background-color: #2000ff00; /* #f0f0f0;  light gray background */
                border: 1px solid #bfbfbf; /* gray border */
                border-radius: 3px;
                padding: 5px;
                color: black;
                font: bold 14px;
            }
            QPushButton:hover {
                background-color: #66ff66; /* slightly darker gray when hovered */
            }
            QPushButton:pressed {
                background-color: #d9d9d9; /* darker gray when pressed */
            }
        """
copy_button_css = """
            QPushButton {
                border: none;
                height: 30px;
                color: black;
                font: bold 14px;
            }
            QPushButton {
                background: qlineargradient(
                    spread: pad,
                    x1: 0, y1: 0.5, x2: 1, y2: 0.5,
                    stop: 0 #20ff0000,
                    stop: 1 #2000ff00
                );
            }
            QPushButton:hover {
                background: qlineargradient(
                    spread: pad,
                    x1: 0, y1: 0.5, x2: 1, y2: 0.5,
                    stop: 0 #ff6666,
                    stop: 1 #66ff66
                    
                );color: white;
            }
        """



class Gobbler:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.src_lyr = None
        self.src_selected_id = None
        self.dest_lyr = None
        self.dest_selected_id = None
        self.field_mapping = None
        
        self.src_colour = QColor( 255, 0, 0, 32)
        self.dest_colour = QColor( 0, 255, 0, 32)
        
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', f'Gobbler_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Gobbler')
        self.toolbar = self.iface.addToolBar(u'Gobbler')
        self.toolbar.setObjectName(u'Gobbler')

        self.pluginIsActive = False
        self.dockwidget = None
        
        # Context menu
        self.menu = None
        self.src_action = None
        self.dest_action = None
        self.copy_action = None


    def tr(self, message):
        return QCoreApplication.translate('Gobbler', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/Gobbler/icon.png'
        self.add_action(icon_path, text=self.tr(u'Gobbler'), callback=self.run, parent=self.iface.mainWindow())
        
        # context menu
        self.src_action = QAction(QIcon(":/plugins/Gobbler/icon_source.png"), "Select source", self.iface.mainWindow())
        self.src_action.triggered.connect(self.select_source_feature)
        self.dest_action = QAction(QIcon(":/plugins/Gobbler/icon_destination.png"), "Select destination", self.iface.mainWindow())
        self.dest_action.triggered.connect(self.select_destination_feature)
        self.copy_action = QAction(QIcon(":/plugins/Gobbler/icon_copy.png"), ">>> Copy >>>", self.iface.mainWindow())
        self.copy_action.triggered.connect(self.copy_attributes)
        
        self.iface.mapCanvas().setContextMenuPolicy(Qt.CustomContextMenu)
        self.iface.mapCanvas().customContextMenuRequested.connect(self.show_context_menu)


    def onClosePlugin(self):
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False

    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.tr(u'&Gobbler'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar
        # context menu
        self.iface.mapCanvas().customContextMenuRequested.disconnect(self.show_context_menu)


    def get_active_layer(self):
        lyrs = self.iface.layerTreeView().selectedLayers()
        if len(lyrs) == 1:
            lyr = lyrs[0]
            if lyr.geometryType() == QgsWkbTypes.LineGeometry:
                QgsMessageLog.logMessage(f"{loggingtime()} : Selected Layer : {lyr.name()}", "OSM_Updater", Qgis.Info)
                return lyr
            else:
                QgsMessageLog.logMessage(f"{loggingtime()} : Not a line layer {lyr.name()}", "OSM_Updater", Qgis.Info)
                QMessageBox.information(None, f"Not a line layer {lyr.name()}")
        elif len(lyrs) == 0:
            QgsMessageLog.logMessage(f"{loggingtime()} : No Layers selected", "OSM_Updater", Qgis.Info)
            QMessageBox.information(None, "DEBUG:", f"No Layers selected")
        else:
            QgsMessageLog.logMessage(f"{loggingtime()} : More than one Layer selected", "OSM_Updater", Qgis.Info)
            for lyr in lyrs:
                QgsMessageLog.logMessage(f"layer: {lyr.name()}", "OSM_Updater", Qgis.Info)
        return None

    def setup_id_table(self):
            self.dockwidget.tableWidget.setColumnCount(4)
            self.dockwidget.tableWidget.setHorizontalHeaderLabels(["SRC: Field Name", "SRC: Attribute","DEST: Field Name", "DEST: Attribute"])

    def feature_callback(self, feature, source=True):
        if feature is not None and isinstance(feature, QgsFeature):
            if self.dockwidget.tableWidget.columnCount() != 4:
                self.setup_id_table()
            # feature_type = "source" if source else "destination"
            # # QgsMessageLog.logMessage(f"You clicked on {feature_type} feature {feature.id()}", "Gobbler", Qgis.Info)
            selected_id_attr = 'src_selected_id' if source else 'dest_selected_id'
            setattr(self, selected_id_attr, feature.id())
            fields = self.get_source_fields() if source else self.get_destination_fields()
            self.dockwidget.tableWidget.setRowCount(len(fields))
            column_offset = 0 if source else 2
            color = self.src_colour if source else self.dest_colour
            rowcnt = 0
            for srcfld, destfld in self.field_mapping.items():
                field_item = QTableWidgetItem(srcfld if source else destfld)
                attribute_item = QTableWidgetItem(str(feature[srcfld if source else destfld]))
                self.dockwidget.tableWidget.setItem(rowcnt, column_offset, field_item)
                self.dockwidget.tableWidget.setItem(rowcnt, column_offset + 1, attribute_item)
                rowcnt += 1
            self.change_column_color(self.dockwidget.tableWidget, column_offset, color)
            self.change_column_color(self.dockwidget.tableWidget, column_offset + 1, color)
                    
            self.change_column_bold(self.dockwidget.tableWidget, column_offset)
            self.change_column_noteditable(self.dockwidget.tableWidget, column_offset)
            if not source:
                self.change_column_noteditable(self.dockwidget.tableWidget, column_offset +1)

            self.canvas.unsetMapTool(self.feature_identifier)
            self.dockwidget.tabWidget.setCurrentIndex(0)

    def src_callback(self, feature):
        self.feature_callback(feature, source=True)

    def dest_callback(self, feature):
        self.feature_callback(feature, source=False)

    def show_context_menu(self, point):
        self.menu = QMenu()
        # self.menu.addAction(self.pan_action)
        self.menu.addAction(self.src_action)
        self.menu.addAction(self.dest_action)
        self.menu.addAction(self.copy_action)
        self.menu.exec_(self.canvas.mapToGlobal(point))

    def activate_pan_tool(self):
        pan_tool = QgsMapToolPan(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(pan_tool)

    def open_fld_mapper(self):
        mappings = self.retrieve_variable("field_mapping")
        if mappings:
            dialog = FieldMapper(self.src_lyr, self.dest_lyr, json.loads(mappings), self.iface)
        else:
            dialog = FieldMapper(self.src_lyr, self.dest_lyr, None, self.iface)
        dialog.load_layers()
        if dialog.exec_() == QDialog.Accepted:
            flds = dialog.get_mappings()
            # QgsMessageLog.logMessage(f"mappings : {flds}", "Gobbler", Qgis.Info)
            self.save_variable("field_mapping", json.dumps(flds))
            self.field_mapping = flds
            self.dockwidget.tableWidget.clearContents()
            self.dockwidget.tableWidget.setRowCount(0)
            self.populate_field_table()
            

    def populate_field_table(self):
        self.dockwidget.tab_field_map.clearContents()
        self.dockwidget.tab_field_map.setRowCount(0)
        # numb_fields = len(self.get_source_fields())
        # QgsMessageLog.logMessage(f"mappings : number fields => {numb_fields}", "Gobbler", Qgis.Info)
        self.dockwidget.tab_field_map.setColumnCount(2)
        # self.dockwidget.tab_field_map.setRowCount(numb_fields)
        self.dockwidget.tab_field_map.setHorizontalHeaderLabels([f"src: {self.src_lyr.name()}", f"Dest: {self.dest_lyr.name()}"])
        rowcnt = 0
        for srcfld, destfld in self.field_mapping.items():
            # QgsMessageLog.logMessage(f"mappings : srcfld, destfld => {srcfld}, {destfld}", "Gobbler", Qgis.Info)
            self.dockwidget.tab_field_map.insertRow(rowcnt)
            self.dockwidget.tab_field_map.setItem(rowcnt, 0, QTableWidgetItem(srcfld))
            self.dockwidget.tab_field_map.setItem(rowcnt, 1, QTableWidgetItem(destfld))      
            rowcnt += 1      
        self.change_column_color(self.dockwidget.tab_field_map, 0, self.src_colour)
        self.change_column_color(self.dockwidget.tab_field_map, 1, self.dest_colour) 
        self.change_column_noteditable(self.dockwidget.tab_field_map, 0)
        self.change_column_noteditable(self.dockwidget.tab_field_map, 1)

    
    def get_source_fields(self):
        return list(self.field_mapping.keys())
    
    def get_destination_fields(self):
        # QgsMessageLog.logMessage(f"dict filds : {type(self.field_mapping)}", "Gobbler", Qgis.Info)
        return list(self.field_mapping.values())

    def start_select(self):
        self.canvas.setMapTool(self.feature_identifier)
        
    def select_destination_feature(self):
        lyr = self.dest_lyr
        self.iface.messageBar().pushMessage("Info", f"Destination Layer: {lyr.name()}", level=Qgis.Info)
        # QgsMessageLog.logMessage(f"Destination Layer: {lyr.name()}", "Gobbler", Qgis.Info)
        self.feature_identifier = IdentifyTool(self.canvas, lyr, False)
        self.feature_identifier.setLayer(lyr)
        self.feature_identifier.featureIdentified.connect(self.dest_callback)
        self.canvas.setMapTool(self.feature_identifier)

    def select_source_feature(self):
        lyr = self.src_lyr
        # QgsMessageLog.logMessage(f"Source Layer: {lyr.name()}", "Gobbler", Qgis.Info)
        self.iface.messageBar().pushMessage("Info", f"Source Layer: {lyr.name()}", level=Qgis.Info)
        self.feature_identifier = IdentifyTool(self.canvas, lyr, True)
        self.feature_identifier.setLayer(lyr)
        self.feature_identifier.featureIdentified.connect(self.src_callback)

        self.canvas.setMapTool(self.feature_identifier)
        
    def show_layer_selection_dialog(self):
            dialog = LayerSelectionDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.src_lyr = dialog.get_source_layer()
                self.dest_lyr = dialog.get_destination_layer()
                source_layer_name = self.src_lyr.name()
                destination_layer_name = self.dest_lyr.name()
                self.save_variable("source_layer", source_layer_name)
                self.save_variable("destination_layer", destination_layer_name)
                self.iface.messageBar().pushMessage("Info", f"Source Layer: {source_layer_name}, Destination Layer: {destination_layer_name}", level=Qgis.Info)
                # 
                # QgsMessageLog.logMessage(f"Source Layer: {source_layer_name}", "Gobbler", Qgis.Info)
                # QgsMessageLog.logMessage(f"Destination Layer: {destination_layer_name}", "Gobbler", Qgis.Info)
                self.dockwidget.txt_src.setText(source_layer_name)
                self.dockwidget.txt_dest.setText(destination_layer_name)
    
    def save_variable(self, variable, value):
        proj = QgsProject.instance()
        proj.writeEntry("myplugin", variable, value)
        self.iface.messageBar().pushMessage("Info", f"{variable} saved to project", level=Qgis.Info)

    def retrieve_variable(self, variable):
        proj = QgsProject.instance()
        my_value, type_conversion_ok = proj.readEntry("myplugin", variable, None)
        self.iface.messageBar().pushMessage("Info", f"{variable}: {my_value}", level=Qgis.Info)
        return my_value
    
    def copy_attributes(self):
        if not self.src_selected_id or not self.dest_selected_id:
            return
        self.dest_lyr.startEditing()
        target_feature = self.dest_lyr.getFeature(self.dest_selected_id)
        
        for row in range(self.dockwidget.tableWidget.rowCount()):
            dest_fld = self.dockwidget.tableWidget.item(row, 2).text()
            dest_value = self.dockwidget.tableWidget.item(row, 1).text()
            # QgsMessageLog.logMessage(f"dest : {dest_fld} : {dest_value}", "Gobbler", Qgis.Info)
            target_feature.setAttribute(dest_fld, dest_value)

        self.dest_lyr.updateFeature(target_feature)
        self.dest_lyr.commitChanges()
        saved_feature = self.dest_lyr.getFeature(self.dest_selected_id)
        self.iface.messageBar().pushMessage("Info", f"{self.dest_selected_id} updated", level=Qgis.Info)
        self.feature_callback(saved_feature, False)

    def change_column_color(self, table, column_index, color):
        for row in range(table.rowCount()):
            item = table.item(row, column_index)
            if item:
                item.setBackground(color)
    
    def change_column_bold(self, table, column_index):
        bold_font = QFont()
        bold_font.setBold(True)
        for row in range(table.rowCount()):
            item = table.item(row, column_index)
            if item:
                item.setFont(bold_font)
    
    def change_column_noteditable(self, table, column_index):
        
        for row in range(table.rowCount()):
            item = table.item(row, column_index)
            if item:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    
    def run(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True
            if self.dockwidget == None:
                self.dockwidget = GobblerDockWidget()             
            layers = QgsProject.instance().mapLayers().values()
            src_lyr = self.retrieve_variable("source_layer")
            if src_lyr:
                layer = next((layer for layer in layers if layer.name() == src_lyr), None)
                self.src_lyr = layer
                self.dockwidget.txt_src.setText(src_lyr)
            
            dest_lyr = self.retrieve_variable("destination_layer")
            if src_lyr:
                layer = next((layer for layer in layers if layer.name() == dest_lyr), None)
                self.dest_lyr = layer
                self.dockwidget.txt_dest.setText(dest_lyr)  
            if self.src_lyr is None:
                self.show_layer_selection_dialog()
                self.dockwidget.tabWidget.setCurrentIndex(0)
            fldmapping = self.retrieve_variable("field_mapping")
            if fldmapping:
                self.field_mapping = json.loads(fldmapping)
            else:
                self.open_fld_mapper()
            self.populate_field_table()
            
            self.dockwidget.btn_copy.setStyleSheet(copy_button_css) 
            self.dockwidget.btn_copy.clicked.connect(self.copy_attributes)
            self.dockwidget.btn_dest.clicked.connect(self.select_destination_feature)
            self.dockwidget.btn_src.clicked.connect(self.select_source_feature)
            
            self.dockwidget.btn_dest.setStyleSheet(dest_button_css) 
            self.dockwidget.btn_src.setStyleSheet(src_button_css) 
            
            self.dockwidget.btn_mapfields.clicked.connect(self.open_fld_mapper)
            self.dockwidget.btn_layers.clicked.connect(self.show_layer_selection_dialog)
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.iface.addTabifiedDockWidget(Qt.RightDockWidgetArea, self.dockwidget, raiseTab=True)
            self.dockwidget.tabWidget.setCurrentIndex(0)
            self.dockwidget.show()
            

                

# Initialize the plugin
def classFactory(iface):
    return Gobbler(iface)

