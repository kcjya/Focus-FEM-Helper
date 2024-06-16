

from PyQt5.QtGui import QGuiApplication, QPixmap
from PyQt5.QtWidgets import *
from bin.gui.viewport import Ui_Dialog
from PyQt5.QtCore import Qt


class ViewportManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(ViewportManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.parent = self.parent()

        self.resize(1000,800)
        self.setModal(False)
        self.subs = list()
        self.tablewidgetInit()
        self.buttonsInit()



    def buttonsInit(self):
        self.ui.close_window.clicked.connect(self.close)


    def tablewidgetInit(self):
        # 查询结果的列表
        self.ui.windows.resizeColumnToContents(2)
        self.ui.windows.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.windows.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.windows.verticalHeader().setVisible(False)
        self.ui.windows.setShowGrid(False)
        # QTableWidget设置整行选中
        self.ui.windows.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.windows.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.windows.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 双击事件处理
        self.ui.windows.clicked.connect(self.tableWidgetClicked)

    @staticmethod
    def Item(data):
        item = QTableWidgetItem(data)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setToolTip(data)
        return item

    def addViewportData(self, subwindow):
        self.subs.append(subwindow)
        window_count = self.ui.windows.rowCount()
        self.ui.windows.setRowCount(window_count + 1)
        self.ui.windows.setItem(window_count, 0, self.Item(subwindow.windowTitle()))
        self.ui.windows.setItem(window_count, 1, self.Item("活动窗口" if subwindow.isActiveWindow()else "非活动窗口"))



    def tableWidgetClicked(self):
        try:
            row = self.ui.windows.currentRow()
            screen = QGuiApplication.primaryScreen()
            screenshot = screen.grabWindow(self.subs[row].winId())
            self.ui.current_window.setPixmap(QPixmap(screenshot).scaled(self.ui.current_window.size()))
        except Exception as e:
            print(e)


    def closeEvent(self, event):
        self.parent.viewport_manager.setChecked(False)



