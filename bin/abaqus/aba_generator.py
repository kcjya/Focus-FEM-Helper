
import os


class ABAgenerator():
    def __init__(self):
        self.CODES = ""
        self.valuesInit()

    def valuesInit(self):
        self.Global = None


    @staticmethod
    def name(file):
        return str(str(file).split("\\")[-1]).split(".")[0]


    def setMustDatas(self, _datas):
        self.Global = _datas

    def _setdir_coding(self):
        dir = self.Global["WorkingDir"]
        return f"""
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
from abaqus import *
os.chdir("{dir}")
session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry= COORDINATE)
print("Working directory setup completed")

        """

    def _openmodel_coding(self):
        model_path = self.Global["ModelPath"]
        name = self.name(model_path).upper()
        return f"""
mdb.Model(description="Created By FocusCAE Helper", modelType=STANDARD_EXPLICIT
    , name="Model-1")
mdb.openStep({str(model_path).encode("utf-8")}, scaleFromFile=OFF)
mdb.models["Model-1"].PartFromGeometryFile(combine=False, dimensionality=
    THREE_D, geometryFile=mdb.acis, name='Part-1', type=DEFORMABLE_BODY)
mdb.models["Model-1"].parts['Part-1'].ConvertToAnalytical()
mdb.models["Model-1"].parts['Part-1'].ConvertToPrecise(method=
    RECOMPUTE_GEOMETRY)
mdb.models["Model-1"].parts['Part-1'].checkGeometry()
print("The model file was successfully opened")
        """

    def _property_coding(self):
        density = self.Global["Density"]
        young_value = self.Global["Young"]
        possion_rate = self.Global["Possion"]
        yield_stress = self.Global["Yield_Stress"]
        plastic_strain = self.Global["Plastic_Strain"]
        plastic_coding = ""
        if "A" in self.Global.values():
            A = self.Global["A"]
            B = self.Global["B"]
            n = self.Global["n"]
            m = self.Global["m"]
            melting_temp = self.Global["Melting_Temp"]
            transition_temp = self.Global["Transition_Temp"]
            C = self.Global["C"]
            epsilon = self.Global["Epsilon"]
            plastic_coding = f"""
mdb.models['Model-1'].materials['Material-1'].Plastic(hardening=JOHNSON_COOK, 
    scaleStress=None, table=(({A},{B}, {n}, {m}, {melting_temp}, {transition_temp}), ))
mdb.models['Model-1'].materials['Material-1'].plastic.RateDependent(table=((
    {C}, {epsilon}), ), type=JOHNSON_COOK)"""
        else:
            plastic_coding = f"mdb.models['Model-1'].materials['Material-1'].Plastic(scaleStress=None, table=(({yield_stress}, {plastic_strain}), ))"


        return f"""
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=(({density}, ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(table=(({young_value}, {possion_rate}), ))
{plastic_coding}
mdb.models['Model-1'].HomogeneousSolidSection(material='Material-1', name=
    'Section-1', thickness=None)
mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
    cells=mdb.models['Model-1'].parts['Part-1'].cells.findAt(((0, 
    0, 0), ), )), sectionName='Section-1', thicknessAssignment=
    FROM_SECTION)
print("The properties were set successfully")
"""

    def _assembly_coding(self):
        return f"""
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='PART-1-1'
    , part=mdb.models['Model-1'].parts['Part-1'])
print("Assembly Successfully")
"""


    def _mesh_coding(self):
        mesh_size = self.Global["Mesh_Size"]
        mesh_shape = self.Global["Mesh_Shape"]
        return f"""
mdb.models['Model-1'].parts['Part-1'].setMeshControls(elemShape={mesh_shape}, regions=
    mdb.models['Model-1'].parts['Part-1'].cells.findAt(((0,0,0), )), technique=FREE)
mdb.models['Model-1'].parts['Part-1'].seedPart(deviationFactor=0.1, 
    minSizeFactor=0.1, size={mesh_size})
mdb.models['Model-1'].parts['Part-1'].setElementType(elemTypes=(ElemType(
    elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT), ElemType(
    elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT), ElemType(elemCode=C3D10M, 
    elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, distortionControl=DEFAULT)), 
    regions=(mdb.models['Model-1'].parts['Part-1'].cells.findAt(((0,0,0), )), ))
mdb.models['Model-1'].parts['Part-1'].generateMesh()
print("Mesh Successfully")
"""
    def _job_coding(self):
        cpus = self.Global["Cpus"]
        return f"""
mdb.models['Model-1'].rootAssembly.regenerate()
mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
    description='FocusCAE-JOB', echoPrint=OFF, explicitPrecision=SINGLE, 
    getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=
    PERCENTAGE, model='Model-1', modelPrint=OFF, multiprocessingMode=DEFAULT, 
    name='Job-1', nodalOutputPrecision=SINGLE, numCpus={cpus}, numDomains={cpus}, 
    numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, 
    scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
print("Submit Successfully")
"""


    def generate(self)->str:
        self.CODES += self._setdir_coding()
        self.CODES += self._openmodel_coding()
        self.CODES += self._property_coding()
        self.CODES += self._assembly_coding()
        self.CODES += self._mesh_coding()
        self.CODES += self._job_coding()

        file = os.path.join(os.getcwd(),"cache","abaqus_python.py")
        with open(file,"w",encoding="utf-8") as fp:
            fp.write(self.CODES)

        return file


