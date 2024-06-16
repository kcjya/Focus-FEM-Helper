import vtk

# 创建箭头源
arrow = vtk.vtkArrowSource()

# 创建箭头的Actor
arrow_mapper = vtk.vtkPolyDataMapper()
arrow_mapper.SetInputConnection(arrow.GetOutputPort())

arrow_actor = vtk.vtkActor()
arrow_actor.SetMapper(arrow_mapper)
# 指定向量的方向和大小
vector = [1, 1, 1]  # 向量的方向
magnitude = vtk.vtkMath.Norm(vector)  # 向量的大小
# 设置箭头的位置和方向
arrow_actor.SetPosition(0-magnitude, 0-magnitude, 0-magnitude)  # 箭头的起始位置
arrow_actor.SetScale(1.0)  # 箭头的大小



# 将箭头放置在指定位置，并设置方向和大小
arrow_actor.SetPosition(0, 0, 0)
arrow_actor.SetScale(magnitude)  # 设置箭头的长度
arrow_actor.RotateWXYZ(90, vector[2], -vector[1], vector[0])  # 设置箭头的方向

# 创建Renderer和RenderWindow
renderer = vtk.vtkRenderer()
renderer.AddActor(arrow_actor)
# 创建球体源
sphere_source = vtk.vtkSphereSource()
sphere_source.SetCenter(0, 0, 0)  # 设置球体的中心位置
sphere_source.SetRadius(1.0)  # 设置球体的半径

# 创建球体的Mapper
sphere_mapper = vtk.vtkPolyDataMapper()
sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

# 创建球体的Actor
sphere_actor = vtk.vtkActor()
sphere_actor.SetMapper(sphere_mapper)
sphere_actor.GetProperty().SetColor(1, 0, 0)  # 设置球体的颜色为红色



render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
renderer.AddActor(sphere_actor)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 启动交互式窗口
render_window.Render()
render_window_interactor.Start()
