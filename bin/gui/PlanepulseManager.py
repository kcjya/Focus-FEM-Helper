
import re
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import *
from bin.gui.plane_pulse import Ui_Dialog
import matplotlib.pyplot as plt
from bin.abaqus.aba_sample import PlaneSample
import numpy as np
from scipy import interpolate
from bin.abaqus.aba_run import ABARun

class PlanePulseManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(PlanePulseManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1350,1100)
        self.setWindowTitle("平板冲击参数表")
        self.setWindowIcon(QIcon(":/graphics/plane_pulse.png"))
        self.ui.python.setPixmap(QPixmap(":/graphics/python.png").scaled(100,100))

        self.parent = self.parent()
        self._data = dict()
        self.CURRENT = ""
        self.planer = PlaneSample()

        self.setModal(False)
        self.tablesInit()
        self.buttonsInit()

    def buttonsInit(self):
        self.ui.start_job.setEnabled(False)
        self.ui.check_data.clicked.connect(self.checkData)
        self.ui.export_data.clicked.connect(self.outputDatas)
        self.ui.close.clicked.connect(self.close)
        self.ui.clear_all.clicked.connect(self.clearAll)
        self.ui.plot_path.clicked.connect(self.plotPath)
        self.ui.plot_amp.clicked.connect(self.plotAmp)
        self.ui.amp_check.clicked.connect(self.usingAmp)
        self.ui.jc_check.clicked.connect(self.usingJC)
        self.ui.generate_python.clicked.connect(self.generatePython)
        self.ui.start_job.clicked.connect(self.submitJob)
        self.ui.main_property.doubleClicked.connect(self.buttonPassive)
        self.ui.using_magnitude.clicked.connect(self.userMagnitude)



    def buttonPassive(self):
        self.ui.plot_path.setEnabled(False)
        self.ui.generate_python.setEnabled(False)
        self.ui.start_job.setEnabled(False)

    def userMagnitude(self, checked):
        self.ui.magnitude.setEnabled(checked)


    def submitJob(self):
        try:
            path = os.path.join(os.getcwd(),"cache",f"{self._data['Inp_Name']}_python.py")
            if not os.path.exists(path):
                self.planer.generateCode(path, self._data)
            # 获取主界面的abaqus运行方式
            ifgui = True if self.parent.ui.gui.isChecked() else False
            args = F"abaqus cae {'script' if ifgui else 'noGUI'}={path}"
            self.parent.put_info(f"Abaqus运行参数:{args},启动中...")
            ABARun().run(args=args,waiting=10)
        except Exception as e:
            self.parent.put_error(f"提交任务时发生错误{e}!")


    def generatePython(self):
        try:
            path = os.path.join(os.getcwd(),"cache",f"{self._data['Inp_Name']}_python.py")
            r = QMessageBox.warning(self, "检查提醒", f"请确保数据正确!是否继续?", QMessageBox.Yes | QMessageBox.No)
            if r == QMessageBox.Yes:
                self.planer.generateCode(path,self._data)
            self.parent.put_info(f"已经生成python文件:{path}.")
        except Exception as e:
            print(e)

    def usingJC(self, checked):
        self.ui.jc_list.setEnabled(checked)

    def usingAmp(self, checked):
        self.ui.amp_list.setEnabled(checked)
        self.ui.plot_amp.setEnabled(checked)

    def clearAll(self):
        reply = QMessageBox.warning(self, "清空提醒", f"删除数据不可恢复!",QMessageBox.Yes | QMessageBox.No)
        if reply==QMessageBox.Yes:
            self.ui.main_property.clear()
            self.ui.amp_list.clear()
            for row in range(self.ui.jc_list.rowCount()):
                self.ui.main_property.item(row, 0).setText("")


    def checkData(self):
        for row in range(self.ui.main_property.rowCount()):
            _data = self.ui.main_property.verticalHeaderItem(row).text()
            key = re.findall(r"\((.*?)\)", _data)[0]
            value_list = list()
            for col in range(self.ui.main_property.columnCount()):
                try:
                    _arg = self.ui.main_property.item(row,col).text()
                    if len(_arg) >0 :
                        value_list.append(float(_arg))
                except Exception as e:
                    pass
            if len(value_list)==1:
                self._data[key] = value_list[0]
            else:
                self._data[key] = tuple(value_list)
            value_list.clear()
        # 是否启用JC本构模型
        self._data["JOHNSON_COOK"] = self.ui.jc_check.isChecked()
        if self.ui.jc_check.isChecked():
            jc_arg = list()
            for row in range(self.ui.jc_list.rowCount()):
                try:
                    _data = self.ui.jc_list.item(row,0).text()
                    jc_arg.append(float(_data))
                except:pass
            self._data["Plastic"] = {
                "JCValue":jc_arg[:6:1],
                "JCRate":jc_arg[6:len(jc_arg):1],
            }
        # 是否启用幅值
        if self.ui.amp_check.isChecked():
            amp_datas = list()
            for row in range(self.ui.amp_list.rowCount()):
                try:
                    _time = self.ui.amp_list.item(row, 0).text()
                    _amp = self.ui.amp_list.item(row, 1).text()
                    amp_datas.append((float(_time),float(_amp)))
                except:pass
            self._data["Amp"] = tuple(amp_datas)

        # 其他参数
        self._data["Inp_Name"] = self.ui.inp_name.text()
        self._data["Elem_Type"] = self.ui.elem_type.currentText()
        self._data["Spot_Type"] = self.ui.spot_type.currentText()
        self._data["Expression"] = self.ui.expression.text()
        self._data["FOR"] = f"({self.ui.FOR.text()})"
        self._data["CPUS"] = self.ui.cpus.value()
        if self.ui.using_magnitude.isChecked():
            self._data["Magnitude"] = self.ui.magnitude.text()
        self._data["WorkingDir"] = self.parent.working.text()
        self.ui.start_job.setEnabled(True)
        self.ui.generate_python.setEnabled(True)
        self.ui.plot_path.setEnabled(True)
        self.plotPath()


    def plotAmp(self):
        try:
            amp_x, amp_y = list(), list()
            for row in range(self.ui.amp_list.rowCount()):
                try:
                    _time = self.ui.amp_list.item(row, 0).text()
                    _amp = self.ui.amp_list.item(row, 1).text()
                    amp_x.append(float(_time))
                    amp_y.append(float(_amp))
                except:
                    pass
            if len(amp_y) <= 0: return
            # 创建绘图窗口并设置大小
            plt.figure(figsize=(8, 8))
            # 绘制原始曲线和光滑曲线
            plt.plot(amp_x, amp_y, marker="o")
            self.parent.put_info("成功绘制幅值曲线")
            plt.show()

        except Exception as e:
            self.parent.put_error(f"绘制幅值曲线时候出现错误:{e}")

    def plotPath(self):
        try:
            # 添加矩形到图中
            fig, ax = plt.subplots(figsize=(8,8))
            # 二维点路径
            points = []
            data = self.planer._data_process(self._data)
            # 创建绘图窗口并设置大小
            _height = float(self._data["H"]) - 2*float(self._data["INFT"])
            _width = float(self._data["W"]) - 2*float(self._data["INFT"])
            pt = (float(self._data["INFT"]), float(self._data["INFT"]))
            rect = plt.Rectangle(pt, _height, _width, fc="green")
            ax.add_patch(rect)
            for pos in data["Path"]:
                points.append([pos[0],pos[1]])
                spot = plt.Circle((pos[0], pos[1]), float(self._data["Spot_Size"])/2, fill=False)
                if self._data["Spot_Type"] == "Square":
                    spot_pt = (pos[0] - float(self._data["Spot_Size"]) / 2, pos[1] - float(self._data["Spot_Size"]) / 2)
                    spot = plt.Rectangle(spot_pt,float(self._data["Spot_Size"]),float(self._data["Spot_Size"]),fill=False)
                ax.add_artist(spot)
            # 绘制点路径
            plt.plot([point[0] for point in points], [point[1] for point in points], marker='o',color="red")
            # 给矩形添加一个txt标签
            plt.text(pt[0]+0.2, pt[1]+0.2, 'Finite', fontsize=15, color='black', ha='left')
            plt.text(0.2, 0.2, 'Infinite', fontsize=15, color='black', ha='left')
            # 添加文本标签
            for i, point in enumerate(points):
                plt.text(point[0]+0.5, point[1], f"P{str(i + 1)}", fontsize=12, ha='left',color="red")
            plt.xlim(0, float(data["H"]))
            plt.ylim(0, float(data["W"]))
            self.parent.put_info("成功绘制LSP路径曲线")

            plt.show()


        except Exception as e:
            self.parent.put_error(f"绘制路径时发生错误:{e},请查看是否已检查参数?")
            QMessageBox.warning(self, "资源检查", f"绘制路径时发生错误:{e}!", QMessageBox.Yes | QMessageBox.No)

    def tablesInit(self):
        """主要参数列表"""
        self.ui.main_property.resizeColumnToContents(2)
        self.ui.main_property.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.main_property.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.main_property.setSelectionMode(QAbstractItemView.SingleSelection)
        """JC参数列表"""
        self.ui.jc_list.resizeColumnToContents(0)
        self.ui.jc_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.jc_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.ui.jc_list.setSelectionMode(QAbstractItemView.SingleSelection)
        for row in range(self.ui.jc_list.rowCount()):
            try:
                self.ui.jc_list.item(row,1).setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
            except:
                item = QTableWidgetItem("无")
                item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
                self.ui.jc_list.setItem(row,1,item)

        """幅值参数列表"""
        self.ui.amp_list.resizeColumnToContents(1)
        self.ui.amp_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.amp_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.ui.amp_list.setSelectionMode(QAbstractItemView.SingleSelection)





    def outputDatas(self):
        try:
            path, filetype = QFileDialog.getSaveFileName(self, "选择保存路径", "properties", "*.txt;;*.html")
            if len(path) <= 0:
                self.parent.put_error(f"选择的路径有问题，已退出！")
                return
            with open(path,"w",encoding="utf-8") as fp:
                fp.write(f"[名称] - [参数]\n")
                for key in self._data.keys():
                    fp.write(f"[{key}] - [{self._data[key]}]\n")
            self.parent.put_info(f"成功导出Properties:{path}")
        except Exception as e:
            print(e)


    def closeEvent(self, event):
        self.parent.plane_sample.setChecked(False)