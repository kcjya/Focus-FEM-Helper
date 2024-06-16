


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from bin.gui.picker import Ui_Dialog

class PickerManager(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(PickerManager, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = self.parent()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.resize(900,700)
        self.setModal(False)
        self.setWindowTitle("拾取对象管理器")
        self.setFont(QFont("微软雅黑", 9))
        self.ui.clear_all.clicked.connect(self.parent.selectListClear)
        self.ui.export_all.clicked.connect(self.parent.exportPickManager)
        self.ui.select_style.currentIndexChanged.connect(self.parent.selectStylesEvents)
        self.ui.select_list.itemEntered.connect(self.parent.selectorInteracterWithView)
        self.ui.select_list.setMouseTracking(True)


    def closeEvent(self, event):
        self.parent.selector_popw.setChecked(False)



