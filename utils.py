import os
import _thread
from Framework.Utilities import self_updater
from tkinter import *

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