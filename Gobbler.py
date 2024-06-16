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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QTableWidgetItem, QDialog

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

    def onClosePlugin(self):
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.pluginIsActive = False

    def unload(self):
        for action in self.actions:
            self.iface.removePluginVectorMenu(self.tr(u'&Gobbler'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

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

    def src_callback(self, feature):
        if feature is not None and isinstance(feature, QgsFeature):
            if self.dockwidget.tableWidget.columnCount() != 4:
                self.setup_id_table()
            QgsMessageLog.logMessage(f"You clicked on feature {feature.id()}", "Gobbler", Qgis.Info)
            self.src_selected_id = feature.id()
            src_fields = self.get_source_fields()
            self.dockwidget.tableWidget.setRowCount(len(src_fields))
            rowcnt = 0
            for srcfld, destfld in self.field_mapping.items():
                field_item = QTableWidgetItem(srcfld)
                attribute_item = QTableWidgetItem(str(feature[srcfld]))
                self.dockwidget.tableWidget.setItem(rowcnt, 0, field_item)
                self.dockwidget.tableWidget.setItem(rowcnt, 1, attribute_item)
                rowcnt += 1
                
            self.change_column_color(self.dockwidget.tableWidget, 0, self.src_colour)
            self.change_column_color(self.dockwidget.tableWidget, 1, self.src_colour)
            self.canvas.unsetMapTool(self.feature_identifier)
            self.dockwidget.tabWidget.setCurrentIndex(0)

    def dest_callback(self, feature):
        if feature is not None and isinstance(feature, QgsFeature):
            if self.dockwidget.tableWidget.columnCount() != 4:
                self.setup_id_table()
            QgsMessageLog.logMessage(f"You clicked on feature {feature.id()}", "Gobbler", Qgis.Info)
            self.dest_selected_id = feature.id()
            dest_fields = self.get_destination_fields()           
            self.dockwidget.tableWidget.setRowCount(len(dest_fields))
            QgsMessageLog.logMessage(f"dest fileds : {dest_fields}", "Gobbler", Qgis.Info)
            rowcnt = 0
            for srcfld, destfld in self.field_mapping.items():
                field_item = QTableWidgetItem(destfld)
                attribute_item = QTableWidgetItem(str(feature[destfld]))
                self.dockwidget.tableWidget.setItem(rowcnt, 2, field_item)
                self.dockwidget.tableWidget.setItem(rowcnt, 3, attribute_item)
                rowcnt += 1
            self.change_column_color(self.dockwidget.tableWidget, 2, self.dest_colour)
            self.change_column_color(self.dockwidget.tableWidget, 3, self.dest_colour)
            self.canvas.unsetMapTool(self.feature_identifier)
            self.dockwidget.tabWidget.setCurrentIndex(0)

    def open_fld_mapper(self):
        mappings = self.retrieve_variable("field_mapping")
        if mappings:
            dialog = FieldMapper(self.src_lyr, self.dest_lyr, json.loads(mappings))
        else:
            dialog = FieldMapper(self.src_lyr, self.dest_lyr, None)
        dialog.load_layers()
        if dialog.exec_() == QDialog.Accepted:
            flds = dialog.get_mappings()
            QgsMessageLog.logMessage(f"mappings : {flds}", "Gobbler", Qgis.Info)
            self.save_variable("field_mapping", json.dumps(flds))
            self.field_mapping = flds
            self.dockwidget.tableWidget.clearContents()
            self.dockwidget.tableWidget.setRowCount(0)
            self.populate_field_table()
            

    def populate_field_table(self):
        self.dockwidget.tab_field_map.clearContents()
        self.dockwidget.tab_field_map.setRowCount(0)
        numb_fields = len(self.get_source_fields())
        QgsMessageLog.logMessage(f"mappings : number fields => {numb_fields}", "Gobbler", Qgis.Info)
        self.dockwidget.tab_field_map.setColumnCount(2)
        # self.dockwidget.tab_field_map.setRowCount(numb_fields)
        self.dockwidget.tab_field_map.setHorizontalHeaderLabels([f"src: {self.src_lyr.name()}", f"Dest: {self.dest_lyr.name()}"])
        rowcnt = 0
        for srcfld, destfld in self.field_mapping.items():
            QgsMessageLog.logMessage(f"mappings : srcfld, destfld => {srcfld}, {destfld}", "Gobbler", Qgis.Info)
            self.dockwidget.tab_field_map.insertRow(rowcnt)
            self.dockwidget.tab_field_map.setItem(rowcnt, 0, QTableWidgetItem(srcfld))
            self.dockwidget.tab_field_map.setItem(rowcnt, 1, QTableWidgetItem(destfld))      
            rowcnt += 1      
        self.change_column_color(self.dockwidget.tab_field_map, 0, self.src_colour)
        self.change_column_color(self.dockwidget.tab_field_map, 1, self.dest_colour)
    
    
    def get_source_fields(self):
        return list(self.field_mapping.keys())
    
    def get_destination_fields(self):
        # QgsMessageLog.logMessage(f"dict filds : {type(self.field_mapping)}", "Gobbler", Qgis.Info)
        return list(self.field_mapping.values())

    def start_select(self):
        self.canvas.setMapTool(self.feature_identifier)
        
    def select_destination_feature(self):
        lyr = self.dest_lyr
        QgsMessageLog.logMessage(f"Destination Layer: {lyr.name()}", "Gobbler", Qgis.Info)
        self.feature_identifier = IdentifyTool(self.canvas, lyr, False)
        self.feature_identifier.setLayer(lyr)
        self.feature_identifier.featureIdentified.connect(self.dest_callback)
        self.canvas.setMapTool(self.feature_identifier)

    def select_source_feature(self):
        lyr = self.src_lyr
        QgsMessageLog.logMessage(f"Source Layer: {lyr.name()}", "Gobbler", Qgis.Info)
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
                QgsMessageLog.logMessage(f"Source Layer: {source_layer_name}", "Gobbler", Qgis.Info)
                QgsMessageLog.logMessage(f"Destination Layer: {destination_layer_name}", "Gobbler", Qgis.Info)
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
            QgsMessageLog.logMessage(f"dest : {dest_fld} : {dest_value}", "Gobbler", Qgis.Info)
            target_feature.setAttribute(dest_fld, dest_value)

        self.dest_lyr.updateFeature(target_feature)
        self.dest_lyr.commitChanges()

    def change_column_color(self, table, column_index, color):
        for row in range(table.rowCount()):
            item = table.item(row, column_index)
            if item:
                item.setBackground(color)
    
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
            self.dockwidget.btn_copy.clicked.connect(self.copy_attributes)
            self.dockwidget.btn_dest.clicked.connect(self.select_destination_feature)
            self.dockwidget.btn_src.clicked.connect(self.select_source_feature)
            self.dockwidget.btn_mapfields.clicked.connect(self.open_fld_mapper)
            self.dockwidget.btn_layers.clicked.connect(self.show_layer_selection_dialog)
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.iface.addTabifiedDockWidget(Qt.RightDockWidgetArea, self.dockwidget, raiseTab=True)
            self.dockwidget.tabWidget.setCurrentIndex(0)
            self.dockwidget.show()
            

                

# Initialize the plugin
def classFactory(iface):
    return Gobbler(iface)
