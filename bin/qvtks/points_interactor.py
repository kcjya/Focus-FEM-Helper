
import vtkmodules.all as vtk
from bin.qvtks.geometry import Geometry



class PointPickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """Point选取交互器，mark_size表示选中高亮点大小，mode为0表示以像素显示，mode为1表示以球体显示，color表示选中高亮颜色，single_select为0表示单选，single_select为1表示多选"""
    def __init__(self, parent):  # parent不能删掉
        super().__init__()
        self.parent_interface = parent
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("KeyReleaseEvent", self.onKeyReleaseEvent)

        self.pickerInit()
        self.valuesInit()


    def setConfig(self,config:dict)->None:
        self.pt_size = config["pt_size"]
        self.pt_color = config["pt_color"]


    def valuesInit(self):
        self.pt_size = 8
        self.pt_color = (1, 0, 0)
        # 选择模式
        self.single_select = True
        self.picked_indexes = []  # 已选取的[actor, self.pt_id]列表
        self.point_actors = []  # 已生成的高亮actor列表，与picked_cellUnit_list对应

    def pickerInit(self):
        self.picker = vtk.vtkPointPicker()
        self.picker.SetTolerance(0.005)  # 设置误差限

    def onKeyPressEvent(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        self.single_select = False
        self.OnKeyPress()

    def onKeyReleaseEvent(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        self.single_select = True
        self.OnKeyRelease()

    def getPickedIndex(self, actor: vtk.vtkActor, pt_id: int):
        try: return self.picked_indexes.index([actor,pt_id])
        except:return None

    def parentAddPointCallbackEvent(self):
        pos = self.picker.GetPickPosition()
        x,y,z = pos[0],pos[1],pos[2]
        self.parent_interface.selector.ui.select_list.addItem(f"点_{self.pt_id} 位置: [{round(x,3)}, {round(y,3)}, {round(z,3)}]")


    def clearAllSelections(self):
        for actor in self.point_actors:
            self.renderer.RemoveActor(actor)
        self.point_actors.clear()
        self.picked_indexes.clear()
        self.parent_interface.selector.ui.select_list.clear()

    def onLeftButtonPressEvent(self, obj, event):  # obj和event参数不能删掉
        self.parent_interface.ui.viewer_process_frame.show()
        # 获取鼠标左键点击时的屏幕坐标
        click_pos = self.GetInteractor().GetEventPosition()
        self.picker.Pick(click_pos[0], click_pos[1], 0, self.GetDefaultRenderer())
        self.pt_id = self.picker.GetPointId()
        if self.pt_id and self.pt_id!=-1:
            picked_actor = self.picker.GetActor()
            index = self.getPickedIndex(picked_actor,self.pt_id)
            #获取默认的渲染器
            self.renderer = self.GetDefaultRenderer()
            # 如果选择的point未被选
            if not index:
                # 如果是单选模式，需要先把之前选择的point复原
                if self.single_select and len(self.point_actors) > 0:
                    self.clearAllSelections()
                # 生成高亮actor
                highlight_point = Geometry.genPixelActor(self.picker.GetPickPosition(), self.pt_size, self.pt_color)
                highlight_point.SetPickable(False)
                self.renderer.AddActor(highlight_point)
                # 添加本地数据
                self.parentAddPointCallbackEvent()
                self.picked_indexes.append([picked_actor, self.pt_id])
                self.point_actors.append(highlight_point)
            # 如果选择的point已被选，则直接复原
            else:
                self.renderer.RemoveActor(self.point_actors[index])
                self.parent_interface.selector.ui.select_list.takeItem(index)
                self.point_actors.pop(index)
                self.picked_indexes.pop(index)
        # elif self.pt_id==-1:
        #     # 清空本地数据据
        #     self.clearAllSelections()

        self.OnLeftButtonDown()

