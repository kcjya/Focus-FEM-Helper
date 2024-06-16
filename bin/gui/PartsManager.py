

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from bin.gui.parts import Ui_Dialog

class PartsManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(PartsManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.CURRENT = ""

        self.setModal(False)
        self.ui.parts_list.resizeColumnToContents(2)
        self.ui.parts_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.parts_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.parts_list.verticalHeader().setVisible(False)
        self.ui.parts_list.setShowGrid(False)
        # QTableWidget设置整行选中
        self.ui.parts_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.parts_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.parts_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.parts_list.setHorizontalHeaderLabels(["名称","类型","详情"])
        # 双击事件处理
        self.ui.parts_list.cellDoubleClicked.connect(self.onDoubleClicked)
        #关闭窗口
        self.ui.part_close.clicked.connect(self.close)
        #导入
        self.ui.part_import.clicked.connect(self.parent().openModel)
        # 导出
        self.ui.part_output.clicked.connect(self.outputModelDatas)



    def outputModelDatas(self):
        path, filetype = QFileDialog.getSaveFileName(self, "选择保存路径", "model_list", "*.txt;;*.html")
        if len(path) <= 0:
            self.parent().put_error(f"选择的路径有问题，已退出！")
            return
        with open(path,"w",encoding="utf-8") as fp:
            fp.write(f"名称\t类型\t详情\n")
            for row in range(self.ui.parts_list.rowCount()):
                name = self.ui.parts_list.item(row, 0).text()
                type = self.ui.parts_list.item(row, 1).text()
                details = self.ui.parts_list.item(row, 2).text()
                fp.write(f"{name}\t{type}\t{details}\n")

        self.parent().put_info(f"成功导出模型列表:{path}")


    def onDoubleClicked(self, row, column):
        path = self.parent().MODEL_LIST[row][2]
        self.parent().openModel(path)
        self.setWindowTitle(f"模型管理器-{self.parent().MODEL_LIST[row][0]}")
        self.CURRENT = path
        return

    @staticmethod
    def Item(data):
        item = QTableWidgetItem(data)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setToolTip(data)
        return item

    def addPartsDetails(self, data):
        self.ui.parts_list.setRowCount(self.ui.parts_list.rowCount()+1)
        self.CURRENT = str(data[2])
        for i in range(3):
            self.ui.parts_list.setItem(self.ui.parts_list.rowCount()-1, i, self.Item(str(data[i])))

    def closeEvent(self, event):
        self.parent().ui.parts_manager.setChecked(False)
