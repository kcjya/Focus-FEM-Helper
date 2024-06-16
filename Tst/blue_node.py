import vtk

# 创建一个球体模型作为示例
sphere_source = vtk.vtkSphereSource()
sphere_source.Update()

# 创建一个 mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(sphere_source.GetOutput())

# 创建一个 actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# 创建渲染器、渲染窗口和交互器
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# 添加 actor 到渲染器中
renderer.AddActor(actor)

# 获取模型的边界框
bounds = actor.GetBounds()
center = actor.GetCenter()

# 计算边界框的对角线长度
diagonal_length = vtk.vtkMath.Distance2BetweenPoints(bounds[0:3], bounds[3:6])

# 获取窗口的尺寸
window_size = render_window.GetSize()

# 计算相机的位置和焦点，使模型适合显示在窗口中央
camera = renderer.GetActiveCamera()
camera.SetFocalPoint(center)
camera.SetPosition(center[0], center[1], center[2] + diagonal_length)

# 渲染并显示窗口
renderer.ResetCamera()
render_window.Render()
interactor.Start()
