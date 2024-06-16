
import subprocess

class ABARun():
    def __int__(self):
        pass
    def run(self,args,waiting=1000):
        pop = subprocess.Popen(args,shell=True)
        pop.wait(waiting)

        return pop.returncode


