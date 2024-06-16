
import vtk

class SolidPickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """Actor选取交互器，color表示选中高亮actor的颜色，select_mode为0表示单选，select_mode为1表示多选"""

    def __init__(self, parent=None, color: tuple[float, float, float] = (1.0, 1.0, 0.0),
                 select_mode: int = 0):  # parent不能删掉
        super().__init__()
        self.AddObserver("LeftButtonPressEvent", self.__leftButtonPressEvent)
        self.picked_actor_list = []  # 已选取的actor列表
        self.original_color_list = []  # 已选取的actor原始颜色列表，与picked_actor_list对应
        self.color = color
        if select_mode != 0 and select_mode != 1:
            raise ValueError
        self.select_mode = select_mode

    def __leftButtonPressEvent(self, obj, event):  # obj和event参数不能删掉
        """左键单击事件"""
        click_pos = self.GetInteractor().GetEventPosition()  # 获取鼠标左键点击时的屏幕坐标
        picker = vtk.vtkPropPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, self.GetDefaultRenderer())
        picked_actor = picker.GetActor()
        if picked_actor is not None:
            # 如果选择的actor已被选，则复原
            if picked_actor in self.picked_actor_list:
                index = self.picked_actor_list.index(picked_actor)
                self.picked_actor_list[index].GetProperty().SetColor(self.original_color_list[index])
                self.picked_actor_list[index].Modified()
                self.picked_actor_list.pop(index)
                self.original_color_list.pop(index)
            # 如果选择的是新actor
            else:
                # 如果是单选模式，需要先把之前选择的actor复原
                if self.select_mode == 0 and len(self.picked_actor_list) > 0:
                    self.picked_actor_list[0].GetProperty().SetColor(self.original_color_list[0])
                    self.picked_actor_list[0].Modified()
                    self.picked_actor_list.pop(0)
                    self.original_color_list.pop(0)
                # 储存选中actor的原始颜色，并把选中的actor高亮
                picked_color = picked_actor.GetProperty().GetColor()
                self.original_color_list.append(picked_color)
                picked_actor.GetProperty().SetColor(self.color)
                picked_actor.Modified()
                self.picked_actor_list.append(picked_actor)
        self.OnLeftButtonDown()



