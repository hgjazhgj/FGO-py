# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(117, 144)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_INFO = QtWidgets.QLineEdit(self.centralwidget)
        self.TXT_INFO.setMaxLength(10)
        self.TXT_INFO.setObjectName("TXT_INFO")
        self.verticalLayout.addWidget(self.TXT_INFO)
        self.BTN_ONEBATTLE = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_ONEBATTLE.setObjectName("BTN_ONEBATTLE")
        self.verticalLayout.addWidget(self.BTN_ONEBATTLE)
        self.BTN_MAIN = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_MAIN.setObjectName("BTN_MAIN")
        self.verticalLayout.addWidget(self.BTN_MAIN)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 117, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        self.BTN_ONEBATTLE.clicked.connect(MainWindow.runOneBattle)
        self.BTN_MAIN.clicked.connect(MainWindow.runMain)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.BTN_ONEBATTLE.setText(_translate("MainWindow", "单次战斗"))
        self.BTN_MAIN.setText(_translate("MainWindow", "清空体力"))
