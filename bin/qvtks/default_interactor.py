import numpy
import vtk
import numpy as np
from vtk import vtkPropPicker,vtkAxesActor,vtkTransform
from vtkmodules.util.numpy_support import numpy_to_vtk

class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.parent = parent
        self.main_axes = None
        self.axes_scale = vtkTransform()
        self.AddObserver("KeyPressEvent", self.OnKeyPressEvent)
        self.AddObserver("LeftButtonPressEvent", self.LeftButtonPressEvent)

        # 将鼠标滚轮回调函数与鼠标滚轮事件关联
        self.AddObserver('MouseWheelForwardEvent', self.mouseWheelForwardCallback)
        self.AddObserver('MouseWheelBackwardEvent', self.mouseWheelBackwardCallback)

    def setFixedAxes(self, actor):
        self.main_axes = actor
        pass


    def mouseWheelForwardCallback(self, object, event):
        exp = self.GetMotionFactor() * (-0.2) * self.GetMouseWheelMotionFactor()
        self.axes_scale.Scale(pow(1.1, exp), pow(1.1, exp), pow(1.1, exp))
        self.axes_scale.Update()
        self.main_axes.SetUserTransform(self.axes_scale)

        self.OnMouseWheelForward()


    def mouseWheelBackwardCallback(self, object, event):
        exp = self.GetMotionFactor() * (0.2) * self.GetMouseWheelMotionFactor()
        self.axes_scale.Scale(pow(1.1, exp), pow(1.1, exp), pow(1.1, exp))
        self.axes_scale.Update()
        self.main_axes.SetUserTransform(self.axes_scale)

        self.OnMouseWheelBackward()



    def OnKeyPressEvent(self, object, event):
        # Get the compound key strokes for the event
        # 获取事件的复合键笔划
        key = self.GetInteractor().GetKeySym()
        print(key)
        if key=="A":
            pass

    def LeftButtonPressEvent(self, object, event):
        transformer = vtk.vtkTransform()
        clickPos = self.GetInteractor().GetEventPosition()
        renderer = self.GetDefaultRenderer()
        picker = vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, renderer)
        # get the new
        self.currentActor = picker.GetActor()

        point_actor = vtk.vtkActor()
        point = vtk.vtkPoints()
        point.SetData(numpy_to_vtk(np.array([picker.GetPickPosition()])))
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(point)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(1)
        actor.GetProperty().SetColor([1,0,0])
        actor.Modified()


        self.GetDefaultRenderer().AddActor(actor)
        self.GetDefaultRenderer().Render()
        self.OnLeftButtonDown()
        return



