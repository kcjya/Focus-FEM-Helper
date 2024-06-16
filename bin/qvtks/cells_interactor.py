
import vtkmodules.all as vtk
import numpy as np
from bin.qvtks.geometry import Geometry

def genHighlightActor(polydata: vtk.vtkPolyData, cell_id: int, color: tuple[float, float, float],
                      mark_size: int = 4) -> vtk.vtkActor:
    """根据polydata和cell_id生成一个对应的actor"""
    cell = polydata.GetCell(cell_id)
    ptn = cell.GetNumberOfPoints()
    pts = np.zeros((ptn, 3), dtype=np.float64)
    for i in range(ptn):
        point_id = cell.GetPointId(i)
        polydata.GetPoint(point_id, pts[i])
    if ptn == 1:  # 如果是点
        actor = Geometry.genPixelActor(pts[0], mark_size, color)
    elif ptn == 3:  # 如果是三角形
        actor = Geometry.genTriangleFrameActor(pts, mark_size, color)
    else:  # 如果是线段或折线
        actor = Geometry.genWholeBreakLineActor(pts, mark_size, color)
    return actor


class CellPickInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """
    Cell选取交互器，mark_size表示选中高亮元素的线宽或点大小，color表示选中高亮颜色，select_mode为0表示单选，select_mode为1表示多选
    easy_to_pick若设置为True，则可以降低选取精度以更方便地选取由线和点组成的单元
    """

    def __init__(self, parent=None, mark_size: int = 4, color: tuple[float, float, float] = (1.0, 0.0, 0.0),
                 select_mode: int = 0, easy_to_pick: bool = False):  # parent不能删掉
        super().__init__()
        self.AddObserver("LeftButtonPressEvent", self.__leftButtonPressEvent)
        self.picked_cellUnit_list = []  # 已选取的[actor, cell_id]列表
        self.highlight_cellActor_list = []  # 已生成的高亮actor列表，与picked_cellUnit_list对应
        self.mark_size = mark_size
        self.color = color
        if select_mode != 0 and select_mode != 1:
            raise ValueError
        self.select_mode = select_mode
        self.easy_to_pick = easy_to_pick

    def __get_selected_cellUnit_index(self, actor: vtk.vtkActor, cell_id: int) -> int:
        """看选的cell是否在已选列表里，是就返回index，不是就返回-1"""
        selected_num = len(self.highlight_cellActor_list)
        if selected_num < 1:
            return -1
        for i in range(selected_num):
            if actor == self.picked_cellUnit_list[i][0] and cell_id == self.picked_cellUnit_list[i][1]:
                return i
        else:
            return -1

    def __leftButtonPressEvent(self, obj, event):  # obj和event参数不能删掉
        """左键单击事件"""
        click_pos = self.GetInteractor().GetEventPosition()  # 获取鼠标左键点击时的屏幕坐标
        picker = vtk.vtkCellPicker()
        if self.easy_to_pick:
            picker.SetTolerance(0.001)  # 设置误差限
        picker.Pick(click_pos[0], click_pos[1], 0, self.GetDefaultRenderer())
        picked_cell_id = picker.GetCellId()
        if picked_cell_id == -1:
            picked_cell_id = None
        if picked_cell_id is not None:
            picked_actor = picker.GetActor()
            index = self.__get_selected_cellUnit_index(picked_actor, picked_cell_id)
            # 如果选择的cell未被选
            if index == -1:
                # 如果是单选模式，需要先把之前选择的cell复原
                if self.select_mode == 0 and len(self.highlight_cellActor_list) > 0:
                    self.GetDefaultRenderer().RemoveActor(self.highlight_cellActor_list[0])
                    self.highlight_cellActor_list.pop(0)
                    self.picked_cellUnit_list.pop(0)
                # 生成高亮actor
                picked_mapper = picked_actor.GetMapper()
                picked_polydata = picked_mapper.GetInput()
                newHighlightActor = genHighlightActor(picked_polydata, picked_cell_id, self.color, self.mark_size)
                newHighlightActor.SetPickable(False)
                newHighlightActor.Modified()
                self.picked_cellUnit_list.append([picked_actor, picked_cell_id])
                self.highlight_cellActor_list.append(newHighlightActor)
                self.GetDefaultRenderer().AddActor(newHighlightActor)
            # 如果选择的cell已被选，则直接复原
            else:
                self.GetDefaultRenderer().RemoveActor(self.highlight_cellActor_list[index])
                self.highlight_cellActor_list.pop(index)
                self.picked_cellUnit_list.pop(index)
        self.GetDefaultRenderer().Modified()
        self.OnLeftButtonDown()


