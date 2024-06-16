
import vtkmodules.all as vtk
import numpy as np
from typing import Union
from vtkmodules.util.numpy_support import numpy_to_vtk


class Geometry:
    """几何元素生成函数封装类"""

    @staticmethod
    def genActorFromPolyData(polydata: vtk.vtkPolyData) -> vtk.vtkActor:
        """由polydata生成actor"""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.Modified()
        return actor

    @staticmethod
    def genSphereActor(position: Union[tuple[float, float, float], list[float], np.ndarray], radius: float = 2.0,
                       color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """以球体形式生成点actor，输入位置、半径、颜色"""
        pt = vtk.vtkSphereSource()
        pt.SetRadius(radius)
        pt.SetCenter(position[0], position[1], position[2])
        pt.SetPhiResolution(20)  # 球体显示的分辨率参数
        pt.SetThetaResolution(20)  # 球体显示的分辨率参数
        pt.Update()
        actor = Geometry.genActorFromPolyData(pt.GetOutput())
        actor.GetProperty().SetColor(color)
        actor.Modified()
        return actor

    @staticmethod
    def genPixelActor(position: Union[tuple[float, float, float], list[float], np.ndarray],
                      size: int = 5, color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """以像素点形式生成点actor，输入位置、像素大小、颜色"""
        pts = np.array([position])
        actor = Geometry.genPointCloudActor(pts, size, color)
        return actor

    @staticmethod
    def genLineActor(start_pos: Union[tuple[float, float, float], list[float], np.ndarray],
                     end_pos: Union[tuple[float, float, float], list[float], np.ndarray],
                     line_width: int = 2, color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """以像素线段形式生成线actor，可自定义线宽颜色"""
        pts = np.array([start_pos, end_pos])
        actor = Geometry.genWholeBreakLineActor(pts, line_width, color)
        return actor

    @staticmethod
    def genTriangleFrameActor(pts: np.ndarray, line_width: int = 2,
                              color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """以线框形式生成三角形actor，可自定义线宽颜色"""
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(np.copy(pts)))
        cells = vtk.vtkCellArray()
        polydata = vtk.vtkPolyData()
        cells.InsertNextCell(4, [0, 1, 2, 0])
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        actor = Geometry.genActorFromPolyData(polydata)
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetColor(color)
        return actor

    @staticmethod
    def genWholeBreakLineActor(pts: np.ndarray, line_width: int = 2,
                               color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """生成整段的折线actor，其中只有一个Cell，可自定义线宽颜色"""
        nL = pts.shape[0]
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(np.copy(pts)))
        cells = vtk.vtkCellArray()
        polydata = vtk.vtkPolyData()
        cells.InsertNextCell(nL, [i for i in range(nL)])
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        actor = Geometry.genActorFromPolyData(polydata)
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetColor(color)
        return actor

    @staticmethod
    def genPolyLineActor(pts: np.ndarray, line_width: int = 2,
                         color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """生成分段的折线actor，其中每一条线段是一个Cell，可自定义线宽颜色"""
        nL = pts.shape[0]
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(np.copy(pts)))
        cells = vtk.vtkCellArray()
        polydata = vtk.vtkPolyData()
        for i in range(nL - 1):
            cells.InsertNextCell(2, [i, i + 1])
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        actor = Geometry.genActorFromPolyData(polydata)
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetColor(color)
        return actor

    @staticmethod
    def genAxesActor(axes_length: int = 600) -> vtk.vtkAxesActor:
        """坐标轴创建，输入三轴长度"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(axes_length, axes_length, axes_length)  # 设置轴长度
        axes.SetShaftType(1)  # 设置轴类型，1为线0为圆柱

        # axes.SetCylinderRadius(1)  # 设置圆柱半径
        axes.SetConeRadius(0.05)  # 设置箭头大小
        axes.GetXAxisCaptionActor2D().SetWidth(0.03)  # 设置坐标轴标签大小
        axes.GetYAxisCaptionActor2D().SetWidth(0.03)
        axes.GetZAxisCaptionActor2D().SetWidth(0.03)
        return axes

    @staticmethod
    def genPointCloudActor(pts: np.ndarray, size: int = 5,
                           color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> vtk.vtkActor:
        """生成点云actor，用固定像素大小的点表示，可定义大小与颜色"""
        npt = pts.shape[0]
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(pts))
        cells = vtk.vtkCellArray()
        polydata = vtk.vtkPolyData()
        for i in range(npt):
            cells.InsertNextCell(1, [i])
        polydata.SetPoints(points)
        polydata.SetVerts(cells)
        actor = Geometry.genActorFromPolyData(polydata)
        actor.GetProperty().SetPointSize(size)
        actor.GetProperty().SetColor(color)
        return actor

    @staticmethod
    def genPointCloudSpheres(pts: np.ndarray, radius: float,
                             color: tuple[float, float, float] = (1.0, 0.0, 0.0)) -> list[vtk.vtkActor]:
        """用球体对象组表示点云，可定义半径与颜色"""
        npt = pts.shape[0]
        actor_list = []
        for i in range(npt):
            actor = Geometry.genSphereActor(tuple(pts[i]), radius, color)
            actor_list.append(actor)
        return actor_list

