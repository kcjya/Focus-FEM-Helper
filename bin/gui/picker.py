# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'picker.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(618, 430)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.select_style = QtWidgets.QComboBox(self.frame)
        self.select_style.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.select_style.setObjectName("select_style")
        self.select_style.addItem("")
        self.select_style.addItem("")
        self.select_style.addItem("")
        self.select_style.addItem("")
        self.horizontalLayout.addWidget(self.select_style)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.frame)
        self.select_list = QtWidgets.QListWidget(Dialog)
        self.select_list.setObjectName("select_list")
        self.verticalLayout.addWidget(self.select_list)
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.clear_all = QtWidgets.QPushButton(self.frame_2)
        self.clear_all.setObjectName("clear_all")
        self.horizontalLayout_2.addWidget(self.clear_all)
        self.export_all = QtWidgets.QPushButton(self.frame_2)
        self.export_all.setObjectName("export_all")
        self.horizontalLayout_2.addWidget(self.export_all)
        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(Dialog)
        self.select_style.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "拾取对象:"))
        self.label.setText(_translate("Dialog", "拾取对象："))
        self.select_style.setItemText(0, _translate("Dialog", "点拾取"))
        self.select_style.setItemText(1, _translate("Dialog", "壳拾取"))
        self.select_style.setItemText(2, _translate("Dialog", "实体拾取"))
        self.select_style.setItemText(3, _translate("Dialog", "无拾取对象"))
        self.clear_all.setText(_translate("Dialog", "清空"))
        self.export_all.setText(_translate("Dialog", "导出"))
