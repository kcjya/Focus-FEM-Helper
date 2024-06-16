


from vtk import (vtkSTLReader,vtkPolyDataNormals,vtkPoints,
vtkPolyData,vtkCellLocator,mutable,vtkTransform,vtkMath)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from bin.gui.pulser import Ui_Dialog

class PulseManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(PulseManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.parent = self.parent()

        self.vectors = []

        self.resize(1100, 800)
        self.setModal(False)
        self.tableWidgwt()
        self.buttonsInit()




    def buttonsInit(self):
        self.ui.compute_normal.clicked.connect(self.computeNormal)

        pass


    @staticmethod
    def filename(file):
        return str(file).split("/")[-1]




    def _create_normals(self, path):
        # 读取 STL 文件
        reader = vtkSTLReader()
        reader.SetFileName(str(path))
        reader.Update()
        # 创建法向量计算器
        normals = vtkPolyDataNormals()
        normals.SetInputConnection(reader.GetOutputPort())
        normals.ComputePointNormalsOn()  # 开启点法向量计算
        normals.ComputeCellNormalsOff()  # 关闭单元法向量计算
        normals.Update()

        return normals


    def _compute_normal(self, index, normals, pos):
        try:
            normals_data = normals.GetOutput().GetPointData().GetNormals()
            # 指定坐标
            # 创建一个点
            point = vtkPoints()
            point.InsertNextPoint(pos)
            # 创建一个数据集
            point_polydata = vtkPolyData()
            point_polydata.SetPoints(point)
            # 创建一个单元定位器
            cell_locator = vtkCellLocator()
            cell_locator.SetDataSet(normals.GetOutput())
            cell_locator.BuildLocator()

            # 查找包含指定点的单元
            cell_id = mutable(0)
            sub_id = mutable(0)
            dist = mutable(0.0)
            cell_locator.FindClosestPoint(pos, pos, cell_id, sub_id, dist)
            # 获取指定点的法向量
            if cell_id:
                cell = normals.GetOutput().GetCell(cell_id)
                vector = list(normals_data.GetTuple(cell.GetPointId(0)))
                # 向界面添加点
                self.addVector(index, vector)
        except Exception as e:
            self.parent.put_error(e)


    def computeNormal(self):
        # 获取夫窗口导入的模型
        buttons = QMessageBox.Yes | QMessageBox.No
        model_count = len(self.parent.MODEL_LIST)
        pos_count = len(self.parent.PULSE_COORD)
        if model_count <= 0 or pos_count <= 0:
            QMessageBox.warning(self, "模型数量问题", f"已导入的模型数量为:{model_count},或没有导入点数据!", buttons)
            return
        repy = QMessageBox.information(self, "计算法向量", f"计算法向量将重新规划LSP路径，是否继续？",buttons)
        if repy==QMessageBox.No:
            return
        # 创建法向器
        normals = self._create_normals(self.parent.MODEL_LIST[0][2])
        # 获取法向量数据
        for pos in self.parent.PULSE_COORD:
            index = self.parent.PULSE_COORD.index(pos)
            self._compute_normal(index, normals, pos)
        # 在模型上绘制冲击点的坐标系
        self.parent.drawPulses(update=True, vector=self.vectors)


    def tableWidgwt(self):
        self.ui.coordinates.resizeColumnToContents(6)
        self.ui.coordinates.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.coordinates.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.coordinates.setShowGrid(True)
        # QTableWidget设置整行选中
        self.ui.coordinates.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.coordinates.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.coordinates.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 双击事件处理
        self.ui.coordinates.cellDoubleClicked.connect(self.onDoubleClicked)
        # 关闭窗口
        self.ui.close.clicked.connect(self.close)
        # 导入Model
        self.ui.import_model.clicked.connect(self.parent.openModel)
        # 导入IGS
        self.ui.import_track.clicked.connect(self.parent.openIGSFile)
        # 导出
        self.ui.export_data.clicked.connect(self.outputCoordDatas)
        self.ui.delete_data.clicked.connect(self.deleteData)



    def deleteData(self):
        row = self.ui.coordinates.currentRow()
        reply = QMessageBox.warning(self, "数据删除", f"确定删除第：{row}条数据吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.No:
            return
        try:
            self.ui.coordinates.removeRow(row)
            self.parent.PULSE_COORD.pop(row)
            self.parent.drawPulsePath()
            self.parent.drawPulses()
        except Exception as e:
            self.parent.put_error(e)


    def outputCoordDatas(self):
        path, filetype = QFileDialog.getSaveFileName(self, "选择保存路径", "coordinates", "*.txt;;*.html")
        if len(path) <= 0:
            self.parent.put_error(f"选择的路径有问题，已退出！")
            return
        with open(path,"w",encoding="utf-8") as fp:
            fp.write(f"[X]-[Y]-[Z]-[VX]-[VY]-[VZ]-[details]\n")
            for row in range(self.ui.coordinates.rowCount()):
                X = self.ui.coordinates.item(row, 0).text()
                Y = self.ui.coordinates.item(row, 1).text()
                Z = self.ui.coordinates.item(row, 2).text()
                VX = self.ui.coordinates.item(row, 2).text()
                VY = self.ui.coordinates.item(row, 3).text()
                VZ = self.ui.coordinates.item(row, 4).text()
                Details = self.ui.coordinates.item(row, 5).text()

                fp.write(f"{X},{Y},{Z},{VX},{VY},{VZ},{Details}\n")

        self.parent.put_info(f"成功导出坐标信息:{path}")



    def onDoubleClicked(self):

        pass

    @staticmethod
    def Item(data):
        item = QTableWidgetItem(data)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setToolTip(data)
        return item

    def addVector(self, index, vector):
        index = self.ui.coordinates.currentRow()
        self.vectors.append(vector)
        self.ui.coordinates.setItem(index, 3, self.Item(str(round(vector[0],4))))
        self.ui.coordinates.setItem(index, 4, self.Item(str(round(vector[1],4))))
        self.ui.coordinates.setItem(index, 5, self.Item(str(round(vector[2],4))))


    def addPulsePiont(self,x,y,z):
        len = self.ui.coordinates.rowCount()
        self.ui.coordinates.setRowCount(len+1)
        self.ui.coordinates.setItem(len, 0, self.Item(str(round(x,4))))
        self.ui.coordinates.setItem(len, 1, self.Item(str(round(y,4))))
        self.ui.coordinates.setItem(len, 2, self.Item(str(round(z,4))))

        # self.ui.details.setText(f"Total:{len+1} !")
        # self.coordinates.append([x,y,z])


    def closeEvent(self, event):
        self.parent.pulse.setChecked(False)



