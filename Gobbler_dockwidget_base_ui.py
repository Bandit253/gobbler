# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Gobbler_dockwidget_base.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MM_UpdaterDockWidgetBase(object):
    def setupUi(self, MM_UpdaterDockWidgetBase):
        if not MM_UpdaterDockWidgetBase.objectName():
            MM_UpdaterDockWidgetBase.setObjectName(u"MM_UpdaterDockWidgetBase")
        MM_UpdaterDockWidgetBase.resize(546, 413)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btn_src = QPushButton(self.dockWidgetContents)
        self.btn_src.setObjectName(u"btn_src")

        self.horizontalLayout.addWidget(self.btn_src)

        self.btn_dest = QPushButton(self.dockWidgetContents)
        self.btn_dest.setObjectName(u"btn_dest")

        self.horizontalLayout.addWidget(self.btn_dest)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.South)
        self.tabWidget.setTabsClosable(False)
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_2 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tableWidget = QTableWidget(self.tab_2)
        self.tableWidget.setObjectName(u"tableWidget")

        self.horizontalLayout_2.addWidget(self.tableWidget)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout = QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btn_layers = QPushButton(self.tab)
        self.btn_layers.setObjectName(u"btn_layers")

        self.verticalLayout.addWidget(self.btn_layers)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lbl_src = QLabel(self.tab)
        self.lbl_src.setObjectName(u"lbl_src")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_src.sizePolicy().hasHeightForWidth())
        self.lbl_src.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.lbl_src)

        self.txt_src = QLineEdit(self.tab)
        self.txt_src.setObjectName(u"txt_src")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txt_src.sizePolicy().hasHeightForWidth())
        self.txt_src.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.txt_src)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lbl_dest = QLabel(self.tab)
        self.lbl_dest.setObjectName(u"lbl_dest")
        sizePolicy.setHeightForWidth(self.lbl_dest.sizePolicy().hasHeightForWidth())
        self.lbl_dest.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.lbl_dest)

        self.txt_dest = QLineEdit(self.tab)
        self.txt_dest.setObjectName(u"txt_dest")

        self.verticalLayout_3.addWidget(self.txt_dest)


        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalLayout.addItem(self.horizontalSpacer)

        self.btn_mapfields = QPushButton(self.tab)
        self.btn_mapfields.setObjectName(u"btn_mapfields")

        self.verticalLayout.addWidget(self.btn_mapfields)

        self.tab_field_map = QTableWidget(self.tab)
        self.tab_field_map.setObjectName(u"tab_field_map")

        self.verticalLayout.addWidget(self.tab_field_map)

        self.tabWidget.addTab(self.tab, "")

        self.gridLayout.addWidget(self.tabWidget, 2, 0, 1, 1)

        self.btn_copy = QPushButton(self.dockWidgetContents)
        self.btn_copy.setObjectName(u"btn_copy")

        self.gridLayout.addWidget(self.btn_copy, 1, 0, 1, 1)

        MM_UpdaterDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(MM_UpdaterDockWidgetBase)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MM_UpdaterDockWidgetBase)
    # setupUi

    def retranslateUi(self, MM_UpdaterDockWidgetBase):
        MM_UpdaterDockWidgetBase.setWindowTitle(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Gobbler", None))
        self.btn_src.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Source", None))
        self.btn_dest.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Destination", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Attributes", None))
        self.btn_layers.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Select layers", None))
        self.lbl_src.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Source", None))
        self.lbl_dest.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Destination", None))
        self.btn_mapfields.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Map Fields", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MM_UpdaterDockWidgetBase", u"Settings", None))
        self.btn_copy.setText(QCoreApplication.translate("MM_UpdaterDockWidgetBase", u">>> Copy >>>", None))
    # retranslateUi

