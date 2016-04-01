# -*- coding: utf-8 -*-
import time, datetime, inspect
import os
import CommonUtil
import sys
sys.path.append("..")

if os.name == "nt":
    from wmi import WMI







class ProcessInformation():
    """

    ========= Instruction: ============

    Function Description:
    This function returns all the propertes of the PID that is provided.
    it will return as an object from which you can simply type on the object that
    you want to get value of.  I will be adding more information about each elements


    Parameter Description:
    - PID is the process ID of the processor that you are interested in

    Example:
    - full_list = performance(5932)
    - private_memory=  full_list.WorkingSetPrivate
    - it returns in Bytes

    ======= End of Instruction: =========
    """

    def __init__(self):
        self.PrivateWorkingSet = ""
    def ProcInfo(self, pid):
        try:
            w = WMI('.')
            result = w.query("SELECT * FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % pid)
            result_detail = result[0]
            #process_info= ProcessInformation()
            self.PrivateWorkingSet = BytesToMB(result_detail.WorkingSetPrivate)
            return self
        except Exception, e:
            print "There was an error getting all the performance related information.  See below error code for more info: "
            print e
            return False


def BytesToMB(bytes):
    """

    ========= Instruction: ============

    Function Description:
    This function converts bytes to MB


    Parameter Description:
    - bytes

    Example:
    - BytesToMB(private_memory)
    - it returns in MB

    ======= End of Instruction: =========
    """
    try:
        bytes = float(bytes)
        MB = bytes / 1048576
        MB_rounded = round(MB, 2)
        return MB_rounded
    except Exception, e:
        print "There was an error with conversion.  See below error code for more info: "
        print e
        return False

def BytesToGB(bytes):
    """

    ========= Instruction: ============

    Function Description:
    This function converts bytes to GB


    Parameter Description:
    - bytes

    Example:
    - BytesToGB(private_memory)
    - it returns in GB

    ======= End of Instruction: =========
    """
    try:
        GB_rounded = round (((float(bytes)) / 1073741824), 0)
        return GB_rounded
    except Exception, e:
        print "There was an error with conversion.  See below error code for more info: "
        print e
        return False

class ComputerHWInfo():
    def __init__(self):
        self.ManufacturerName = ""
        self.ModelName = ""
        self.PhysicalMemory = ""
        self.HWModel = ""
    def CompInfo(self):
        info = []
        comp = WMI()
        for i in comp.Win32_ComputerSystem():
            #print i
            info.append(i.Manufacturer)
            info.append(i.Model)
            TotalMemory = BytesToGB(i.TotalPhysicalMemory)
            if i.Model == '3228BC7' or i.Model == '7034DL9':
                self.ModelName = "M Series"
            else:
                self.ModelName = i.Model
            self.ManufacturerName = i.Manufacturer
            self.PhysicalMemory = TotalMemory
            tmpHWModel = self.ManufacturerName + " " + self.ModelName.replace("HP", "").replace("Compaq", "").replace("Convertible", "").replace("Minitower", "").replace(" ", "")
            self.HWModel = tmpHWModel
            return self

def CollectProcessMemory(StepName, Input_Q, ProcName='windows.exe'):
    #print "Collect Process Memory for ",ProcName
    while Input_Q.get() != 'Start':
        time.sleep (1)

    print "Starting"

    while Input_Q.get() != 'Stop':
        print "inside getting memory"
        pid = CommonUtil.GetProcessId(ProcName)
        if pid != False:
            Obj = ProcessInformation()
            MemObj = Obj.ProcInfo(pid)
            if MemObj:
                WSP = MemObj.PrivateWorkingSet
                CurTime = datetime.datetime.now()
                #print "StepName: ",StepName
                #print "Current Time: ",CurTime
                #print "Working Set Private Memory: ",WSP
            else:
                print "Memory details not found for pid: ", pid
        else:
            print "Process not found"
        time.sleep (5)



