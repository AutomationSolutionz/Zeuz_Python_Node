import os
import time
import select
import sys
import platform
import _thread
from Framework.Utilities import self_updater
from tkinter import Toplevel, Label, Button

class MyDialogBox:

    def __init__(self,root):
        self.UPDATE_MSG = 'A Zeuz Node update is available. Do you want to download and install it?'
        self.DISPLAY_DURATION = 6000
        self.root = root
        top = self.top = Toplevel()
        top.title('Update')
        # a = tkinter.messagebox.askyesno("Print", "Print this report?")
        # print(a)
        Label(top, text=self.UPDATE_MSG).grid(row=0,column=0,rowspan=2,columnspan=10, padx=20, pady=20)
        yes_button = Button(top, text="yes", command=self.yesf).grid(row=3,column=4)
        yes_button = Button(top, text="no" , command=self.nof).grid(row=3,column=5)

        top.after(self.DISPLAY_DURATION, top.destroy)

    def nof(self):
        print("no")
        self.top.destroy()
        # self.root.say_hi()

    def yesf(self):
        print("yes")
        self.top.destroy()
        _thread.start_new_thread(self_updater.main,
                                 (os.path.dirname(os.path.realpath(__file__)).replace(os.sep + 'Framework' + os.sep + 'Utilities', ''),))
        self.root.after(10000, self.root.check_for_updates)  # Checks if install is complete


class TimeoutExpired(Exception):
    pass

def input_with_timeout1(prompt, timeout, timer=time.monotonic):
    import msvcrt
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\n':   #XXX check what Windows returns here
                return ''.join(result[:-1])
        time.sleep(0.04) # just to yield to other processes/threads
    raise TimeoutExpired




def input_with_timeout2(prompt, timeout):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [],[], timeout)
    if ready:
        return sys.stdin.readline().rstrip('\n') # expect stdin to be line-buffered
    raise TimeoutExpired

def input_with_timeout(prompt, timeout):
    operating_system = platform.system()
    if operating_system in ["Linux", "Darwin"]:
        return input_with_timeout2(prompt, timeout)
    elif operating_system == "Windows":
        return input_with_timeout1(prompt, timeout)