from typing import Any
import numpy as np



class PlaneSample():
    def __init__(self) -> None:
        pass

    def generateCode(self,_filename, _in):
        # Bug:板材的尺寸必须为偶数
        #   Brief:实际板材的尺寸通过无限元的厚度来约束
        self._data = self._data_process(_in)
        CODE = ""
        with open(_filename,"w",encoding="utf-8")as fp:
            CODE += self._using_coding()
            CODE += self._part_coding()
            CODE += self._property_coding()
            CODE += self._assembly_coding()
            CODE += self._partition_coding()
            CODE += self._datumsys_coding()
            CODE += self._sansysfield_coding()
            CODE += self._step_coding()
            CODE += self._load_coding()
            CODE += self._mesh_coding()
            CODE += self._job_coding()

            fp.write(CODE)


    def _data_process(self,_data):
        E,spot_size,Lap_up_rate,H,W,h,C,R,inft,spot_type = (
            float(_data["E"]),
            float(_data["Spot_Size"]),
            float(_data["LR"]),
            float(_data["H"]),
            float(_data["W"]),
            float(_data["h"]),
            int(_data["CC"]),
            int(_data["RC"]),
            float(_data["INFT"]),
            _data["Spot_Type"],
        )
        # 冲击区域
        bx = spot_size*C-(spot_size*Lap_up_rate)*(C-1)
        x = round((H-bx)/2+spot_size/2,4)
        by = spot_size*R-(spot_size*Lap_up_rate)*(R-1)
        y = round((W-by)/2+spot_size/2,4)
        # 初始点
        ori_xy = [x,y]
        step = spot_size-Lap_up_rate*spot_size
        # 路径
        path = []
        for i in range(1,C+1):
            for j in range(1,R+1):
                path.append([round(ori_xy[0],4),round(ori_xy[1],4),h])
                if j==R:continue
                if i%2==0:
                    ori_xy[1]+=-step
                else:
                    ori_xy[1]+=step
            ori_xy[0]+=step
        # 默认圆形光斑
        I = E / (20 * np.pi * (spot_size / 20) ** 2)
        if spot_type == "Square":
            I = E / (20 * (spot_size / 10) ** 2)
        magnitude = round((0.01*0.262613*np.sqrt(9.08*10**5)*np.sqrt(I)/1.2512)*1000,3)
        # 生成Field场
        _data["Path"] = path
        if "Magnitude" not in _data.keys():
            _data["Magnitude"] = magnitude

        return _data

    # Abaqus头文件
    def _using_coding(self):
        _dir = self._data["WorkingDir"]
        coding = f"""
# -*- coding: mbcs -*-
import os
from part import *
from material import *
from section import *
from optimization import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
# Modify the index to coordinate
os.chdir("{_dir}")
session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry= COORDINATE)
print("Modify the index to coordinate")
    """
        return coding


    # 生成板材
    def _part_coding(self):
        height,width,thickness=(
            float(self._data["H"]),
            float(self._data["W"]),
            float(self._data["h"]),
        )
        coding = f"""
height,width,thickness={height},{width},{thickness}
mdb.models['Model-1'].ConstrainedSketch(
    name='SKETCH',
    sheetSize={max(height,width)+20})
mdb.models['Model-1'].sketches['SKETCH'].rectangle(
    point1=(0.0, 0.0), 
    point2=({height}, {width}))
mdb.models['Model-1'].Part(
    dimensionality=THREE_D, 
    name='Part-1', 
    type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Part-1'].BaseSolidExtrude(
    depth={thickness},
    sketch=mdb.models['Model-1'].sketches['SKETCH'])
del mdb.models['Model-1'].sketches['SKETCH']
print("Entity generatE Successfully!")
    """

        return coding


    def _property_coding(self):
        density,elastic,poisson,plastic,jc=(
            self._data["Density"],
            self._data["Elastic"],
            self._data["Poisson"],
            self._data["Plastic"],
            self._data["JOHNSON_COOK"],
        )

        coding = f"""
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=(({density}, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(table=(({elastic}, {poisson}), ))
{ (f"mdb.models['Model-1'].materials['Material-1'].Plastic(scaleStress=None, table=({tuple(plastic)}, ))" if not jc else f'''
mdb.models['Model-1'].materials['Material-1'].Plastic(
    hardening=JOHNSON_COOK, 
    scaleStress=None, 
    table=({tuple(plastic["JCValue"])}, ))
{
"mdb.models['Model-1'].materials['Material-1'].plastic.RateDependent("
f"    table=({tuple(plastic['JCRate'])}, ), "
"    type=JOHNSON_COOK)" if len(plastic["JCRate"])>0 else ""
}
''') }
# Section
mdb.models['Model-1'].HomogeneousSolidSection(
    material='Material-1', 
    name='Section-1', 
    thickness=None)
mdb.models['Model-1'].parts['Part-1'].SectionAssignment(
    offset=0.0,offsetField='', 
    offsetType=MIDDLE_SURFACE, 
    region=Region(
        cells=mdb.models['Model-1'].parts['Part-1'].cells.findAt(
            ((height/2, width/2, thickness), ), )), 
        sectionName='Section-1', 
        thicknessAssignment=FROM_SECTION)

"""
        return coding



    #装配
    def _assembly_coding(self):
        coding = f"""
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(
    dependent=ON, 
    name='Part-1-1', 
    part=mdb.models['Model-1'].parts['Part-1'])
    """
        return coding


    #创建坐标系
    def _datumsys_coding(self):
        _path = self._data["Path"]
        coding = f"""
datum_position = {_path}
mdb.models['Model-1'].rootAssembly.features.changeKey(
    fromName='Datum csys-1', 
    toName='Datum-csys-main')

for pos in datum_position:
    index = datum_position.index(pos)
    mdb.models['Model-1'].rootAssembly.DatumCsysByOffset(
        coordSysType=CARTESIAN, 
        datumCoordSys=mdb.models['Model-1'].rootAssembly.datums[1], 
        name='Datum csys-'+str(index+1), vector=(pos[0], pos[1], pos[2]))
    """
        return coding



    # 分割无限元
    def _partition_coding(self):
        _infinite = float(self._data["INFT"])
        coding = f"""
mdb.models['Model-1'].ConstrainedSketch(
    gridSpacing=1.0, 
    name='SKETCH', 
    sheetSize=max(height,width)+40, 
    transform = mdb.models['Model-1'].parts['Part-1'].MakeSketchTransform(
        sketchPlane=mdb.models['Model-1'].parts['Part-1'].faces.findAt((height/2,width/2,thickness), ), 
        sketchPlaneSide=SIDE1,
        sketchUpEdge=mdb.models['Model-1'].parts['Part-1'].edges.findAt((height,width/2, thickness), ), 
        sketchOrientation=RIGHT, 
        origin=(height/2,width/2,thickness)))

#_infinite_position

_height = height-2*{_infinite}
_width = width-2*{_infinite}
infinite_thickness = {_infinite}
infinite_pt1 = (-height/2+{_infinite}, width/2-{_infinite})
infinite_pt2 = (height/2-{_infinite}, -width/2+{_infinite})

mdb.models['Model-1'].parts['Part-1'].projectReferencesOntoSketch(filter=
    COPLANAR_EDGES, sketch=mdb.models['Model-1'].sketches['SKETCH'])
mdb.models['Model-1'].sketches['SKETCH'].rectangle(point1=infinite_pt1,point2=infinite_pt2)
mdb.models['Model-1'].sketches['SKETCH'].Line(point1=(-height/2, width/2),point2=infinite_pt1)
mdb.models['Model-1'].sketches['SKETCH'].Line(point1=(_height/2, _width/2), point2=(height/2, width/2))
mdb.models['Model-1'].sketches['SKETCH'].Line(point1=(-_height/2, -_width/2),point2=(-height/2, -width/2))
mdb.models['Model-1'].sketches['SKETCH'].Line(point1=(_height/2, -_width/2),point2=(height/2, -width/2))
mdb.models['Model-1'].parts['Part-1'].PartitionFaceBySketch(
    faces=mdb.models['Model-1'].parts['Part-1'].faces.findAt(((height/2, width/2,thickness), )), 
    sketch=mdb.models['Model-1'].sketches['SKETCH'], 
    sketchUpEdge=mdb.models['Model-1'].parts['Part-1'].edges.findAt((height,width/2, thickness), ))
del mdb.models['Model-1'].sketches['SKETCH']

mdb.models['Model-1'].parts['Part-1'].PartitionCellByExtrudeEdge(
    cells=mdb.models['Model-1'].parts['Part-1'].cells.findAt(((height/2,width/2,thickness), )), 
    edges=(
        mdb.models['Model-1'].parts['Part-1'].edges.findAt((height/2,{_infinite}, thickness), ),
        mdb.models['Model-1'].parts['Part-1'].edges.findAt((height/2,width-{_infinite}, thickness), ), 
        mdb.models['Model-1'].parts['Part-1'].edges.findAt(({_infinite}, width/2, thickness), ), 
        mdb.models['Model-1'].parts['Part-1'].edges.findAt((height-{_infinite}, width/2, thickness), )), 
    line=mdb.models['Model-1'].parts['Part-1'].edges.findAt((0.0, 0.0, thickness/2), ), 
    sense=REVERSE)
mdb.models['Model-1'].parts['Part-1'].PartitionCellByExtrudeEdge(
    cells=mdb.models['Model-1'].parts['Part-1'].cells.findAt((({_infinite/2},{_infinite/2}, thickness), )), 
    edges=(
        mdb.models['Model-1'].parts['Part-1'].edges.findAt((height-{_infinite/2},{_infinite/2}, thickness), ), 
        mdb.models['Model-1'].parts['Part-1'].edges.findAt((height-{_infinite/2},width-{_infinite/2}, thickness), ), 
        mdb.models['Model-1'].parts['Part-1'].edges.findAt(({_infinite/2},{_infinite/2}, thickness), ), 
        mdb.models['Model-1'].parts['Part-1'].edges.findAt(({_infinite/2},width-{_infinite/2}, thickness), )), 
    line=mdb.models['Model-1'].parts['Part-1'].edges.findAt((0.0, 0.0, thickness/2), ), 
    sense=REVERSE)



    """
        return coding



    # 建立冲击波分布场
    def _sansysfield_coding(self):
        _expression = self._data["Expression"]
        coding = f"""
for i in range(len(datum_position)):
    mdb.models['Model-1'].ExpressionField(
        description='', 
        expression='{_expression}', 
        localCsys=mdb.models['Model-1'].rootAssembly.datums[4+i], 
        name='AnalyticalField-'+str(i+1))

    """
        return coding


    # 创建分析步骤
    def _step_coding(self):
        _period = self._data["Period"]
        _requests = self._data["FOR"]
        coding = f"""
mdb.models['Model-1'].ExplicitDynamicsStep(
    improvedDtMethod=ON, 
    name='Step-1', 
    previous='Initial',
    timePeriod={_period})
for i in range(len(datum_position)-1):
    mdb.models['Model-1'].ExplicitDynamicsStep(
        improvedDtMethod=ON, 
        name='Step-'+str(i+2), 
        previous='Step-'+str(i+1),
        timePeriod={_period})
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(
    variables={_requests})

    """
        return coding


    # 添加冲击波
    def _load_coding(self):
        _magnitude = self._data["Magnitude"]
        coding =f"""{
f'''
# Amp
mdb.models['Model-1'].TabularAmplitude(
    data={tuple(self._data["Amp"])},
    name='Amp-1', 
    smooth=SOLVER_DEFAULT, 
    timeSpan=STEP)''' if  "Amp" in dict(self._data).keys() else ""}
#Surf-Load
mdb.models['Model-1'].rootAssembly.Surface(
    name='Surf-Load', 
    side1Faces=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.findAt(((width/2,height/2, thickness), )))
#Load
for i in range(len(datum_position)):
    mdb.models['Model-1'].Pressure(
        {"amplitude='Amp-1'," if "Amp" in dict(self._data).keys() else ""}
        createStepName='Step-'+str(i+1), 
        distributionType=FIELD, 
        field='AnalyticalField-'+str(i+1), 
        magnitude={_magnitude}, 
        name='Load-'+str(i+1), 
        region=mdb.models['Model-1'].rootAssembly.surfaces['Surf-Load'])
    if i<len(datum_position)-1:mdb.models['Model-1'].loads['Load-'+str(i+1)].deactivate('Step-'+str(i+2))    
# 2024-03-14 update
{'''# BC
mdb.models['Model-1'].EncastreBC(
createStepName='Initial', 
localCsys=None, 
    name='BC-1', 
    region=Region(
    faces=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'].faces.findAt(((width/2,height/2, 0), )))
''' if float(self._data["INFT"])<=0 else ""
}"""

        return coding



    def _mesh_coding(self):
        global_size,max_size,min_size,elem_type = (
            self._data["Global_Size"],
            self._data["Max_Size"],
            self._data["Min_Size"],
            self._data["Elem_Type"],
        )
        coding = f"""
mdb.models['Model-1'].parts['Part-1'].setMeshControls(
    algorithm=ADVANCING_FRONT, 
    regions=mdb.models['Model-1'].parts['Part-1'].cells.findAt(
        ((infinite_thickness/2, width/2,thickness), ), 
        ((height/2, infinite_thickness/2, thickness), ), 
        ((height/2, width-infinite_thickness/2, thickness), ), 
        ((height-infinite_thickness/2, width/2, thickness), ), ), 
        technique=SWEEP)
mdb.models['Model-1'].parts['Part-1'].setSweepPath(
    edge=mdb.models['Model-1'].parts['Part-1'].edges.findAt((height-infinite_thickness/2, infinite_thickness/2, thickness), ), 
    region=mdb.models['Model-1'].parts['Part-1'].cells.findAt((height-infinite_thickness/2, width/2, thickness), ), 
    sense=FORWARD)
mdb.models['Model-1'].parts['Part-1'].setSweepPath(
    edge=mdb.models['Model-1'].parts['Part-1'].edges.findAt((height-infinite_thickness/2, infinite_thickness/2, thickness), ), 
    region=mdb.models['Model-1'].parts['Part-1'].cells.findAt((height/2, infinite_thickness/2,thickness), ), 
    sense=FORWARD)
mdb.models['Model-1'].parts['Part-1'].setSweepPath(
    edge=mdb.models['Model-1'].parts['Part-1'].edges.findAt((infinite_thickness/2, width-infinite_thickness/2, thickness), ), 
    region=mdb.models['Model-1'].parts['Part-1'].cells.findAt((height/2, width-infinite_thickness/2, thickness), ), 
    sense=REVERSE)
mdb.models['Model-1'].parts['Part-1'].setSweepPath(
    edge=mdb.models['Model-1'].parts['Part-1'].edges.findAt((infinite_thickness/2, width-infinite_thickness/2, thickness), ), 
    region=mdb.models['Model-1'].parts['Part-1'].cells.findAt((infinite_thickness/2, width/2, thickness), ), 
    sense=REVERSE)

#Mesh

mdb.models['Model-1'].parts['Part-1'].seedPart(
    deviationFactor=0.1,
    minSizeFactor=0.1, 
    size={global_size})

mdb.models['Model-1'].parts['Part-1'].seedEdgeByNumber(
    constraint=FINER,
    edges=mdb.models['Model-1'].parts['Part-1'].edges.findAt(
        ((infinite_thickness/2, infinite_thickness/2,thickness), ), 
        ((infinite_thickness/2, width-infinite_thickness/2, thickness), ), 
        ((height-infinite_thickness/2, infinite_thickness/2, thickness), ), 
        ((height-infinite_thickness/2, width-infinite_thickness/2, thickness), ), ), 
        number=1)
mdb.models['Model-1'].parts['Part-1'].seedEdgeByBias(
    biasMethod=SINGLE, 
    constraint=FINER, 
    end2Edges=mdb.models['Model-1'].parts['Part-1'].edges.findAt(
        ((0.0, 0.0, thickness/2), ), 
        ((height, 0.0, thickness/2), ), 
        ((height, width, thickness/2), ), 
        ((0.0, width, thickness/2), ), ), 
        maxSize={max_size}, 
        minSize={min_size})
mdb.models['Model-1'].parts['Part-1'].generateMesh()

# Type
# C3D8R
mdb.models['Model-1'].parts['Part-1'].setElementType(
    elemTypes=(
        ElemType(
            elemCode={elem_type}, 
            elemLibrary=EXPLICIT, 
            secondOrderAccuracy=OFF, 
            kinematicSplit=AVERAGE_STRAIN, 
            hourglassControl=DEFAULT, 
            distortionControl=DEFAULT), 
        ElemType(
            elemCode=C3D6, 
            elemLibrary=EXPLICIT), 
        ElemType(
            elemCode=C3D4, 
            elemLibrary=EXPLICIT)), 
        regions=(mdb.models['Model-1'].parts['Part-1'].cells.findAt(
            ((height/2, width/2,thickness), )), 
        ))

mdb.models['Model-1'].parts['Part-1'].setElementType(
    elemTypes=(
        ElemType(
            elemCode=C3D8T, 
            elemLibrary=EXPLICIT, 
            secondOrderAccuracy=OFF, 
            distortionControl=DEFAULT), 
        ElemType(
            elemCode=C3D6T, 
            elemLibrary=EXPLICIT),
        ElemType(
            elemCode=C3D4T, 
            elemLibrary=EXPLICIT
        )), regions=(
        mdb.models['Model-1'].parts['Part-1'].cells.findAt(
            ((infinite_thickness/2, width/2,thickness), ), 
            ((height/2, infinite_thickness/2, thickness), ), 
            ((height/2, width-infinite_thickness/2, thickness), ), 
            ((height-infinite_thickness/2, width/2, thickness), ), ), ))

    """
        return coding



    def _job_coding(self):
        cpus, inp_name = (
            self._data["CPUS"],
            self._data["Inp_Name"],
        )
        coding = f"""
mdb.Job(
    activateLoadBalancing=False, 
    atTime=None, 
    contactPrint=OFF, 
    description='Do not submit the job', 
    echoPrint=OFF, 
    explicitPrecision=SINGLE, 
    historyPrint=OFF, 
    memory=90, 
    memoryUnits=PERCENTAGE, 
    model='Model-1', 
    modelPrint=OFF, 
    multiprocessingMode=DEFAULT, 
    name='{inp_name}', 
    nodalOutputPrecision=SINGLE, 
    numCpus=2, 
    numDomains=2, 
    numThreadsPerMpiProcess=1, 
    queue=None, 
    resultsFormat=ODB, 
    scratch='', 
    type=ANALYSIS, 
    userSubroutine='', 
    waitHours=0, 
    waitMinutes=0)
    
# Main Job
mdb.JobFromInputFile(
    activateLoadBalancing=False, 
    atTime=None, 
    explicitPrecision=SINGLE, 
    inputFileName='C:\\KNG\\Preject\\Python\\Focus\\INPUT.inp', 
    memory=90, 
    memoryUnits=PERCENTAGE, 
    multiprocessingMode=DEFAULT, 
    name="{str(inp_name).upper()}_ANALYSIS", 
    nodalOutputPrecision=SINGLE, 
    numCpus={cpus}, 
    numDomains={cpus}, 
    numThreadsPerMpiProcess=1, 
    queue=None, 
    resultsFormat=ODB, 
    scratch=r'C:\KNG\Preject\Python\Focus\cache', 
    type=ANALYSIS, 
    userSubroutine='', 
    waitHours=0, 
    waitMinutes=0)
# Viewport
session.viewports['Viewport: 1'].setValues(displayedObject=mdb.models['Model-1'].parts['Part-1'])
session.viewports['Viewport: 1'].partDisplay.setValues(mesh=ON)
mdb.models['Model-1'].rootAssembly.regenerate()
print('''
            ******
            ******
            ******
            ******
            ******
            ******
            ******
            ******   
         ************
          ********** 
           ********
            ****** 
             ****  
              **
''')
print('**-Information-**: Please modify "C3D8T"->"CIN3D8" in "INPUT.inp"file manually!')
"""

        return coding





if __name__ == "__main__":
    _in = {
        "E":10,     # 激光能量J
        "Spot_Size":4,      # 光斑直径mm
        "Spot_Type":"Square",
        "LR":0.3,   # 搭接率0.#
        "H":26,     # 板材长(包括无限元)mm
        "W":26,     # 板材宽(包括无限元)mm
        "h":3,      #板材厚度mm
        "CC":5,     #光斑列数量(个)
        "RC":5,     #光斑行数量(个)
        "INFT":2,   #无限元的厚度
        "Global_Size":0.15,     #全局网格尺寸
        "Max_Size":0.15,        #最大网格尺寸(厚度方向)
        "Min_Size":0.05,         #最小网格尺寸(厚度方向)
        "Elem_Type":"C3D8R",
        "Density": 4.56e-9,
        "Elastic": 110000,
        "Poisson": 0.3,
        "Plastic": (980, 0),  # 不用JC本构
        "JOHNSON_COOK": 0,  # 不用JC本构(必须)
        "JCValue": "(A, b, n, m, meltin_temp, transition_temp),",
        "JCRate":"(C,rate)",
        # "JOHNSON_COOK":1,    #JC本构(必须)
        "Period": 3e-5,
        "Expression":"exp(-2*(sqrt(X**2+Y**2)/2.0)**10 )",
        "FOR": ("S", "U", "V"),
        "CPUS":8,
        "Inp_Name":"INPUT",
        "Amp":(
            (0.0, 0.0),
            (2e-09, 0.14), 
            (4e-09,0.26), 
            (9e-09, 0.98), 
            (1e-08, 1.0), 
            (1.2e-08, 0.96), 
            (1.8e-08, 0.8), 
            (2.5e-08, 0.5), 
            (8e-08, 0.2), 
            (1.8e-07, 0.05), 
            (2e-07, 0.0),
        ),

        
    }

# taker = PlaneSample()
# taker("main.py",_in)

