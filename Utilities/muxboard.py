'''
Created on Apr 25, 2016

@author: Riz
'''
#!/usr/bin/env python

# Depends on pyserial module availability
# pip install pyserial
#

#!/usr/bin/env python

# Depends on pyserial module availability
# pip install pyserial
# check which usb port on NUC is connected to mux serial port 
# run the following command for that port to allow read/write permissions:
# sudo chmod 666 /dev/tty<USB port>
# in most cases the USB port will be USB0

##Error Message:
#Exception AttributeError: "'muxboard' object has no attribute '_fd'" in  ignored

import time, os, sys, subprocess
import pip
try:
    import serial
except:
    pip.main(['install', 'pyserial'])

import serial.tools.list_ports
# import logging
import inspect, socket

# logger = logging.get# logger(__name__)

class muxboard(object):
    def __init__(self, path):
        self._fd = serial.Serial(path, timeout=1.0)

    def __del__(self):
        self._fd.close()

    @staticmethod
    def find():
        for p in serial.tools.list_ports.comports():
            if p[2].startswith("/dev/tty.usbserial") or \
               p[2].startswith("/dev/tty.usbmodem") or \
               p[2].startswith("USB VID:PID=0403:6001") or \
               p[2].startswith("FTDIBUS"):
                print p[0]
                return p[0]

        if sys.platform.startswith('win32'):
            # No device was found. Not all COMPORTS seem to get found by
            # pyserial on Windows. Walk the registry manually and look for
            # any ports that weren't reported by pyserial and see if they
            # respond to the handshake
            import _winreg

            def all_com_ports():
                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "HARDWARE\DEVICEMAP\SERIALCOMM")
                try:
                    i = 0
                    while True:
                        yield _winreg.EnumValue(key, i)
                        i = i + 1
                except WindowsError:
                    pass

            pyserial_comports = [p[0] for p in serial.tools.list_ports.comports()]
            for p in all_com_ports():
                if p[1] not in pyserial_comports:
                    if muxboard(p[1]).handshake():
                        if 'USBSER' in p[0]:
                            #print p[0]
                            return p[1]

    def write(self, val):
        self._fd.write(chr(val))

    def read(self, timeout):
        return self._fd.read()

    def handshake(self):
        self.write(99)
        try:
            return self.read(1.0) == chr(99)
        except:
            return False

    def setswitch(self, index, state):
        if state: state = 1
        state ^= 1
        self.write(self.switch_base + 2 * index + state)

    def setmux(self, index):
        self.write(self.mux_base + index)

    def reset(self):
        self.write(25)
        self.write(26)

    def close(self):
        self._fd.close()

    def __repr__(self):
        return "MuxBoard(%s)" % self._fd.name

    switch_base = 15
    mux_base = 0

def sequence_test(mux):
        mux.reset()
        for i in range(4):
            mux.setswitch(i + 1, 1)
            time.sleep(0.2)
            mux.setswitch(i + 1, 0)
            time.sleep(0.2)
        for i in range(16):
            mux.setmux(i + 1)
            time.sleep(0.2)
        mux.reset()

def install_board_driver():
    import wmi
    c = wmi.WMI()
    USB_MUX_Driver = os.path.join(os.path.dirname(__file__), 'CDM20814_Setup.exe')
    proc = subprocess.Popen(USB_MUX_Driver, shell=True)
    time.sleep(10)
    if proc.poll():
        p = proc.pid
        for process in c.Win32_Process (ProcessId=p):
            process.terminate ()
    print "done"


def ConnectionControl(connection_status, port_index=1, port='s'):
    try:
        mux = muxboard.find()
        #print "mux: ",mux
        muxObj = muxboard(mux)
        #print "muxObj: ",muxObj
        muxHandShake = muxObj.handshake()
        #print "muxHandShake: ",muxHandShake
        if muxHandShake == False:
            mux = muxboard.find()
            #print "mux: ",mux
            muxObj = muxboard(mux)
            #print "muxObj: ",muxObj
            muxHandShake = muxObj.handshake()
            #print "muxHandShake: ",muxHandShake

        if muxHandShake == True:
            #print "Established communication with MUX Board"
            if port == 's' and connection_status != 'reset':
                repeat = 0
                if port_index in range (1, 5):
                    while repeat != 10:
                        muxObj.setswitch(port_index, connection_status)
                        time.sleep(0.1)
                        repeat = repeat + 1
                    return "Pass"
                else:
                    print "incorrect port selection"
                    return "Critical"
            elif port == 'm' and connection_status != 'reset':
                repeat = 0
                if port_index in range (1, 17):
                    while repeat != 3:
                        if connection_status == 0:
                            muxObj.reset()
                            time.sleep(0.1)
                        else:
                            muxObj.setmux(port_index)
                            time.sleep(0.1)
                        repeat = repeat + 1
                    return "Pass"
                else:
                    print "incorrect port selection"
                    return "Critical"
            elif connection_status == 'reset':
                repeat = 0
                print "disconnecting all ports"
                while repeat != 3:
                    muxObj.reset()
                    time.sleep(0.1)
                    muxObj.close()
                return "Pass"
            else:
                print 'you didnt select a valid selection'
                return "Critical"
        elif muxHandShake == False:
            #print "Please verify that your hardware is connected and driver files are installed"
            return "Critical"
    except Exception, e:
            #print "Please verify that your hardware is connected and driver files are installed"
            #print "Error: %s" %e
            return "Critical"



def ConnectDisconnectDevice(connection_status, port_index=1, port='s'):


    """
    ConnectDisconnectDevice connects and disconnects the device from MUX / Switch
    By default it will always consider that your device is connected to simultaneous connection port with
    first port.

    Parameters:
                first parameter is 1(connect) or 0(disconnect)
                Second parameter is number of port of MUX or Switch
                Third parameter is to control the port (MUX or Switch).
                Forth parameter is "reset". You can send just 'reset' and it will set all the ports to 0.
    Example:
            ConnectDisconnectDevice(1) --> it will connect the device to switch 1 by default
            ConnectDisconnectDevice(0) --> it will disconnect the device from switch 1 by default
            ConnectDisconnectDevice(1,2,'s') --> sets the second port of simultaneous port to 1 (connect)
            ConnectDisconnectDevice(0,2,'s') --> sets the second port of simultaneous port to 0 (disconnect)
            ConnectDisconnectDevice(1,14,'m') --> sets the 14th port of MUX port to 1 (connect)
            ConnectDisconnectDevice(0,14,'m') --> sets the 14th port of MUX port to 1 (disconnect)
            ConnectDisconnectDevice('reset') --> disconnects all the ports





    """
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        if connection_status == 1:
            connect_string = 'Connecting'
        elif connection_status == 0:
            connect_string = 'Disconnecting'
        elif connection_status == 'reset':
            connect_string = 'Resetting'
        else:
            connect_string = 'Invalid operation'
        #print "%s MuxBoard port %s%s" % (connect_string, port, port_index)
        print "%s MuxBoard port %s%s" % (connect_string, port, port_index)
        return ConnectionControl(connection_status, port_index, port)

    except Exception, e:
        print e
        print "%s MuxBoard port %s%s" % (connect_string, port, port_index)
        return "Critical"


#
#x =1
#while x==1:
#    print "conneecint to port 1: high"
#    ConnectionControl(1)
#    time.sleep(10)
#    print "disconnecting port 1: low"
#    ConnectionControl(0)
#    time.sleep(5)
#    print "conneecint to port 2: high"
#    ConnectionControl(1,2,'s')
#    time.sleep(10)
#    print "disconnecting port 2: low"
#    ConnectionControl(0,2,'s')
#    time.sleep(5)




#print ConnectionControl(1)
#print ConnectDisconnectDevice(0)

# if __name__ == '__main__':
#     ConnectDisconnectDevice(1,2,'m')
