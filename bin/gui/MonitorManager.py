
from PyQt5.QtCore import Qt,QRectF,QThread,pyqtSignal,QTimer
from PyQt5.QtGui import QPainter,QBrush,QColor,QConicalGradient,QPen,QFont
from PyQt5.QtWidgets import *
from bin.gui.monitor import Ui_Dialog
import re



class MonitorManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(MonitorManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = self.parent()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1200, 850)
        self.setModal(False)
        self.valuesInit()
        self.buttonsInit()
        self.guiInit()
        self.timerInit()



    def openSTAFile(self):
        file, filetype = QFileDialog.getOpenFileName(self, "打开*.STA文件", "", "*.sta")
        if len(file) <= 0:
            return
        self.ui.sta_file.setText(file)

    def buttonsInit(self):
        self.ui.close.clicked.connect(self.close)
        self.ui.open_stafile.clicked.connect(self.openSTAFile)
        self.ui.update_defult.clicked.connect(self.defaultUpateTime)
        self.ui.update_time.valueChanged.connect(self.setUpdateTime)
        self.ui.start_monitor.clicked.connect(self.startMonitor)
        self.ui.terminate_monitor.clicked.connect(self.stopMonitor)
        self.ui.terminate_job.clicked.connect(self.terminateJob)

    def terminateJob(self):
        pass


    def startMonitor(self):
        if len(self.ui.sta_file.text())<=0:
            QMessageBox.information(self, "文件错误", f"请先导入STA文件",QMessageBox.Yes | QMessageBox.No)
            return

        _time = self.ui.update_time.value()
        self.main_timer.setInterval(_time)
        self.main_timer.start()
        self.ui.terminate_monitor.setEnabled(True)
        self.ui.start_monitor.setEnabled(False)

    def stopMonitor(self):
        self.main_timer.stop()
        self.ui.terminate_monitor.setEnabled(False)
        self.ui.start_monitor.setEnabled(True)

    def setUpdateTime(self, value):
        self.main_timer.setInterval(value)
        self.main_timer.start()


    def setStepData(self,_time,_count):
        self.step_time = _time
        self.step_counts = _count

    def defaultUpateTime(self):
        self.ui.update_time.setValue(5000)
        self.main_timer.setInterval(5000)
        self.main_timer.start()

    def valuesInit(self):
        self.step_time = 0
        self.step_counts = 0

    def timerInit(self):
        self.main_timer = QTimer(self)
        self.main_timer.setInterval(5000)
        self.main_timer.timeout.connect(self.readProgress)

    def readProgress(self):
        sta_file = self.ui.sta_file.text()
        try:
            datas,progress_data,temp_line,reads,step = [],[],[],str(),[]
            with open(sta_file,"r",encoding="gbk")as fp:
                reads = fp.read()
            self.ui.stafile_content.setText(reads)
            step_data = re.findall(r'STEP.*\d+', reads)
            for i in step_data:
                temp = i.split(" ")
                step.append([x for x in temp if x])
            for line in reads.split("\n"):
                if re.match(r'^\s*\d', line):
                    datas.append(line)
            for data in datas:
                temp_line = data.split(" ")
                progress_data.append([x for x in temp_line if x])
            step_num,origin_time = float(step[-1][1]),float(step[-1][3])
            # 数据处理
            inc,stp_tim,tot_tim,kinetic_eny,tot_eny = (
                int(progress_data[-1][0]),
                float(progress_data[-1][1]),
                float(progress_data[-1][2]),
                float(progress_data[-1][5]),
                float(progress_data[-1][6]),
            )
            # 更新状态
            main_ = int((tot_tim/(self.step_counts*self.step_time)) * 100)
            step_ = int((stp_tim/self.step_time) * 100)
            self.ui.main_progress.setValue(main_ if main_<100 else 100)
            self.ui.step_progress.setValue(step_ if step_<100 else 100)
            print(main_)
        except Exception as e:
            print(e)


    def guiInit(self):
        pass






    def closeEvent(self, event):
        self.parent.job_finished_action.setChecked(False)



