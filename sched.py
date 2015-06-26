class scheduler:
    def __init__(self, processes = []):
        self._processes = processes
        self._interval = 0 #time interval, didn't started yet
        self._processToRun = None
    def addProcess(self, process):
        self._processes.append(process)

class process:
#simple class that keeps info about process (runtime and time left to run)
    def __init__(self):
        self._runtime = 0 #how many intervals it has been running
        self._sleeptime = 0 #how many intervals it has been sleeping
        self._timeNeeded = timeNeeded
    def timeLeft(self):
        return self._timeNeeded - self._runtime
    def run(self, intervals = 1):
        self._runtime += intervals
        #if self.timeLeft() < 0:
        #    self._runtime

