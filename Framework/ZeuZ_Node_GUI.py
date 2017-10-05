#!/usr/bin/env python
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/tkinter.pdf
import Tkinter as tk
import tkMessageBox
import os, os.path, thread
from Utilities import ConfigModule, CommonUtil
from ZeuZ_Node import Login

node_id_filename = os.path.join(os.getenv('HOME'), 'Desktop', 'node_id.conf')
log_timer = 200 # TIme in ms to check for log lines
     
class Application(tk.Frame):
    show_adv_settings = False
    run = False
    widgets = {} # Holds the text entry widget handles under the line name
    entry_width = 50
    button_width = 20
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        # Create main frame and sub-frames to contain everything
        self.mainframe = tk.Frame()
        self.mainframe.grid(sticky = 'nw')
        self.mainframe.bind("<Escape>", quit)
        
        self.leftframe = tk.Frame(self.mainframe)
        self.leftframe.grid(row = 0, column = 0, sticky = 'nw')
        
        self.rightframe = tk.Frame(self.mainframe)
        self.rightframe.grid(row = 0, column = 1, sticky = 'nw')
        
        # Top Left buttons
        self.topframe = tk.Frame(self.leftframe)
        self.topframe.grid(sticky = 'w')
        
        tk.Label(self.topframe, text = 'Node ID', fg="red").grid(row = 0, column = 0, sticky = 'e')
        self.node_id = tk.Entry(self.topframe)
        self.node_id.grid(row = 0, column = 1, columnspan = 2, sticky = 'w')
        self.read_node_id(self.node_id)

        self.settings_button = tk.Button(self.topframe, text='Show Advanced Settings', width = self.button_width, command=self.advanced_settings)
        self.settings_button.grid(row = 1, column = 0)

        self.save_button = tk.Button(self.topframe, text='Save Settings', width = self.button_width, command=self.save_all)
        self.save_button.grid(row = 1, column = 1)

        self.quitButton = tk.Button(self.topframe, text='Quit', width = self.button_width, command=self.quit)
        self.quitButton.grid(row = 1, column = 2)
        
        self.startButton = tk.Button(self.topframe, text='Online', width = self.button_width, command=self.read_mod)
        self.startButton.grid(row = 1, column = 3)
        
        # Basic Settings
        self.basic_settings_frame = tk.Frame(self.leftframe)
        self.basic_settings_frame.grid(sticky = 'w')
        
        # Dynamically load the Authentication section - this is displayed all the time
        tk.Label(self.basic_settings_frame, text = 'Authentication', fg="red").grid(row = 0, column = 0, columnspan = 2)
        row = 1
        options = ConfigModule.get_all_option('Authentication')
        if options:
            self.widgets['Authentication'] = {}
            for option in options:
                value = ConfigModule.get_config_value('Authentication', option)
                tk.Label(self.basic_settings_frame, text = option).grid(row = row, column = 0, sticky = 'w')
                if option == 'password':
                    self.widgets['Authentication'][option] = tk.Entry(self.basic_settings_frame, show = '*', width = self.entry_width)
                else:
                    self.widgets['Authentication'][option] = tk.Entry(self.basic_settings_frame, width = self.entry_width)
                self.widgets['Authentication'][option].grid(row = row, column = 1, sticky = 'w')
                self.widgets['Authentication'][option].insert('end', value)
                row += 1

        # Read the remaining settings data, and add widgets to window
        self.adv_settings_frame = tk.Frame(self.leftframe)
        row = 0
        sections = ConfigModule.get_all_sections()
        if sections:
            for section in sections:
                if section != 'Authentication':
                    self.widgets[section] = {}
                    #tk.Frame(self.adv_settings_frame, height = 1, width = 500, bg = 'black').grid(row = row, columnspan = 2)
                    #row += 1
                    tk.Label(self.adv_settings_frame, text = section, fg="red").grid(row = row, column = 0, pady = 10, columnspan = 2)
                    #tk.Frame(self.adv_settings_frame, height = 1, width = 500, bg = 'black').grid(row = row, column = 1)
                    row += 1
                    options = ConfigModule.get_all_option(section)
                    if options:
                        for option in options:
                            value = ConfigModule.get_config_value(section, option)
                            tk.Label(self.adv_settings_frame, text = option).grid(row = row, column = 0, sticky = 'w')
                            self.widgets[section][option] = tk.Entry(self.adv_settings_frame, width = self.entry_width)
                            self.widgets[section][option].grid(row = row, column = 1, sticky = 'w')
                            self.widgets[section][option].insert('end', value)
                            row += 1
        
        # Create text area for log output
        self.log = tk.Text(self.rightframe, width = 70, height = 30)
        self.log.grid(row = 0, column = 0, sticky = 'w')
        
        # Set initial focus on enable button
        self.startButton.focus_set()
        
    def advanced_settings(self):
        ''' Dynamically load the rest of the settings and display, or if already displayed, remove them '''
        
        if self.show_adv_settings:
            self.show_adv_settings = False
            self.settings_button.configure(text='Show Advanced Settings')
            self.adv_settings_frame.grid_forget()
        else:
            self.show_adv_settings = True
            self.settings_button.configure(text='Hide Advanced Settings')
            self.adv_settings_frame.grid(sticky = 'w')
            

    def read_mod(self):
        if self.run:
            self.run = False
            self.startButton.configure(text = 'Online')
        else:
            self.run = True
            self.startButton.configure(text = 'Offline')
            thread.start_new_thread(Login,()) # Execute Zeuz_Node.py
            root.after(log_timer, self.read_log)

    def read_log(self):
        data = CommonUtil.give_log_to_gui()
        if data: self.log.insert('end', data + "\n")
        if self.run: root.after(log_timer, self.read_log)
        
        
    def read_node_id(self, w):
        if os.path.exists(node_id_filename):
            node_id = ConfigModule.get_config_value('UniqueID', 'id', node_id_filename)
            w.insert('end', node_id.strip())
                
    def save_all(self):
        try:
            # Write node_id.conf
            node_id = str(self.node_id.get()).strip()
            node_id = node_id.replace(' ', '_')
            if node_id != '':
                ConfigModule.add_config_value('UniqueID', 'id', node_id, node_id_filename)
            
            # Write settings.conf
            for section in self.widgets:
                for option in self.widgets[section]:
                    value = str(self.widgets[section][option].get()).strip()
                    ConfigModule.add_config_value(section, option, value)
                    
            tkMessageBox.showinfo('Info', 'Settings Updated')
        except:
            tkMessageBox.showerror('Error', 'Settings Not Saved - Try again')

root = Application()
root.master.title('Sample application')
#root.bind("<Escape>", quit)
root.mainloop()
