import meshio
import subprocess
import numpy as np

from bin.gui.main_ui import Ui_MainWindow
from bin.aba_details.version import Version
from bin.abaqus.aba_run import ABARun
from bin.abaqus.aba_generator import ABAgenerator
from bin.abaqus.aba_sample import PlaneSample
from bin.abaqus.commands import Commands

from multiprocessing import Process,freeze_support
from bin.qvtks.default_interactor import InteractorStyle
from bin.qvtks.types import MODELINPUT
from bin.qvtks.default_interactor import InteractorStyle
from bin.qvtks.solid_interactor import SolidPickInteractorStyle
from bin.qvtks.points_interactor import PointPickInteractorStyle
from bin.qvtks.cells_interactor import CellPickInteractorStyle

from bin.gui.PartsManager import PartsManager
from bin.gui.PickerManager import PickerManager
from bin.gui.PropertyManager import PropertyManager
from bin.gui.TemplatePop import TemplatePop
from bin.gui.AutorunManager import AutorunManager
from bin.gui.ViewportManager import ViewportManager
from bin.gui.PulseManager import PulseManager
from bin.gui.PlanepulseManager import PlanePulseManager
from bin.gui.ExtractorManager import ExtractorManager
from bin.gui.MonitorManager import MonitorManager
from bin.gui.SettingsWindow import Settings


from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util.numpy_support import vtk_to_numpy
from meshio import read as readModel
from meshio import write as writeModel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import datetime
import cv2
import time
import sys
import vtk
import os


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Windows(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Windows, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.setWindowTitle("Focus FEM Helper-1.0.1_base(测试版本1)")
        # self.setWindowTitle("基于ABAQUS复的杂曲面激光冲击路径自动加载软件 v1.0")
        self.setWindowTitle("Simulation Software For Laser Shock Processing v1.0")
        self.sizeInit()
        self.valuesInit()
        self.childrenWindows()
        self.vtkRenderWindowInit()
        self.environmentInit()
        self.toolBarInit()
        self.viewportBarInit()
        self.guiInit()
        self.actionsInit()
        self.datasTreeInit()
        self.buttonClickEvents()

        # Test

        # Warning
        self.template_window.TempPOP("软件须知",":/graphics/information.png","warnings.html")



    def environmentInit(self):
        self.abaqus_python_generator = ABAgenerator()


    def valuesInit(self):
        self.MODEL_DES={
            "name":None,
            "boundary":None,
            "edges": None,
            "boundsize": 0
        }
        self.ACTORS_2D = []
        self.DEFAULT_BACK = [(.8,.8,.8,True),(1,1,1,False),(0,0,0,False)]
        self.BACKGROUND_INDEX = 0
        self.PULSE_PATH_ACTORS = []
        self.MODEL_LIST = list()
        self.PROPERTIES = dict()
        self.CMDLIST = list()
        self.PULSE_COORD = list()
        self.PULSE_COORD_SYSTEM = list()


    def changeWorksapce(self):
        dir = QFileDialog.getExistingDirectory(self, "选择工作路径")
        if len(dir) <= 0:
            return
        self.working.setText(dir)
        self.put_info(f"更改工作区为:{dir}")



    def toolBarInit(self):
        self.files = QToolBar(self)
        self.working = QLineEdit(self)
        self.working.setMaximumWidth(250)
        self.change_worksapce = QPushButton("Change",self)
        self.change_worksapce.clicked.connect(self.changeWorksapce)
        self.files.addWidget(QLabel("Working Directory：",self))
        self.files.addWidget(self.working)
        self.files.addWidget(self.change_worksapce)
        self.addToolBar(self.files)

        # 设置拾取方式
        self.select_style_bar = QToolBar(self)

        self.select_style = QComboBox(self)
        self.select_style.addItems(["Pick Points","壳拾取","实体拾取","Default"])
        self.select_style.setCurrentIndex(3)
        self.select_style.setMaximumWidth(250)
        self.select_style.currentIndexChanged.connect(self.changeSelectStyle)
        self.select_style_bar.addWidget(QLabel("Pick-up Style：", self))
        self.select_style_bar.addWidget(self.select_style)
        # 打开拾取器
        self.selector_popw = QAction(QIcon(":/graphics/select.png"), "点击打开拾取器", self)
        self.selector_popw.triggered.connect(self.selectorAction)
        self.selector_popw.setCheckable(True)
        self.select_style_bar.addAction(self.selector_popw)

        self.addToolBar(self.select_style_bar)


        # self.addToolBarBreak()

        self.selectorGuiInit()
        self.selector_bar = QToolBar(self)
        self.selector_bar.setIconSize(QSize(30,30))
        # 运行Cmd窗口
        self.normal = QAction(QIcon(":/graphics/normal.png"), "法向检查", self)
        self.normal.triggered.connect(self.normalCheck)
        self.selector_bar.addAction(self.normal)

        # 运行Cmd窗口
        self.cmd = QAction(QIcon(":/graphics/cmd.png"), "运行Cmd", self)
        self.cmd.setCheckable(True)
        self.cmd.triggered.connect(self.runCmd)
        self.selector_bar.addAction(self.cmd)

        # 添加分割线
        self.selector_bar.addSeparator()
        # 自动分析
        self.auto_anasys_popw = QAction(QIcon(":/graphics/auto_ansys.png"), "运行自动分析", self)
        self.auto_anasys_popw.triggered.connect(self.autoAnasysPop)
        self.auto_anasys_popw.setCheckable(True)
        self.selector_bar.addAction(self.auto_anasys_popw)
        # LSP路径点管理
        self.plane_sample = QAction(QIcon(":/graphics/plane_pulse.png"), "平板激光冲击", self)
        self.plane_sample.setCheckable(True)
        self.plane_sample.triggered.connect(self.palneSampleAction)
        self.selector_bar.addAction(self.plane_sample)
        # LSP路径点管理
        self.pulse = QAction(QIcon(":/graphics/pulse.png"), "LSP路径点管理", self)
        self.pulse.setCheckable(True)
        self.pulse.triggered.connect(self.pulseManager)
        self.selector_bar.addAction(self.pulse)
        # 数据提取-后处理
        self.data_extraction_action = QAction(QIcon(":/graphics/data_extraction.png"), "数据提取-后处理", self)
        self.data_extraction_action.setCheckable(True)
        self.data_extraction_action.triggered.connect(self.dataExtraction)
        self.selector_bar.addAction(self.data_extraction_action)
        # 进度监控
        self.job_finished_action = QAction(QIcon(":/graphics/finished.png"), "进度监控", self)
        self.job_finished_action.setCheckable(True)
        self.job_finished_action.triggered.connect(self.jobFinished)
        self.selector_bar.addAction(self.job_finished_action)

        self.addToolBar(self.selector_bar)


        self.model_view_bar = QToolBar(self)
        self.model_view_bar.setIconSize(QSize(30, 30))
        # 显示局部坐标
        self.show_local_coordinate = QAction(QIcon(":/graphics/local_coordinate.png"), "显示局部坐标", self)
        self.show_local_coordinate.setCheckable(True)
        self.show_local_coordinate.setChecked(True)
        self.show_local_coordinate.triggered.connect(self.showLocalCoordinate)
        self.model_view_bar.addAction(self.show_local_coordinate)
        # 显示冲击点
        self.show_path = QAction(QIcon(":/graphics/path_point.png"), "显示冲击点", self)
        self.show_path.setCheckable(True)
        self.show_path.setChecked(False)
        self.show_path.triggered.connect(self.showPulsePath)
        self.model_view_bar.addAction(self.show_path)

        self.addToolBar(self.model_view_bar)
        """--------------"""
        self.back_view_bar = QToolBar(self)
        self.back_view_bar.setIconSize(QSize(30, 30))
        # 进度监控
        self.gradient = QAction(QIcon(":/graphics/gradient.png"), "背景渐变", self)
        self.gradient.triggered.connect(self.gradientChange)
        self.back_view_bar.addAction(self.gradient)
        # 进度监控
        self.single_view = QAction(QIcon(":/graphics/single_view.png"), "整洁显示", self)
        self.single_view.setCheckable(True)
        self.single_view.triggered.connect(self.singleBackView)
        self.back_view_bar.addAction(self.single_view)
        # 进度监控
        self.background_option = QAction(QIcon(":/graphics/background.png"), "背景选项", self)
        # self.background_option.triggered.connect()
        self.back_view_bar.addAction(self.background_option)

        self.addToolBar(self.back_view_bar)


        self.screentool_bar = QToolBar(self)
        self.screentool_bar.setIconSize(QSize(30, 30))
        self.screenshot = QAction(QIcon(":/graphics/screenshot.png"), "点击截取渲染窗口", self)
        self.screenshot.triggered.connect(self.screenShot)
        self.screentool_bar.addAction(self.screenshot)
        self.addToolBar(self.screentool_bar)
    #     # 设置正交投影
    #         self.camera.ParallelProjectionOff()
        self.view_bar = QToolBar(self)
        self.view_bar.setIconSize(QSize(30, 30))
        self.parallel = QAction(QIcon(":/graphics/parallel.png"), "点击切换投影视图", self)
        self.parallel.setCheckable(True)
        self.parallel.setChecked(True)
        self.parallel.triggered.connect(self.parallelView)
        self.view_bar.addAction(self.parallel)
        # 添加分割线
        self.view_bar.addSeparator()

        self.gridview_style = QAction(QIcon(":/graphics/grid_3d.png"), u"显示线框", self)
        self.gridview_style.setCheckable(True)
        self.gridview_style.triggered.connect(self.showAsWaveframe)
        self.view_bar.addAction(self.gridview_style)

        self.points_style = QAction(QIcon(":/graphics/points.png"), u"显示为点云", self)
        self.points_style.setCheckable(True)
        self.points_style.triggered.connect(self.showAsPoints)
        self.view_bar.addAction(self.points_style)

        self.light_switch_on = QAction(QIcon(":/graphics/light_off.png"), u"点击开灯", self)
        self.light_switch_on.setCheckable(True)
        self.light_switch_on.setChecked(True)
        self.light_switch_on.triggered.connect(self.lightOn)
        self.view_bar.addAction(self.light_switch_on)

        self.light_switch_off = QAction(QIcon(":/graphics/light_on.png"), u"点击关灯", self)
        self.light_switch_off.setCheckable(True)
        self.light_switch_off.triggered.connect(self.lightOff)
        self.view_bar.addAction(self.light_switch_off)

        self.addToolBar(self.view_bar)

        # viewport
        self.viewport_bar = QToolBar(self)
        self.viewport_bar.actionTriggered.connect(self.viewportTriggered)
        self.viewport_bar.setIconSize(QSize(30, 30))

        self.viewport_single = QAction(QIcon(":/graphics/viewport_single.png"), "单个渲染窗口铺满", self)
        self.viewport_bar.addAction(self.viewport_single)

        self.viewport_double = QAction(QIcon(":/graphics/viewport_double.png"), "渲染窗口并排", self)
        self.viewport_bar.addAction(self.viewport_double)

        self.add_viewport = QAction(QIcon(":/graphics/add_viewport.png"), "点击添加渲染窗口", self)
        self.viewport_bar.addAction(self.add_viewport)

        self.viewport_manager = QAction(QIcon(":/graphics/viewport_manager.png"), "渲染窗口管理", self)
        self.viewport_manager.setCheckable(True)
        self.viewport_bar.addAction(self.viewport_manager)

        self.addToolBar(self.viewport_bar)

        # contact
        self.contact_bar = QToolBar(self)
        self.contact_bar.actionTriggered.connect(self.contactTriggered)
        self.contact_bar.setIconSize(QSize(30, 30))

        self.options = QAction(QIcon(":/graphics/options.png"), "选项", self)
        self.options.setCheckable(True)
        self.options.triggered.connect(self.optionsWindow)
        self.contact_bar.addAction(self.options)
        self.contact_bar.addSeparator()
        self.wechat = QAction(QIcon(":/graphics/wechat.png"), "联系WeChat", self)
        self.contact_bar.addAction(self.wechat)
        self.qq = QAction(QIcon(":/graphics/QQ.png"), "联系QQ", self)
        self.contact_bar.addAction(self.qq)
        self.official = QAction(QIcon(":/graphics/official.png"), "官方网址", self)
        self.contact_bar.addAction(self.official)

        self.addToolBar(self.contact_bar)


    def singleBackView(self, checked):
        self.right_top_widget(not checked)
        self.left_bottom_widget(not checked)
        if checked:
            for _2d_actor in self.renderer.GetActors2D():
                self.renderer.RemoveActor2D(_2d_actor)
        else:
            for _2d_actor in self.ACTORS_2D:
                self.renderer.AddActor2D(_2d_actor)

        self.vtkWidget.update()



    def gradientChange(self):
        self.BACKGROUND_INDEX = (self.BACKGROUND_INDEX+1)%3
        _1,_2,_3,_ = self.DEFAULT_BACK[self.BACKGROUND_INDEX]
        self.renderer.SetBackground(_1,_2,_3)
        self.renderer.SetBackground2(.1, .2, .4)  # 设置页面顶部颜色值
        self.renderer.SetGradientBackground(_)  # 开启渐变色背景设置
        self.vtkWidget.update()


    def showPulsePath(self, checked):
        if not checked and len(self.PULSE_PATH_ACTORS)>0:
            for actor in self.PULSE_PATH_ACTORS:
                self.renderer.RemoveActor(actor)
            self.vtkWidget.update()
            return
        self.drawPulsePath()


    def showLocalCoordinate(self, checked):
        if not checked:
            for actor in self.PULSE_COORD_SYSTEM:
                self.renderer.RemoveActor(actor)
            self.vtkWidget.update()
            return
        self.drawPulses()


    def optionsWindow(self,checked):
        self.settings_window.setVisible(checked)


    def contactTriggered(self, action):
        if action is self.wechat:
            self.put_info("微信:18076023795")
        elif action is self.qq:
            self.put_info("QQ:1043886331")
        elif action is self.official:
            self.put_warning("暂未开放官方网址，敬请期待。")

    def lightOn(self, checked):
        self.renderer.GetLights().GetItemAsObject(0).SetSwitch(checked)
        self.light_switch_off.setChecked(not checked)
        self.vtkWidget.update()


    def lightOff(self, checked):
        self.renderer.GetLights().GetItemAsObject(0).SetSwitch(not checked)
        self.light_switch_on.setChecked(not checked)
        self.vtkWidget.update()


    def dataExtraction(self, checked):
        self.extractor_window.setVisible(checked)


    def jobFinished(self,checked):
        self.monitor_window.setVisible(checked)
        pass



    def viewportTriggered(self, action):
        if action is self.add_viewport:
            sub = QMdiSubWindow()

            # l = QLabel()
            # l.setPixmap(QPixmap(":/graphics/viewport.png"))
            # sub.setWidget(l)

            self.ui.viewer.addSubWindow(sub)
            sub.show()
            sub.resize(600,400)
            sub.setWindowIcon(QIcon(":/graphics/viewport.png"))
            sub.setWindowTitle(f"Render View-{len(self.ui.viewer.subWindowList())}")
            self.ui.viewer.tileSubWindows()
            self.viewport_manager_window.addViewportData(sub)

        if action is self.viewport_double:
            self.ui.viewer.tileSubWindows()
        if action is self.viewport_single:
            active_window = self.ui.viewer.activeSubWindow()
            active_window.showMaximized()
        elif action is self.viewport_manager:
            checkable = self.viewport_manager.isChecked()
            self.viewport_manager_window.setVisible(checkable)



    def normalCheck(self):
        # 调用法相检查器优先检查数据的完整性
        self.pulse_window.computeNormal()


    def pulseManager(self, checked):
        self.pulse_window.setVisible(checked)
        pass

    def runCmd(self ,checked):
        if checked:
            self.cmd_pop = subprocess.Popen([r"cmd"], shell=False)
        else:
            self.cmd_pop.terminate()
            self.cmd_pop.wait()


    def terminateALLCmd(self):
        for cmd in self.CMDLIST:
            cmd.terminate()


    def autoAnasysPop(self ,checked):
        self.auto_window.setVisible(checked)



    def showAsPoints(self, checked):
        if checked:
            self.onlyPointsCloud()
            self.ui.points_cloud.setChecked(True)
            self.gridview_style.setChecked(False)
        else:
            self.onlySolid()
            self.ui.solid.setChecked(True)

    def showAsWaveframe(self, checked):
        if checked:
            self.onlyWaveframe()
            self.ui.waveframe.setChecked(True)
            self.points_style.setChecked(False)
        else:
            self.onlySolid()
            self.ui.solid.setChecked(True)



    def changeSelectStyle(self ,index):
        self.selectStylesEvents(index ,True)




    def parallelView(self, checked):
        self.camera.ParallelProjectionOn()
        if checked:
            self.camera.ParallelProjectionOff()
        self.vtkWidget.update()



    def actionsInit(self):
        # 文件菜单
        self.ui.menu_file.triggered.connect(self.menuFileTriggered)
        # 视图菜单
        self.ui.menu_view.triggered.connect(self.menuViewTriggered)
        # 实例菜单
        self.ui.menu_sample.triggered.connect(self.menuSampleTriggered)
        # 插件菜单
        self.ui.menu_plugin.triggered.connect(self.menuPluginTriggered)
        # 工具菜单
        self.ui.menu_tool.triggered.connect(self.menuToolTriggered)
        # 选项菜单
        self.ui.menu_option.triggered.connect(self.menuOptionTriggered)
        # 其他菜单
        self.ui.menu_other.triggered.connect(self.menuOtherTriggered)


    def menuFileTriggered(self, action):
        if action is self.ui.action_import_track:
            self.openIGSFile()
        if action is self.ui.action_output_VDLOAD:
            self.generateFortranCode()
        pass

    def menuViewTriggered(self, action):

        pass

    def menuSampleTriggered(self, action):
        if action is self.ui.action_plane_pulse:
            self.plane_pulse_window.setVisible(True)
            self.plane_sample.setChecked(True)

    def palneSampleAction(self, checked):
        self.plane_pulse_window.setVisible(checked)

    def menuPluginTriggered(self, action):

        pass

    def menuToolTriggered(self, action):

        pass

    def menuOptionTriggered(self, action):

        pass

    def menuOtherTriggered(self, action):
        if action is self.ui.action_help:
            self.template_window.TempPOP("帮助文档", ":/graphics/help.png", "help.html")
        elif action is self.ui.action_aboutsoft:
            self.template_window.TempPOP("关于软件", ":/graphics/about.png", "software.html")
        elif action is self.ui.action_aboutus:
            self.template_window.TempPOP("关于开发者", ":/graphics/about_us.png", "us.html")
        elif action is self.ui.action_devlog:
            self.template_window.TempPOP("开发日志", ":/graphics/development_log.png", "dev.html")
        elif action is self.ui.action_reference:
            self.template_window.TempPOP("参考", ":/graphics/reference.png", "reference.html")



    def readHTML(self, file_name):
        try:
            with open(os.path.join(os.getcwd(),"bin","doc",file_name) ,"r", encoding="utf-8")as fp:
                return fp.read()
        except Exception as e:
            self.put_error(f"读取系统文档时发生错误:{e}")


    def viewportBarInit(self):
        # 设置摄像机以获取场景的特定视图
        self.camera = vtk.vtkCamera()
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetPosition(1, 1, 1)
        self.camera.UseOffAxisProjectionOff()
        self.camera.ComputeViewPlaneNormal()
        self.camera.SetViewUp(0, 0, 1)
        # self.camera.Zoom(0.4)
        # 设置正交投影
        self.camera.ParallelProjectionOff()
        self.renderer.SetActiveCamera(self.camera)
        self.renderer.ResetCamera()

        self.viewport = QToolBar(self)
        self.viewport.actionTriggered.connect(self.viewStyle)
        self.viewport.setIconSize(QSize(30, 30))
        # 导入STL模型文件
        self.upview_action = QAction(QIcon(":/graphics/up_view.png"), u"俯视图", self)
        self.viewport.addAction(self.upview_action)
        self.leftview_action = QAction(QIcon(":/graphics/left_view.png"), u"左视图", self)
        self.viewport.addAction(self.leftview_action)
        self.frontview_action = QAction(QIcon(":/graphics/front_view.png"), u"正视图", self)
        self.viewport.addAction(self.frontview_action)
        self.rightview_action = QAction(QIcon(":/graphics/right_view.png"), u"右视图", self)
        self.viewport.addAction(self.rightview_action)
        self.backview_action = QAction(QIcon(":/graphics/back_view.png"), u"后视图", self)
        self.viewport.addAction(self.backview_action)
        self.bottomview_action = QAction(QIcon(":/graphics/bottom_view.png"), u"下视图", self)
        self.viewport.addAction(self.bottomview_action)
        self._3dview_action = QAction(QIcon(":/graphics/3D.png"), u"3D视图", self)
        self.viewport.addAction(self._3dview_action)

        self.addToolBar(self.viewport)


    def viewStyle(self, action):
        for act in self.viewport.actions():
            if not act is action:
                act.setChecked(False)
        self.camera.SetFocalPoint(0, 0, 0)
        if action is self.upview_action:  # up
            self.camera.SetPosition(0, 0, 1)
            self.camera.SetViewUp(0, 1, 0)
        elif action is self.leftview_action:  # left
            self.camera.SetPosition(0, -1, 0)
            self.camera.SetViewUp(0, 0, 1)
        elif action is self.frontview_action:  # front
            self.camera.SetPosition(1, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
        elif action is self.rightview_action:  # right
            self.camera.SetPosition(0, 1, 0)
            self.camera.SetViewUp(0, 0, 1)
        elif action is self.backview_action:  # back
            self.camera.SetPosition(-1, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
        elif action is self.bottomview_action:  # buttom
            self.camera.SetPosition(0, 0, -1)
            self.camera.SetViewUp(0, 1, 0)
        else:
            self.camera.SetPosition(1, 1, 1)
            self.camera.SetViewUp(0, 0, 1)

        self.renderer.Render()

        self.renderer.ResetCamera()
        self.vtkWidget.update()


    def exportPickManager(self):
        self.put_warning("暂未支持导出非字符行参量!")


    def selectorGuiInit(self):
        self.selector = PickerManager(self)
        self.last_highlight_index = 0



    def selectorInteracterWithView(self,item):
        try:
            row = self.selector.ui.select_list.row(item)
            curpt = self.interactorstyle.point_actors[row]
            lstpt = self.interactorstyle.point_actors[self.last_highlight_index]
            curpt.GetProperty().SetColor(0, 1, 0)
            lstpt.GetProperty().SetColor(self.interactorstyle.pt_color)
            self.last_highlight_index = row
            self.vtkWidget.update()
        except Exception as e:
            print(e)


    def selectListClear(self):
        try:
            self.selector.ui.select_list.clear()
            for i in self.interactorstyle.point_actors:
                self.renderer.RemoveActor(i)
            self.vtkWidget.update()
        except Exception as e:
            print(e)


    def selectStylesEvents(self, index, call=False):
        # 保持两个index统一
        if call:self.selector.ui.select_style.setCurrentIndex(index)
        else:self.select_style.setCurrentIndex(index)
        # 切换拾取方式
        info = ["已切换为点拾取方式","已切换为壳拾取方式","已切换为实体拾取方式","当前无拾取方式",]
        try:
            if index == 0:self.interactorstyle = PointPickInteractorStyle(self)
            elif index == 1:self.interactorstyle = CellPickInteractorStyle(self)
            elif index == 2:self.interactorstyle = SolidPickInteractorStyle(self)
            else:self.interactorstyle = InteractorStyle()
            self.interactorstyle.SetDefaultRenderer(self.renderer)
            self.interactor.SetInteractorStyle(self.interactorstyle)
            self.interactor.Initialize()
        except Exception as e:
            print(e)
        self.put_info(info[index])


    def selectorAction(self, checked):
        self.selector.setVisible(checked)


    def screenShot(self):
        files, filetype = QFileDialog.getSaveFileName(self, "选择路径", "screen_shot", "*.png;;*.jpg;;*.jpeg;;*.bmp")
        if len(files) <= 0:
            return
        res = self.outputCVImage(self.renderer.GetRenderWindow(),files)
        if res is True:
            self.put_info(f"截取图像于:{files}")
            return
        self.put_error(f"截取出错:{res}")






    def workingStructAction(self, checked):
        self.working_struct_pop.setVisible(checked)


    @staticmethod
    def normalProcessing(output_port):
        normal = vtk.vtkPolyDataNormals()
        normal.SetInputConnection(output_port)
        normal.SetFeatureAngle(45)
        normal.ConsistencyOff()
        normal.NonManifoldTraversalOn()
        normal.SplittingOn()
        normal.ComputePointNormalsOn()
        normal.ComputeCellNormalsOn()
        normal.FlipNormalsOff()
        normal.Update()

        return normal




    def loadVtkModel(self, filename):
        reader = vtk.vtkSTLReader()
        # 获取类型文件
        type_ = filename.split(".")[-1]
        # 读取obj文件
        if type_ in ["obj", "OBJ"]:
            reader = vtk.vtkOBJReader()
        elif type_ in ["ply", "PLY"]:
            reader = vtk.vtkPLYReader()
        reader.SetFileName(filename)
        reader.Update()
        # 创建特征边
        edges = vtk.vtkFeatureEdges()
        edges.SetInputConnection(reader.GetOutputPort())
        edges.ColoringOff()
        # 创建Mapper和Actor
        edges_mapper = vtk.vtkPolyDataMapper()
        edges_mapper.SetInputConnection(edges.GetOutputPort())
        edges_actor = vtk.vtkActor()
        edges_actor.SetMapper(edges_mapper)
        #设置边的颜色
        edges_actor.GetProperty().SetColor(0, 0, 0)
        edges_actor.GetProperty().SetLineWidth(2.5)
        #进行法线处理-光滑模型
        normal = self.normalProcessing(reader.GetOutputPort())
        # 创建VTK对象的可视化器
        solid_mapper = vtk.vtkPolyDataMapper()
        solid_mapper.SetInputData(normal.GetOutput())
        # 创建一个演员并将其添加到渲染器中
        solid_actor = vtk.vtkActor()
        solid_actor.SetMapper(solid_mapper)
        solid_property = solid_actor.GetProperty()
        solid_property.SetDiffuse(0.5)
        solid_property.SetAmbient(0.6)
        solid_property.SetSpecular(0.5)
        # 创建一个边界框
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(reader.GetOutputPort())
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(outline_mapper)

        return solid_actor,edges_actor,outline_actor

    def read_format(self, file, type="116"):
        temps = []
        file_type = str(file).split(".")[-1]
        if file_type=="txt":
            with open(file, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    try:
                        x, y, z, vx, vy, vz = (line.split(","))
                        print( x, y, z, vx, vy, vz)
                        self.auto_window.addPulsePiont(float(x), float(y), float(z))
                        self.pulse_window.addPulsePiont(float(x), float(y), float(z))
                        self.PULSE_COORD.append([float(x), float(y), float(z)])
                    except Exception as e:
                        print(e)
        else:
            with open(file, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    temps.append(line.split(";")[0])
                for temp in temps:
                    line = temp.split(",")
                    if line[0] == type:
                        x, y, z = float(line[1]), float(line[2]), float(line[3])
                        self.auto_window.addPulsePiont(x, y, z)
                        self.pulse_window.addPulsePiont(x, y, z)
                        self.PULSE_COORD.append([x, y, z])

    def FORTRANH(self,pulse_time,Pm):
        return f"""
!*************************************************!
!  PROGRAM VDLOAD.FOR                             !
!  WRITED BY KONG CHUIJIANG                       !
!  DETAIL USE PYTHON TO generate                  !
!*************************************************!

C User subroutine VDLOAD
      subroutine VDLOAD (
C Read only (unmodifiable) variables -
      *     nblock, ndim, stepTime, totalTime,
      *     amplitude, curCoords, velocity, dircos,
      *     jltyp, sname,
C Write only (modifiable) variable -
      *     value )
      include 'vaba_param.inc'
      dimension curCoords(nblock,ndim),
      *     velocity(nblock,ndim),
      *     dircos(nblock,ndim,ndim),
      *     value(nblock)
      character*80 sname
      real Pm,period
      Pm = {Pm}
      period = {pulse_time}
      DO k=1,nblock
          Pos=FLOOR(stepTime/period)+1"""

    def generateFortranCode(self):
        if len(self.ui.single_pulse_time.text())<=0 or \
                len(self.coordinates)<=0:
            QMessageBox.warning(self, "Data Error", "Please check that the data is correct!", QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes)
            return
        file, filetype = QFileDialog.getSaveFileName(self, "Save as*.for file", "vdload.for", "*.for")
        if len(file) <= 0:
            return
        #判断时间是否正确
        pulse_time = 3E-6
        ALLPROGRAM = ""
        try:
            pulse_time=self.ui.single_pulse_time.text()
            pulse_max=self.ui.pulse_max.text()
            pluse_size = self.ui.single_pulse_size.text()
            Header = "IF"
            with (open(file, "w") as fp):
                ALLPROGRAM += self.FORTRANH(pulse_time,pulse_max)
                for coordinate in self.coordinates:
                    index = self.coordinates.index(coordinate) + 1
                    if index != 1:
                        Header = "ELSEIF"
                    ALLPROGRAM += f"""
          {Header}(Pos.EQ.{index})THEN
              Dx = {coordinate[0]}-curcoords(k,1)
              Dy = {coordinate[1]}-curcoords(k,2)
              Dz = {coordinate[2]}-curcoords(k,3)
              Radius = ABS(SQRT(Dx*Dx+Dy*Dy))
              IF(Radius.LT.{pluse_size})THEN
                  value(k)=Pm*amplitude
              ELSE
                  value(k)=0
              ENDIF"""
                ALLPROGRAM += """
          ENDIF
      ENDDO
      RETURN
      END"""
                fp.write(ALLPROGRAM)
                QMessageBox.information(self, "Generate successfully", f"The Fortran code has been generated to the root dir(vdload.for)！",
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes)

        except Exception as e:
            self.statusbar.showMessage(F"ERROR:{e}",3000)


    def openIGSFile(self):
        try:
            file, filetype = QFileDialog.getOpenFileNames(self, "打开*.IGS文件",
                                                          "",
                                                          "*.igs;;*.txt",
                                                          options=QFileDialog.DontUseNativeDialog)
            if len(file) <= 0:
                return
            for index in range(len(file)):
                self.read_format(file[index])
            # self.ui.filepath.setText(file)
            # self.ui.filepath.setToolTip(file)
            # return
            # temps, coordinates,inner_coords = [], [], []
            # with open(file, "r") as fp:
            #     lines = fp.readlines()
            #     for line in lines:
            #         temps.append(line.split(";")[0])
            #     for temp in temps:
            #         line = temp.split(",")
            #         if line[0]=="116":
            #             x,y,z = float(line[1]),float(line[2]),float(line[3])
            #             self.auto_window.addPulsePiont(x,y,z)
            #             self.pulse_window.addPulsePiont(x,y,z)
            #             self.PULSE_COORD.append([x,y,z])
            # 绘制路径
            self.drawPulses()
            # 绘制冲击路径
            self.drawPulsePath()

        except  Exception as e:
            print(e)


    def drawPulsePath(self):
        if not self.show_path.isChecked():
            return
        if len(self.PULSE_PATH_ACTORS)>0:
            for actor in self.PULSE_PATH_ACTORS:
                self.renderer.RemoveActor(actor)
        # 创建一个vtkPoints对象，用于存储路径上的坐标点
        points = vtk.vtkPoints()
        # 添加多个坐标点到vtkPoints对象中
        for i in self.PULSE_COORD:
            points.InsertNextPoint(i)
        # 创建一个vtkCellArray对象，用于存储路径上的连接关系
        lines = vtk.vtkCellArray()
        # 添加连接关系到vtkCellArray对象中
        line = vtk.vtkLine()
        for i in range(points.GetNumberOfPoints() - 1):
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i + 1)
            lines.InsertNextCell(line)
            # 绘制文本标签
            atext = vtk.vtkVectorText()
            atext.SetText(f"P{i}")
            textMapper = vtk.vtkPolyDataMapper()
            textMapper.SetInputConnection(atext.GetOutputPort())
            _actor = vtk.vtkFollower()
            _actor.SetMapper(textMapper)
            _1,_2,_3 = (
                self.PULSE_COORD[i][0]+0.5,
                self.PULSE_COORD[i][1]+0.5,
                self.PULSE_COORD[i][2]+0.5
                )
            _actor.AddPosition(_1,_2,_3)
            _actor.SetCamera(self.renderer.GetActiveCamera())  # 文本始终正面显示
            self.renderer.AddActor(_actor)
            self.PULSE_PATH_ACTORS.append(_actor)


        # 创建一个vtkPolyData对象，用于存储路径的几何信息
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)
        # 创建一个vtkPolyDataMapper对象，用于将vtkPolyData对象转换为可视化对象
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        # 创建一个vtkActor对象，用于显示路径
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        self.PULSE_PATH_ACTORS.append(actor)
        self.vtkWidget.update()


    def pulseAxes(self, position):
        # 创建坐标系Actor
        size = self.MODEL_DES["boundsize"]
        # 创建一个vtkAxesActor
        axes = vtk.vtkAxesActor()
        axes.AxisLabelsOff()
        axes.SetConeRadius(.0)
        axes.SetTotalLength(size/15, size/15, size/15)
        # axes.GetZAxisShaftProperty().SetColor(1,0,0)


        return axes


    def packager(self, actors, position):
        # 创建一个装配体
        assembly = vtk.vtkAssembly()
        for actor in actors:
            assembly.AddPart(actor)
        # 创建一个transform对象
        transform = vtk.vtkTransform()
        transform.Translate(position[0], position[1], position[2])
        assembly.SetUserTransform(transform)
        self.PULSE_COORD_SYSTEM.append(assembly)
        self.renderer.AddActor(assembly)

        return assembly


    def normalPulser(self, pulser, index, vector, update=False):
        if update:
            transform = vtk.vtkTransform()
            # 计算坐标系Z轴与指定向量的夹角
            z_axis = [0, 0, 1]  # Z轴方向向量
            rotation_axis = [0, 0, 0]  # 旋转轴
            vtk.vtkMath.Cross(z_axis, vector[index], rotation_axis)  # 计算旋转轴
            angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(z_axis, vector[index]))  # 计算旋转角度
            transform.RotateWXYZ(angle, rotation_axis[0], rotation_axis[1], rotation_axis[2])  # 根据旋转轴和角度进行旋转
            pulser.SetUserTransform(transform)




    def drawPulses(self, update=False, vector=[]):
        if not self.show_local_coordinate.isChecked():
            return
        #重新删除，重绘
        for actor in self.PULSE_COORD_SYSTEM:
            self.renderer.RemoveActor(actor)
        self.PULSE_COORD_SYSTEM.clear()
        # 根据冲击点绘制坐标系
        for pos in self.PULSE_COORD:
            # 获得法向量
            index = self.PULSE_COORD.index(pos)
            pulse_coord_sys = self.pulseAxes(pos)
            self.normalPulser(pulse_coord_sys, index, vector, update)
            pulser = self.packager([pulse_coord_sys],pos)
        self.vtkWidget.update()



    def openModel(self, file=None, Msg=False):
        if not file:
            Msg = True
            file, filetype = QFileDialog.getOpenFileName(self, "选择模型", "", MODELINPUT)
            if len(file)<=0:
                return
        self.ui.model_path.setText(file)
        try:
            """
            mesh = readModel(file)
            # print(mesh.points)
            # 模型的子对象
            self.part_instance_folder = QTreeWidgetItem(self.parts_folder, [f"{self.getFileName(file)}<实体>"])
            self.points_folder = QTreeWidgetItem(self.part_instance_folder, [f"{self.getFileName(file)}<结点集({len(mesh.points)})>"])
            self.cells_folder = QTreeWidgetItem(self.part_instance_folder,[f"{self.getFileName(file)}<单元集({len(mesh.cells)})>"])
            # 将网格保存为VTK通用文件
            writeModel("cache/curt.vtk", mesh)
            actor = self.loadVtkModel("cache/curt.vtk")
            """
            solid, edges, outline = self.loadVtkModel(file)
            self.MODEL_DES["edges"] = edges
            self.MODEL_DES["boundary"] = outline
            solid.GetProperty().SetEdgeVisibility(False)
            solid.GetProperty().SetColor(0.110, 0.460, 0.8)
            # 存储文件名到用户数据
            self.clearAllActor()
            # 设置坐标系的初始大小
            bounds = list(solid.GetBounds())
            size = ((bounds[0]-bounds[3])**2+(bounds[1]-bounds[4])**2+(bounds[2]-bounds[5])**2)**0.5
            self.mainaxes.SetTotalLength(size/10,size/10,size/10)
            self.MODEL_DES["boundsize"] = size
            self.renderer.AddActor(solid)
            self.renderer.AddActor(edges)
            self.vtkWidget.update()
            self.renderer.Render()
            self.renderer.ResetCamera()
            if not Msg:
                return
            # 导入管理器显示
            model_index = len(self.MODEL_LIST) + 1
            model_data = [f"Model-{model_index}", "3D-导入", file]
            # 导入模型树显示
            self.addDataToTree(self.parts_folder, f"Model-{model_index}", file)
            self.MODEL_LIST.append(model_data)
            # 提示信息
            self.put_info(f"The model was successfully imported:{file}")
            QMessageBox.information(self, "模型导入成功", f"已删除原有模型，并成功导入模型:{file}",
                                    QMessageBox.Yes | QMessageBox.No)

        except Exception as e:
            self.ui.statusbar.showMessage(f"文件:'{file}'导入错误:'{e}'!", 4000)
            self.put_error(f"文件:'{file}'导入错误:'{e}'!")



    def clearAllActor(self):
        actors = self.renderer.GetActors()
        for actor in actors:
            self.renderer.RemoveActor(actor)


    @staticmethod
    def getFileName(_path):
        try:return (_path.split("/")[-1]).split(".")[0]
        except:return "None"



    def showAbaqusVersion(self):
        ver = Version()   #返回字典 键值OV IV
        v = ver()
        if len(v.keys())<=0:
            QMessageBox.critical(self,"Abaqus检测","未检测到Abaqus相关信息,请检查或重新安装!",QMessageBox.Yes|QMessageBox.No)
            return -1
        QMessageBox.information(self, "Abaqus检测", f"Official Version:{v['OV']}\nInternal Version:{v['IV']}",QMessageBox.Yes|QMessageBox.No)
        self.put_info(f"Official Version:{v['OV']} Internal Version:{v['IV']}")



    def initAbaqusGenerator(self):
        datas = {
            "WorkingDir":self.working.text(),
            "ModelPath":str(self.parts_manager_dialog.CURRENT).replace(".STL",".STEP"),
            "Density":"4.56E-9",
            "Young":"110000",
            "Possion":"0.3",
            "Yield_Stress":"890",
            "Plastic_Strain":"0",
            "A":"1234",
            "B":"1123",
            "n": "0.01",
            "m": "1.2",
            "C": "0.024",
            "Epsilon": "1",
            "Melting_Temp": "1232",
            "Transition_Temp": "890",
            "Mesh_Size":"2.5",
            "Cpus":"8",
            "Mesh_Shape":"TET"

        }
        self.abaqus_python_generator.setMustDatas(_datas=datas)
        # self.abaqus_python_generator.setWorkingDir(self.working.text())


    def runAbaqus(self):
        try:
            self.initAbaqusGenerator()

            self.ui.abaqus_script.setText(self.abaqus_python_generator.generate())

            # 获取abaqus的运行方式
            ifgui = True if self.ui.gui.isChecked() else False
            abaqus_script = self.ui.abaqus_script.text()
            if len(abaqus_script)<=0:
                QMessageBox.information(self, "Abaqus脚本",
                                        f"没有供Abaqus运行的脚本！",
                                        QMessageBox.Yes | QMessageBox.No)

                return
            args = F"abaqus cae {'script' if ifgui else 'noGUI'}={abaqus_script}"
            self.ui.statusbar.showMessage(f"Abaqus运行参数:{args},启动中...",3000)
            self.put_info(f"Abaqus运行参数:{args},启动中...")

            abaqus = ABARun()
            # abaqus.run(args) #运行abaqus
            abaqus_process = Process(target=abaqus.run,args=(args,))
            abaqus_process.start()
        except Exception as e:
            print(e)


    def childrenWindows(self):
        # 模型对象窗口对象
        self.parts_manager_dialog = PartsManager(self)
        # 新建属性的窗口
        self.new_property_window = PropertyManager(self)
        # 窗口弹出模板
        self.template_window = TemplatePop(self)
        # 自动运行窗口
        self.auto_window = AutorunManager(self)
        # 渲染窗口管理窗口
        self.viewport_manager_window = ViewportManager(self)
        # LSP路径管理
        self.pulse_window = PulseManager(self)
        # LSP平板实例管理
        self.plane_pulse_window = PlanePulseManager(self)
        # LSP后处理管理
        self.extractor_window = ExtractorManager(self)
        # LS监控
        self.monitor_window = MonitorManager(self)
        # 设置窗口
        self.settings_window = Settings(self)


    def propertyArgTabelInit(self):
        # 已经设置的属性值
        self.ui.property_args.resizeColumnToContents(2)
        self.ui.property_args.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应窗口宽度
        self.ui.property_args.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # 第一列自适应内容
        self.ui.property_args.verticalHeader().setVisible(False)
        self.ui.property_args.setShowGrid(False)
        # QTableWidget设置整行选中
        self.ui.property_args.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.property_args.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.property_args.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 右键初始化


    def guiInit(self):
        # 初始化新建窗口
        # self.childrenWindows()
        # 打印欢迎日志
        self.put_info("Welcom!")
        self.movie = QMovie('bin/graphics/start_logo.gif')
        self.movie.setSpeed(350)
        self.ui.start.setMovie(self.movie)
        self.movie.start()
        self.ui.start.setFixedHeight(80)
        # 去除左边窗口的窗口边框
        for ob in [self.ui.left,self.ui.right,self.ui.left_up,self.ui.bottom]:
            _ = QFrame(self)
            ob.setTitleBarWidget(_)
            del _

        # 默认工作路径
        self.working.setText(os.path.join(os.getcwd(),"cache"))
        self.modulesInit()
        # self.ui.module_widget.setCornerWidget(self.modules,Qt.TopRightCorner)
        #安装命令行窗口的事件监听器
        self.ui.commands.installEventFilter(self)
        self.ui.commands.append(f"<a style='color:#dfdfdf;'>{os.getcwd()}></a>")
        # 隐藏视口操作bar
        self.ui.viewer_process_frame.hide()
        # 设置dock栏的窗口
        self.ui.right.resize(380,472)
        # 设置打开模型管理器的按钮为可选中
        self.ui.parts_manager.setCheckable(True)
        # 初始化属性参数界面
        self.propertyArgTabelInit()


        # 设置底部的窗口标题栏部件
        self.bottom_widget = QWidget(self)
        layout = QHBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0,0,0,5)
        start_logo = QIcon(":/graphics/start_logo.png")
        logo = QToolButton(self)
        logo.setIcon(start_logo)
        logo.setIconSize(QSize(75,35))
        logo.setStyleSheet("QToolButton{background:rgba(0,0,0,0);}")
        layout.addWidget(logo)
        soft_label = QLabel("Focus FEM Helper-1.0.1")
        soft_label.setFont(QFont("微软雅黑",9))
        layout.addWidget(soft_label)

        self.bottom_widget.setLayout(layout)
        # self.ui.bottom.setTitleBarWidget(self.bottom_widget)
        self.ui.interacter_widget.setCornerWidget(self.bottom_widget)

        #视口窗口右键菜单
        self.ui.viewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.viewer.customContextMenuRequested.connect(self.viewportRightClick)  # 连接到菜单显示函数



    def viewportRightClick(self):
        # 菜单对象
        self._menu = QMenu(self)
        self._menu.triggered.connect(self.viewportRightActions)

        self.reset_camera = QAction(QIcon(":/graphics/reset_camera.png"), u"重置视角", self)
        self._menu.addAction(self.reset_camera)
        self.rotation_center = QAction(QIcon(":/graphics/rotation_center.png"), u"设置旋转中心", self)
        self._menu.addAction(self.rotation_center)

        self._menu.popup(QCursor.pos())


    def viewportRightActions(self,action):
        if action is self.reset_camera:
            pass
        elif action is self.rotation_center:
            pass




    def modulesInit(self):
        module_names = ["Model","Properties","Mesh","Analyze"]
        # 这里设置窗口的标题
        self.changeModule(0)
        module_w = QWidget(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.modules_label = QLabel("Module:", self)
        self.modules = QComboBox(self)
        self.modules.setFont(QFont("微软雅黑",9))
        self.modules.setStyleSheet("QComboBox::item {height: 25px;}")
        self.modules.setView(QListView())
        self.modules.setMinimumWidth(150)
        self.modules.addItems(module_names)
        self.modules.currentIndexChanged.connect(self.changeModule)
        layout.addWidget(self.modules_label)
        layout.addWidget(self.modules)
        module_w.setLayout(layout)
        self.ui.module_widget.setCornerWidget(module_w, Qt.TopRightCorner)


    def hideAllModuleTab(self):
        for i in range(self.ui.module_widget.count()):
            self.ui.module_widget.tabBar().setTabVisible(i,False)

    def changeModule(self,index):
        self.hideAllModuleTab()
        self.ui.module_widget.setCurrentIndex(index)
        self.ui.module_widget.tabBar().setTabVisible(index, True)
        # self.ui.module_widget.count()



    @staticmethod
    def outputCVImage(renw,path="Tst_image.png"):
        try:
            window_to_image_filter = vtk.vtkWindowToImageFilter()
            window_to_image_filter.SetInput(renw)
            window_to_image_filter.SetInputBufferTypeToRGB()
            window_to_image_filter.Update()
            image = window_to_image_filter.GetOutput()
            rows, cols, _ = image.GetDimensions()
            scalars = image.GetPointData().GetScalars()
            arr = vtk_to_numpy(scalars).reshape(cols, rows, -1)[..., ::-1]

            cv2.imencode('.png', cv2.flip(arr, 0))[1].tofile(path)

        except Exception as e:
            return e
        return True


    @staticmethod
    def axes():
        axes_actor = vtk.vtkAxesActor()
        axes_actor.SetTotalLength(1, 1, 1)
        axes_actor.SetShaftType(1)
        axes_actor.SetCylinderRadius(0.02)

        return axes_actor
    @staticmethod
    def text2d():
        # 提示信息
        LineText = vtk.vtkTextMapper()
        LineText.SetInput("Left mouse button: Rotate the view\nMiddle mouse button: Move the view\nRight-click to zoom")
        tprop = LineText.GetTextProperty()
        tprop.SetVerticalJustificationToBottom()
        tprop.SetColor(0.8, 0.8, 0.8)
        tprop.SetFontSize(20)
        tiptext = vtk.vtkActor2D()
        tiptext.SetMapper(LineText)
        tiptext.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        tiptext.GetPositionCoordinate().SetValue(0.02, 0.90)

        return tiptext


    @staticmethod
    def vtext():
        # 版本信息
        vLineText = vtk.vtkTextMapper()
        vLineText.SetInput("Focus-2023 Beta.")
        vtprop = vLineText.GetTextProperty()
        vtprop.SetVerticalJustificationToBottom()
        vtprop.SetColor(0.8,0,0)
        vtprop.SetFontSize(28)
        vtiptext = vtk.vtkActor2D()
        vtiptext.SetMapper(vLineText)
        vtiptext.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        vtiptext.GetPositionCoordinate().SetValue(0.02, 0.02)

        return vtiptext

    def right_top_widget(self, _swith=True):
        if _swith:
            self.right_top_axes_widget.EnabledOn()
        else:
            self.right_top_axes_widget.EnabledOff()

    def left_bottom_widget(self, _swith=True):
        if _swith:
            self.left_bottom_axes_widget.EnabledOn()
        else:
            self.left_bottom_axes_widget.EnabledOff()

    def orientationWidget(self):
        # 右上角视图
        self.right_top_axes_widget = vtk.vtkCameraOrientationWidget()
        self.right_top_axes_widget.SetParentRenderer(self.renderer)
        self.right_top_axes_widget.SetInteractor(self.vtkWidget.GetRenderWindow().GetInteractor())
        self.right_top_axes_widget.EnabledOn()
        # 左下角坐标轴
        self.left_bottom_axes_widget = vtk.vtkOrientationMarkerWidget()
        self.left_bottom_axes_widget.SetOrientationMarker(self.axes())
        self.left_bottom_axes_widget.SetDefaultRenderer(self.renderer)
        self.left_bottom_axes_widget.SetInteractor(self.vtkWidget.GetRenderWindow().GetInteractor())
        self.left_bottom_axes_widget.EnabledOn()
        self.left_bottom_axes_widget.InteractiveOff()


    @staticmethod
    def mainlight():
        main_light = vtk.vtkLight()
        main_light.SetLightType(1)
        main_light.SetIntensity(0.5)
        main_light.SetColor(0.85, 0.85, 0.85)

        # main_light.SetPosition(1, 1, 1)
        # main_light.SetFocalPoint(self.renderer.GetActiveCamera().GetFocalPoint())
        main_light.SetLightTypeToCameraLight()

        return main_light


    @staticmethod
    def mainAxes():
        # 创建一个vtkAxesActor
        axes = vtk.vtkAxesActor()
        # axes.AxisLabelsOff()
        axes.SetConeRadius(.0)
        axes.SetTotalLength(10,10,10)
        caption_x = axes.GetXAxisCaptionActor2D()
        caption_y = axes.GetYAxisCaptionActor2D()
        caption_z = axes.GetZAxisCaptionActor2D()
        for caption in [caption_x,caption_y,caption_z]:
            caption.GetTextActor().SetTextScaleModeToNone()
            caption.GetCaptionTextProperty().SetFontSize(18)
            caption.GetCaptionTextProperty().SetColor(1,0.6,0.07)
        # 223, 232, 20
        axes.GetXAxisShaftProperty().SetColor(1,0.6,0.07)
        axes.GetYAxisShaftProperty().SetColor(1,0.6,0.07)
        axes.GetZAxisShaftProperty().SetColor(1,0.6,0.07)

        return axes


    def vtkRenderWindowInit(self):
        self.vtkFrame = QWidget()
        self.vtkWidget = QVTKRenderWindowInteractor(self.vtkFrame)
        sub = QMdiSubWindow()
        sub.setWidget(self.vtkWidget)
        self.ui.viewer.addSubWindow(sub)
        # self.ui.viewer.setViewMode(1)
        sub.showMaximized()
        sub.setWindowIcon(QIcon(":/graphics/viewport.png"))
        sub.setWindowTitle(f"Render View-{len(self.ui.viewer.subWindowList())}")
        self.viewport_manager_window.addViewportData(sub)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().SetMultiSamples(4)  # 启用4倍多重采样
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        # 视图的局部
        self.orientationWidget()
        # 自定义交互方式
        self.interactorstyle = InteractorStyle(self)
        self.interactorstyle.SetDefaultRenderer(self.renderer)
        self.interactor.SetInteractorStyle(self.interactorstyle)
        self.interactor.Initialize()
        # 添加灯光
        self.renderer.AddLight(self.mainlight())
        self.mainaxes = self.mainAxes()
        self.interactorstyle.setFixedAxes(self.mainaxes)
        # self.mainaxes.SetCoordinateSystemToNormalizedDisplay()
        self.renderer.AddActor(self.mainaxes)
        self.ACTORS_2D = [self.text2d(),self.vtext()]
        self.renderer.AddActor2D(self.ACTORS_2D[0])
        self.renderer.AddActor2D(self.ACTORS_2D[1])

        # 开启渐变
        # self.renderer.SetBackground(1, 1, 1)
        self.renderer.SetBackground(.8, .8, .8)  # 设置页面底部颜色值
        self.renderer.SetBackground2(.1, .2, .4)  # 设置页面顶部颜色值
        self.renderer.SetGradientBackground(True)  # 开启渐变色背景设置

        self.renderer.UseDepthPeelingOn()
        self.renderer.SetUseFXAA(False)

        self.vtkWidget.update()
        self.interactor.Initialize()


    def datasTreeInit(self):
        self.ui.data_tree.doubleClicked.connect(self.dataTreedoubleClickedEvents)
        self.ui.data_tree.setDragEnabled(False)
        # self.ui.data_tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree_root = self.ui.data_tree
        #模型的根路径
        self.models_folder = QTreeWidgetItem(self.tree_root, ["Model"])
        self.models_folder.setIcon(0, QIcon(":/graphics/model.png"))
        # 模型的子对象
        self.parts_folder = QTreeWidgetItem(self.models_folder, ["Solid"])
        self.parts_folder.setIcon(0, QIcon(":/graphics/model.png"))

        self.attribute_folder = QTreeWidgetItem(self.models_folder, ["Properties"])
        self.attribute_folder.setIcon(0, QIcon(":/graphics/attribute.png"))

        self.assemblies_folder = QTreeWidgetItem(self.models_folder, ["Assembly"])
        self.assemblies_folder.setIcon(0, QIcon(":/graphics/assemblies.png"))

        self.steps_folder = QTreeWidgetItem(self.models_folder, ["Step"])
        self.steps_folder.setIcon(0, QIcon(":/graphics/step.png"))

        self.loads_folder = QTreeWidgetItem(self.models_folder, ["Load"])
        self.loads_folder.setIcon(0, QIcon(":/graphics/force.png"))

        self.boundary_folder = QTreeWidgetItem(self.models_folder, ["Boundary"])
        self.boundary_folder.setIcon(0, QIcon(":/graphics/boundary.png"))
        # 工作的根路径
        self.ansys_folder = QTreeWidgetItem(self.tree_root, ["Analyze"])
        self.ansys_folder.setIcon(0, QIcon(":/graphics/work.png"))
        self.jobs_folder = QTreeWidgetItem(self.ansys_folder, ["Job"])
        self.jobs_folder.setIcon(0, QIcon(":/graphics/jobs.png"))
        # 可视化的根路径
        self.visualization_folder = QTreeWidgetItem(self.tree_root, ["Visualization"])
        self.visualization_folder.setIcon(0, QIcon(":/graphics/chart.png"))

        self.liner_folder = QTreeWidgetItem(self.visualization_folder, ["Data Extraction"])
        self.liner_folder.setIcon(0, QIcon(":/graphics/extract.png"))
        # 展开树
        self.ui.data_tree.expandAll()

    def addDataToTree(self, root ,data, tooltip=None):
        item = QTreeWidgetItem(root, [data])
        item.setToolTip(0,tooltip)


    def popShowerDialog(self,info:str):
        dat_info = QDialog(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # 显示器设置
        infer = QTextBrowser(self)
        infer.setFont(QFont("微软雅黑", 10))
        infer.setText(info)
        layout.addWidget(infer)
        dat_info.setLayout(layout)
        dat_info.resize(1000, 650)
        dat_info.setWindowTitle("数据显示")
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        dat_info.setWindowModality(Qt.ApplicationModal)
        dat_info.exec_()
    def dataTreedoubleClickedEvents(self,object:QModelIndex):
        try:
            curt_item = self.ui.data_tree.currentItem()
            if curt_item is self.points_folder:
                self.popShowerDialog("None")
        except Exception as error:
            pass

    """
    处理按钮点击的事件
    """
    def buttonClickEvents(self):
        # self.ui.abaqty_start.clicked.connect(lambda :Popen(r"explorer start C:\KNG\Preject\Python\Focus\bin\helps"))
        # 检查Abaqus版本信息
        self.ui.abaqus_version.clicked.connect(self.showAbaqusVersion)
        # 自定义abaqus运行脚本
        self.ui.abaqus_script_customize.clicked.connect(lambda :\
        self.ui.abaqus_script.setEnabled(self.ui.abaqus_script_customize.isChecked()))
        # 运行abaqus
        self.ui.run_abaqus.clicked.connect(self.runAbaqus)
        # 打开模型
        self.ui.open_model.clicked.connect(self.openModel)
        #显示网格
        self.ui.grid.clicked.connect(self.showPartsGrid)
        #只显示为线框
        self.ui.waveframe.clicked.connect(self.onlyWaveframe)
        #显示为正常模式
        self.ui.solid.clicked.connect(self.onlySolid)
        # 显示为点云
        self.ui.points_cloud.clicked.connect(self.onlyPointsCloud)
        #显示模型的边界框
        self.ui.model_boundary.clicked.connect(self.showBoundaryBox)
        # 显示模型的边线
        self.ui.model_outline.clicked.connect(self.showOutline)
        # parts管理
        self.ui.parts_manager.clicked.connect(self.partsManagerPop)
        # 弹出新建属性的查询窗口
        self.ui.new_property.clicked.connect(self.propertyManagerPop)
        self.ui.property_manager.setEnabled(False)

    def propertyManagerPop(self,checked):
        self.new_property_window.setVisible(checked)


    def partsManagerPop(self,checked):
        # 清空元有的数据重新加上
        # self.parts_manager_dialog.ui.parts_list.clear()
        self.parts_manager_dialog.ui.parts_list.setRowCount(0)
        self.parts_manager_dialog.setVisible(checked)
        for dt in self.MODEL_LIST:
            self.parts_manager_dialog.addPartsDetails(dt)


    def showBoundaryBox(self,checked):
        if not self.MODEL_DES["boundary"]:
            return
        if checked and not self.MODEL_DES["boundary"] in self.renderer.GetActors():
            self.renderer.AddActor(self.MODEL_DES["boundary"])
        elif not checked and self.MODEL_DES["boundary"] in self.renderer.GetActors():
            self.renderer.RemoveActor(self.MODEL_DES["boundary"])
        self.vtkWidget.update()
    def showOutline(self, checked):
        if not self.MODEL_DES["edges"]:
            return
        if checked and not self.MODEL_DES["edges"] in self.renderer.GetActors():
            self.renderer.AddActor(self.MODEL_DES["edges"])
        elif not checked and self.MODEL_DES["edges"] in self.renderer.GetActors():
            self.renderer.RemoveActor(self.MODEL_DES["edges"])
        self.vtkWidget.update()

    def onlyPointsCloud(self):
        # 操作
        self.gridview_style.setChecked(False)
        self.points_style.setChecked(True)

        actors = self.renderer.GetActors()
        for actor in actors:
            actor.GetProperty().SetRepresentationToPoints()
            actor.GetProperty().SetPointSize(4)
        self.renderer.Render()
        self.vtkWidget.update()

    def showPartsGrid(self, checked):
        #遍历所有的Actor
        actors = self.renderer.GetActors()
        for actor in actors:
            actor.GetProperty().EdgeVisibilityOn() if checked else actor.GetProperty().EdgeVisibilityOff()
        self.renderer.Render()
        self.vtkWidget.update()

    def onlyWaveframe(self):
        self.gridview_style.setChecked(True)
        self.points_style.setChecked(False)
        # 遍历所有的Actor
        actors = self.renderer.GetActors()
        for actor in actors:
            actor.GetProperty().SetRepresentationToWireframe()
        self.renderer.Render()
        self.vtkWidget.update()

    def onlySolid(self):
        # 操作
        self.gridview_style.setChecked(False)
        self.points_style.setChecked(False)
        # 遍历所有的Actor
        actors = self.renderer.GetActors()
        for actor in actors:
            actor.GetProperty().SetRepresentationToSurface()
            # actor.GetProperty().SetEdgeVisibility(1)
        self.renderer.Render()
        self.vtkWidget.update()



    """
    初始化各个尺寸的大小
    """
    def sizeInit(self):
        # 默认最大化窗口
        desktop = QApplication.desktop()
        self.resize(int(desktop.width()*0.85),int(desktop.height()*0.8))
        self.move(int(desktop.width()*(0.075)),int(desktop.height()*(0.1)))
        # 设置坐标操作窗口的最小尺寸
        self.ui.left.setMinimumWidth(150)
        self.ui.right.setMinimumWidth(150)
        self.ui.bottom.setMinimumHeight(150)
        # 设置menubar的
        self.ui.menubar.setMinimumHeight(35)


    def closeEvent(self, event):
        reply = QMessageBox.information(self,'退出',"是否要退出程序，请确保信息已经保存！",QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.terminateALLCmd()

        else:
            event.ignore()

    def put_error(self, error):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.messager.insertHtml(f"<a style='color:#FF0000;'><strong>[Error] </strong></a> <a style='color:#000000;'>{now}  </a> {error}<br>")
    def put_warning(self, warning):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.messager.insertHtml(f"<a style='color:#FF7F00;'><strong>[Warning] </strong></a> <a style='color:#000000;'>{now}  </a> {warning}<br>")
    def put_info(self, normal):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.messager.insertHtml(f"<a style='color:#9B30FF;'><strong>[Info] </strong></a> <a style='color:#000000;'>{now}  </a> {normal}<br>")

    def eventFilter(self, object, event):
        if object == self.ui.commands and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Backspace:
                if self.ui.commands.textCursor().columnNumber() <= 3:
                    return True
            elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                line = self.ui.commands.document().lineCount()
                current_command = self.ui.commands.document().findBlockByLineNumber(line - 1).text()
                command = current_command.replace(f"{os.getcwd()}>", "")
                if command == "":
                    self.ui.commands.append(f"<a style='color:#dfdfdf;'>{os.getcwd()}></a>")
                    return True
                try:
                    _C = Commands(self)
                    getattr(_C, command)
                except Exception as e:
                    print(e)
                    self.ui.commands.insertHtml(f"<br><a style='color:#FF0000;'>无法将'{command}'项识别为函数、脚本文件或可运行程序的名称。请检查名称的拼写，如果包括路径，请确保路径正确，然后再试一次。<br>^^^^^</a><br>")
                # 从新加入新行
                self.ui.commands.append(f"<a style='color:#dfdfdf;'>{os.getcwd()}></a>")
                return True
            elif event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left):
                return True

        return False

def ABAQUSCHECK(switch=1)->bool:
    if not switch:return
    ver = Version()  # 返回字典 键值OV IV
    checker = QProgressDialog('正在检测是否安装ABAQUS..', '取消检查', 0, 1600, None)
    checker.setFont(QFont("微软雅黑",10))
    checker.setWindowTitle("ABAQUS版本检查")
    checker.setWindowIcon(QIcon(":/graphics/check_abaqus.png"))
    checker.setFixedSize(520,200)
    checker.setCancelButton(None)
    v = ver()
    for val in range(1600):
        time.sleep(0.001)
        checker.setValue(val)
        QCoreApplication.processEvents()
        if checker.wasCanceled():
            break
    if len(v.keys()) <= 0:
        checker.setLabelText(f"未检测到Abaqus相关信息,请检查环境变量或重新安装!\n否则将无法正常使用该软件!")
        checker.exec()
        return False
    checker.setLabelText(f"Official Version:{v['OV']}\nInternal Version:{v['IV']}")
    checker.exec()
    return True


if __name__ == '__main__':
    # 适应高DPI设备
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 解决图片在不同分辨率显示模糊问题
    # QApplication.setAttribute(Qt.AA_Use96Dpi)
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 适应windows缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # 设置支持小数放大比例（适应如125%的缩放比）
    freeze_support()
    app = QApplication(sys.argv)
    ABAQUSCHECK(False)
    win = Windows()
    win.show()
    sys.exit(app.exec_())