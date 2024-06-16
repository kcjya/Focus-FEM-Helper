import os


class ABAInp():
    def __init__(self):
        self.INPDATA = str()
        pass


    def strcat(self, _str):
        self.INPDATA += _str
        self.INPDATA += "\n"


    def check(self):


        return True


    def catNodes(self, nodes):
        for i in range(len(nodes)):
            Node_Line = f"    {i+1}, {nodes[i][0]}, {nodes[i][1]}, {nodes[i][2]}"
            self.strcat(Node_Line)

    def generateInp(self):
        if not self.check():
            return

        # **INP 文件总是以*Heading开头，接下来可以用一行或多行来写下此模型的标题和相关信息.
        self.strcat("*Heading")
        self.strcat("** Job name: Focus-Job Model name: Model-1")
        self.strcat("** Generated by: Focus FEM 1.0.1")
        # **Preprint可设置在DAT文件（*.dat)中记录的内容。上述为ABAQUS默认，内容为：在DAT文件
        # **中不记录对INP文件的处理过程，以及详细的模型和历史数据。
        self.strcat("*Preprint, echo=NO, model=NO, history=NO, contact=NO")
        self.strcat("**")
        self.strcat("**PARTS")
        self.strcat("**")
        self.strcat("*Part, name=Part-1")
        self.strcat("*Node")
        self.catNodes(nodes=[[0,0,0],[0,0,1],[0,1,0],[1,0,0],[1,0,1],[1,1,1]])
        self.strcat("*Element, type=C3D4")


        with open(os.path.join(os.getcwd(),"abaqus_input.inp"),"w",encoding="utf-8")as fp:
            fp.write(self.INPDATA)


if __name__ == '__main__':
    inp = ABAInp()
    inp.generateInp()
