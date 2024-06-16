
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import *
from bin.gui.extractor import Ui_Dialog
from PyQt5.QtChart import QChart, QChartView, QLineSeries


class ExtractorManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(ExtractorManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = self.parent()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1100, 750)
        self.setModal(False)
        self.plotInit()



    def plotInit(self):
        #绘制图表
        self.series_liner = QLineSeries()
        self.series_liner.append(0, 1)
        self.series_liner.append(1, 3)
        self.series_liner.append(2, 2)
        self.series_liner.append(3, 4)
        self.series_liner.append(4, 3)

        chart = QChart()
        chart.addSeries(self.series_liner)
        chart.createDefaultAxes()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        # 启用图表的缩放和拖动
        chart_view.setRubberBand(QChartView.HorizontalRubberBand)
        chart_view.setDragMode(QChartView.ScrollHandDrag)
        self.ui.plot_container.addWidget(chart_view)


    def closeEvent(self, event):
        self.parent.data_extraction_action.setChecked(False)



