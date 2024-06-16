
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from bin.gui.settings import Ui_Dialog
import xml.etree.ElementTree as ET


class Settings(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1200,850)
        self.parent = self.parent()
        self.optionsInit()


    def optionsInit(self):
        self.option_file = os.path.join(os.getcwd(),"bin","options","options.json")
        if not os.path.exists(self.option_file):
            with open(self.option_file,"w",encoding="utf-8")as fp:
                json.dump(self.OPTIONS(),fp=fp,indent=0)
            return
        with open(self.option_file, "r", encoding="utf-8") as fp:
            self.options = json.load(fp)


    def recentlyInit(self):
        for recnt in self.options["recently"]:

            pass


    @staticmethod
    def OPTIONS():
        d_ = {
            "recently":[],
        }
        return d_


    def closeEvent(self, event):
        self.parent.options.setChecked(False)



