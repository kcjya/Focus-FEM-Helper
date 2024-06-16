


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont,QBrush,QColor
from PyQt5.QtWidgets import *
from bin.gui.property import Ui_Dialog
from bin.abaqus.aba_keys import properties

class PropertyManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(PropertyManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = self.parent()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.resize(1000,800)
        self.setModal(False)
        self.setWindowTitle("新建属性")
        self.ui.query_edit.returnPressed.connect(self.dynamicQuery)
        self.ui.query_edit.textChanged.connect(self.dynamicQuery)
        self.propertiesInit()
        self.tablewidgetInit()


    def tablewidgetInit(self):
        # 查询结果的列表
        self.ui.query_results.resizeColumnToContents(2)
        self.ui.query_results.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.query_results.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.query_results.verticalHeader().setVisible(False)
        self.ui.query_results.setShowGrid(False)
        # QTableWidget设置整行选中
        self.ui.query_results.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.query_results.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.query_results.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 双击事件处理
        self.ui.query_results.clicked.connect(self.tableWidgetClicked)
        # 关闭窗口
        self.ui.confirm.clicked.connect(self.close)
        self.ui.cancel.clicked.connect(self.close)
        self.ui.export_keys.clicked.connect(self.outputModelDatas)

        # 已经设置的属性值
        self.ui.property_used.resizeColumnToContents(2)
        self.ui.property_used.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.property_used.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.property_used.verticalHeader().setVisible(False)
        self.ui.property_used.setShowGrid(False)
        # QTableWidget设置整行选中
        self.ui.property_used.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.property_used.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.property_used.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 双击事件处理
        self.ui.property_used.clicked.connect(self.usedTableWidgetClicked)
        # 添加一个属性
        self.ui.add_property.clicked.connect(self.addProperty)
        self.ui.delete_property.clicked.connect(self.deleteProperty)



    def deleteProperty(self):
        try:
            crow = self.ui.property_used.currentRow()
            # 删除字典数据
            key = self.ui.property_used.item(crow, 0).text()
            del self.parent.PROPERTIES[key]
            print(self.parent.PROPERTIES)
            self.ui.property_used.removeRow(crow)
            self.parent.ui.property_args.removeRow(crow)

        except Exception as e:
            self.parent.put_error(f"删除属性时发生错误:{e}")


    @staticmethod
    def Item(data):
        item = QTableWidgetItem(data)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setToolTip(data)
        return item

    def addProperty(self):
        key = self.ui.key.text()
        value = self.ui.value.text()
        if key == "NONE" or len(value) <= 0:
            QMessageBox.information(self, "警告", f"请检查键值是否为空",QMessageBox.Yes | QMessageBox.No)
            return
        keys = self.parent.PROPERTIES.keys()
        data_count = len(keys)
        if key not in keys:
            self.parent.PROPERTIES[key] = value
            self.ui.property_used.setRowCount(data_count + 1)
            self.ui.property_used.setItem(data_count, 0, self.Item(key))
            self.ui.property_used.setItem(data_count, 1, self.Item(value))
            # 主界面的属性列表
            self.parent.ui.property_args.setRowCount(data_count + 1)
            self.parent.ui.property_args.setItem(data_count, 0, self.Item(key))
            self.parent.ui.property_args.setItem(data_count, 1, self.Item(value))

        else:
            reply = QMessageBox.information(self, "警告", f"已添加该属性，需要修改？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
            self.parent.PROPERTIES[key] = value
            row = list(self.parent.PROPERTIES.keys()).index(key)
            self.ui.property_used.setItem(row, 1, self.Item(value))
            self.parent.ui.property_args.setItem(row, 1, self.Item(value))




    def outputModelDatas(self):
        path, filetype = QFileDialog.getSaveFileName(self, "选择保存路径", "key_list", "*.txt;;*.html")
        if len(path) <= 0:
            self.parent.put_error(f"选择的路径有问题，已退出！")
            return
        with open(path,"w",encoding="utf-8") as fp:
            fp.write(f"名称\t描述\n")
            for row in range(self.ui.query_results.rowCount()):
                name = self.ui.query_results.item(row, 0).text()
                details = self.ui.query_results.item(row, 1).text()
                fp.write(f"{name}\t{details}\n")

        self.parent.put_info(f"成功导出键值列表:{path}")


    def usedTableWidgetClicked(self):

        pass



    def tableWidgetClicked(self):
        crow = self.ui.query_results.currentRow()
        key = self.ui.query_results.item(crow, 0).text()
        details = self.ui.query_results.item(crow, 1).text()
        self.ui.key.setText(key)
        self.ui.key_details.setText(details)

    def propertiesInit(self):
        self.properties = dict(properties())
        self.ui.query_results.setRowCount(len(self.properties))
        keys = list(self.properties.keys())
        for i in range(len(keys)):
            self.ui.query_results.setItem(i, 0, QTableWidgetItem(keys[i]))
            self.ui.query_results.setItem(i, 1, QTableWidgetItem(self.properties[keys[i]]))

    def dynamicQuery(self):
        try:
            for r in range(self.ui.query_results.rowCount()):
                for c in range(self.ui.query_results.columnCount()):
                    self.ui.query_results.item(r, c).setBackground(QBrush(QColor("#FFFFFF")))

            content = self.ui.query_edit.text()
            if len(content) > 0 and self.ui.query_results.rowCount() > 0:
                items = self.ui.query_results.findItems(content, Qt.MatchStartsWith)
                queried_items = list(filter(lambda x: not x.column(), items))
                self.ui.query_results.verticalScrollBar().setValue(queried_items[0].row())
                for item in queried_items:
                    row = item.row()
                    self.ui.query_results.item(row, 0).setBackground(QBrush(QColor("#CCFFCC")))
                    self.ui.query_results.item(row, 1).setBackground(QBrush(QColor("#CCFFCC")))


        except Exception as e:
            self.parent.put_error(f"搜索时出现错误:{e}")


    def closeEvent(self, event):
        self.parent.ui.new_property.setChecked(False)



