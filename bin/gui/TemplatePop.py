

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from bin.gui.template import Ui_Dialog
import os

class TemplatePop(QDialog, Ui_Dialog):
    def __init__(self, parent=None, data=None):
        super(TemplatePop, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.parent = self.parent()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.resize(1200, 850)
        self.data = data
        self.setModal(False)
        self.initContent()


    def readHTML(self, file_name):
        try:
            with open(os.path.join(os.getcwd(),"bin","doc",file_name) ,"r", encoding="utf-8")as fp:
                return fp.read()
        except Exception as e:
            self.parent.put_error(f"读取系统文档时发生错误:{e}")

    @staticmethod
    def filetype(_file):
        return str(_file).split(".")[-1]

    def TempPOP(self,_title:str,_icon:str,_markdown:str):
        self.setWindowTitle(_title)
        self.ui.content.setHtml(self.readHTML(_markdown))
        if _icon:
            self.setWindowIcon(QIcon(_icon))
        self.setVisible(True)

    def initContent(self):
        self.ui.content.setMarkdown(self.data)
        pass


