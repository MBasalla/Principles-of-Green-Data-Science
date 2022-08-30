#Measure energy of GPU using the NVIDIA smi tool on Ubuntu (This must be installed and callable from shell)
#The smi tool is started in a suprocess and stores measurements in a file

import os,subprocess
import numpy as np


def startLog(logname): #Start the nvidia-smi tool in a seperate shell, kill any other, already running nvidia-smi processes before
    os.system("killall -9 nvidia-smi");  #
    p = subprocess.Popen(['nvidia-smi stats -d pwrDraw -c 99999999 > ' + logname], shell=True);  # conda init bash;conda activate pytorch ";nvidia-smi stats -d pwrDraw -c 99999999 > " + logname
    # p = subprocess.Popen(['bash -c "conda activate root;nvidia-smi stats -d pwrDraw -c 99999999 > "' + logname], shell=True);#conda init bash;conda activate pytorch ";nvidia-smi stats -d pwrDraw -c 99999999 > " + logname
    return p

def endLog(process):
    process.kill()
    os.system("killall -9 nvidia-smi");

# Parse log with name "logame",  return mean energy, e.g., sum and dividing by #samples or computation time (e.g. measure time between startlog / endlog call, e.g. see https://stackoverflow.com/questions/7370801/how-do-i-measure-elapsed-time-in-python
def getWattFromLog(logname):
    with open(logname, "r") as f:
        lines = f.readlines()
        numbstrs = [int(c.replace(" ", "").split(",")[-1]) for c in lines]

    # Parse log
    powerUsage = [int(x) for x in numbstrs]  # remove trailing "W"
    powerUsage = powerUsage[len(powerUsage) // 10:-len(powerUsage) // 10]  # ignore the first and last samples -for start up phase
    return np.sum(powerUsage), len(powerUsage)
    #return np.median(powerUsage) * len(powerUsage), len(powerUsage)



#Example usage
if __name__ == "__main__":
    from timeit import default_timer as timer
    import time

    start = timer()
    logname="testlog.txt"
    process=startLog(logname=logname)
    time.sleep(2000) #just do nothing/ here would be computation
    end = timer()
    endLog(process)
    energy,samples=getWattFromLog(logname)
    print("Duration",end - start," Energy based on sum",energy)
