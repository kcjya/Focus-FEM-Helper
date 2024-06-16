


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import *
from bin.gui.autorun import Ui_Dialog

class AutorunManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(AutorunManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = self.parent()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1200,850)
        self.setModal(False)

        self.buttonsInit()
        self.tableWidgwt()


    def buttonsInit(self):
        self.ui.import_coord.clicked.connect(self.parent.openIGSFile)
        self.ui.clear.clicked.connect(self.clearTableDatas)
        self.ui.delete_coord.clicked.connect(self.deleteTabItem)
        self.ui.default_settings.clicked.connect(self.defaultSetting)
        self.ui.generate_code_PY.clicked.connect(self.generateCodePY)


    @staticmethod
    def CODING(model_name,
                _pos,
               sys_prefix,
               _exp,
               ansys_prefix,
               step_prefix,
               _time,
               _amp_curve,
               _magnitude,
               load_area,
               load_prefix
               ):
        CODE = f"""
# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from optimization import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

iteration = len(pos)
Model = mdb.models['{model_name}']
pos = {_pos}

# The setting of the global coordinate system
try:
    for i in range(iteration):
        Model.rootAssembly.DatumCsysByThreePoints(coordSysType=CARTESIAN,
                                                             name='{sys_prefix}-'+str(i+1),
                                                             origin=(pos[i][0], pos[i][1], pos[i][2]),
                                                             point2=(pos[i][0]-1, pos[i][1]-1, pos[i][2]-1))
except Exception as error:
    print(error)                                                       
# The setting of the analysis field
for i in range(iteration):
    Model.ExpressionField(description='', expression=
        '{_exp}', localCsys=Model.rootAssembly.datums[i], name='{ansys_prefix}-'+str(i+1))

# The settings for the analysis step
try:
    for i in range(1,iteration+1):
        if i ==1:
            Model.ExplicitDynamicsStep(improvedDtMethod=ON, name='{step_prefix}-'+str(i), previous="Initial", timePeriod={_time})
        else:
            Model.ExplicitDynamicsStep(improvedDtMethod=ON, name='{step_prefix}-' + str(i), previous="{step_prefix}-" + str(i-1),timePeriod={_time})
except Exception as error:
    print(error)   
# The application of a load
try:
    for i in range(1,iteration+1):
        Model.Pressure(amplitude='{_amp_curve}', createStepName='{step_prefix}-'+str(i), 
            distributionType=FIELD, field='{ansys_prefix}-'+str(i), magnitude={_magnitude}, name=
            '{load_prefix}-'+str(i), region=Model.rootAssembly.surfaces['{load_area}'])
        if i<iteration:
            Model.loads['{load_prefix}-'+str(i)].deactivate('{step_prefix}-'+str(i+1))
except Exception as error:
    print(error)
"""

        return CODE


    def errerCheck(self):
        if (len(self.parent.PULSE_COORD)<=0 or
            len(self.ui.model_name.text()) <= 0 or
            len(self.ui.sys_prefix.text())<=0 or
            len(self.ui.ansys_expression.text()) <= 0 or
            len(self.ui.ansys_prefix.text()) <= 0 or
            len(self.ui.step_prefix.text()) <= 0 or
            len(self.ui.step_time.text()) <= 0 or
            len(self.ui.amp_curve.text()) <= 0 or
            len(self.ui.magnitude.text()) <= 0 or
            len(self.ui.load_area.text()) <= 0 or
            len(self.ui.load_prefix.text()) <= 0
            ):
            QMessageBox.warning(self, "数据错误", f"数据错误！", QMessageBox.Yes | QMessageBox.No)

            return False
        return True

    def generateCodePY(self):
        # checker
        if not self.errerCheck():return
        path, filetype = QFileDialog.getSaveFileName(self, "选择保存路径", "powerload", "*.py;;*.PY")
        if len(path) <= 0:
            self.parent.put_error(f"选择的路径有问题，已退出！")
            return

        coding = self.CODING(
            model_name=self.ui.model_name.text(),
            _pos=self.parent.PULSE_COORD,
            sys_prefix=self.ui.sys_prefix.text(),
            _exp=self.ui.ansys_expression.text(),
            ansys_prefix=self.ui.ansys_prefix.text(),
            step_prefix=self.ui.step_prefix.text(),
            _time=self.ui.step_time.text(),
            _amp_curve=self.ui.amp_curve.text(),
            _magnitude=self.ui.magnitude.text(),
            load_area=self.ui.load_area.text(),
            load_prefix=self.ui.load_prefix.text()
        )
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(coding)
        QMessageBox.information(self, "生成成功", f"Python代码生成成功！",QMessageBox.Yes | QMessageBox.No)

    def generateCodeFOR(self):
        pass


    def deleteTabItem(self):
        row = self.ui.coordinates.currentRow()
        reply = QMessageBox.warning(self, "数据删除", f"确定删除第：{row}条数据吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.ui.coordinates.removeRow(row)
            self.parent.PULSE_COORD.pop(row)
            self.parent.drawPulsePath()
            self.parent.drawPulses()


    def clearTableDatas(self):
        reply = QMessageBox.warning(self, "清空", f"确定清空数据吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.ui.coordinates.clear()
            self.parent.PULSE_COORD=[]

    def defaultSetting(self):
        self.ui.sys_prefix.setText("Datum csys")
        self.ui.ansys_prefix.setText("AnalyticalField")
        self.ui.ansys_expression.setText("exp(-2*(sqrt(X**2+Z**2)/2.5)**10 )")
        self.ui.step_prefix.setText("Step")
        self.ui.load_prefix.setText("Load")
        self.ui.step_time.setText("3E-5")
        self.ui.amp_curve.setText("Amp-1")
        self.ui.magnitude.setText("0")
        self.ui.load_area.setText("Surf-1")
        self.ui.next_step_deactive.setChecked(True)
        self.ui.sorting.setChecked(True)
        self.ui.all_in_one.setChecked(True)



    def tableWidgwt(self):
        self.ui.coordinates.resizeColumnToContents(4)
        self.ui.coordinates.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.coordinates.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.coordinates.setShowGrid(True)
        # QTableWidget设置整行选中
        self.ui.coordinates.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.coordinates.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.coordinates.setEditTriggers(QAbstractItemView.NoEditTriggers)


    @staticmethod
    def Item(data):
        item = QTableWidgetItem(data)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setToolTip(data)
        return item


    def addPulsePiont(self,x,y,z):
        len = self.ui.coordinates.rowCount()
        self.ui.coordinates.setRowCount(len+1)
        self.ui.coordinates.setItem(len, 0, self.Item(str(round(x,4))))
        self.ui.coordinates.setItem(len, 1, self.Item(str(round(y,4))))
        self.ui.coordinates.setItem(len, 2, self.Item(str(round(z,4))))
        self.ui.coordinates.setItem(len, 3, self.Item("无"))
        self.ui.coord_count_label.setText(f"一共:{len} 条数据!")


    def closeEvent(self, event):
        self.parent.auto_anasys_popw.setChecked(False)



