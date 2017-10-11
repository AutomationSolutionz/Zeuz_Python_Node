#!/usr/bin/env python
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/tkinter.pdf
# Written by Lucas Donkers
# Function: Front-end to Zeuz_Node.py and settings.conf

import Tkinter as tk
from Crypto.Cipher import ARC4 # Password encryption
from base64 import b64encode, b64decode # Password encoding
import tkMessageBox
import os.path, thread, sys, time
from Utilities import ConfigModule
from ZeuZ_Node import Login, disconnect_from_server, get_team_names, get_project_names

# Find node id file
if sys.platform  == 'win32':
    node_id_filename = os.path.join(os.getenv('USERPROFILE'), 'Desktop', 'node_id.conf')
else:
    node_id_filename = os.path.join(os.getenv('HOME'), 'Desktop', 'node_id.conf')

gui_title = 'Zeuz Node'
help_text = "\
Zeuz Node Help\n\n\
Description:\n\
This is a graphical front-end for the ZeuZ_Node.py script. It provides an interface to configure the settings, running the Zeuz Node, and displaying the output. Either this, or the ZeuZ_Node.py script can be run with the same effect.\n\n\
Show Advance Settings:\tDisplay more settings including server, port, screenshot, etc\n\
Save Settings:\tSave all settings (whether displayed or not)\n\
Quit: Exit immediately - Any running automation will be stopped\n\
Online: Start the Zeuz_Node.py script, login to the Zeuz server, and wait for a Test Case to be deployed\n\
Refresh: Gets the list of Teams the current user has access to\n\n\
"
     
class Application(tk.Frame):
    show_adv_settings = False
    run = False
    widgets = {} # Holds the text entry widget handles under the line name
    team = None # !!! Needs to be added to widgets{}, update save_all() as wel
    team_choices = [] # !!! Needs to be added to widgets{}, update save_all() as wel
    project = None
    project_choices = []
    settings_modified = []
    settings_saved = int(time.time())

    entry_width = 50
    button_width = 20
    colour_tag = 0
    colour_debug = 'blue'
    colour_passed = 'green'
    colour_warning = 'orange'
    colour_failed = 'red'
    colour_default = 'black'
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.createWidgets()

    def createWidgets(self):
        # Create main frame and sub-frames to contain everything
        self.mainframe = tk.Frame()
        self.mainframe.grid(sticky = 'nw')
        
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
        self.help_button = tk.Button(self.topframe, text = 'Help', width = self.button_width, command = self.show_help)
        self.help_button.grid(row = 0, column = 3, sticky = 'w')

        self.settings_button = tk.Button(self.topframe, text='Show Advanced Settings', width = self.button_width, command=self.advanced_settings)
        self.settings_button.grid(row = 1, column = 0)

        self.save_button = tk.Button(self.topframe, text='Save Settings', width = self.button_width, command=lambda: self.save_all(True))
        self.save_button.grid(row = 1, column = 1)

        self.quitButton = tk.Button(self.topframe, text='Quit', width = self.button_width, command=self.teardown)
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
                self.widgets['Authentication'][option] = {}
                
                if option == 'password':
                    if value != '': value = self.password(False, 'zeuz', value) # Decrypt password
                    self.widgets['Authentication'][option]['widget'] = tk.Entry(self.basic_settings_frame, show = '*', width = self.entry_width)
                    self.widgets['Authentication'][option]['widget'].insert('end', value)
                elif option == 'team':
                    # Setup refresh link
                    self.team_refresh = tk.Label(self.basic_settings_frame, text = 'Refresh', fg = 'blue', cursor = 'hand2')
                    self.team_refresh.grid(row = row, column = 1, sticky = 'e')
                    self.team_refresh.bind('<Button-1>', lambda e: self.get_teams()) # Bind label to action
                    
                    # Configure drop down menu
                    self.team = tk.StringVar(self) # Initialize drop down variable
                    self.team.set('') # Need to initialize this, so OptionMenu will work
                    self.team_choices.append(value) # Need to initialize this, so OptionMenu will work
                    self.widgets['Authentication'][option]['widget'] = tk.OptionMenu(self.basic_settings_frame, self.team, *self.team_choices)
                    self.get_teams() # Get list of teams from the server, populate the list
                    self.team.set(value) # Set menu to value in config file
                elif option == 'project':
                    # Configure drop down menu
                    self.project = tk.StringVar(self)
                    self.project.set('') # Need to initialize this, so OptionMenu will work
                    self.project_choices.append(value) # Need to initialize this, so OptionMenu will work
                    self.widgets['Authentication'][option]['widget'] = tk.OptionMenu(self.basic_settings_frame, self.project, *self.project_choices)
                    self.project.set(value) # Set menu to value in config file
                else:
                    self.widgets['Authentication'][option]['widget'] = tk.Entry(self.basic_settings_frame, width = self.entry_width)
                    self.widgets['Authentication'][option]['widget'].insert('end', value)
                
                self.widgets['Authentication'][option]['widget'].grid(row = row, column = 1, sticky = 'w')
                row += 1
        
        # Put a trace on the team field, so we can automatically change the project when the team is changed
        self.team.trace('w', self.switch_teams)
        if self.team.get() != '':
            self.get_projects(self.team.get()) # Get list of projects from the server for the curent team, populate the list

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
                            self.widgets[section][option] = {}
                            value = ConfigModule.get_config_value(section, option)
                            tk.Label(self.adv_settings_frame, text = option).grid(row = row, column = 0, sticky = 'w')
                            if value.lower() in ('true', 'false'):
                                self.widgets[section][option]['check'] = tk.IntVar()
                                self.widgets[section][option]['widget'] = tk.Checkbutton(self.adv_settings_frame, variable = self.widgets[section][option]['check'])
                                if value.lower() == 'true': self.widgets[section][option]['check'].set(1) # Enable checkbox
                                else: self.widgets[section][option]['check'].set(0) # Disable checkbox
                            else:
                                self.widgets[section][option]['widget'] = tk.Entry(self.adv_settings_frame, width = self.entry_width)
                                self.widgets[section][option]['widget'].insert('end', value)
                            self.widgets[section][option]['widget'].grid(row = row, column = 1, sticky = 'w')
                            row += 1
        
        # Create text area for log output
        self.log = tk.Text(self.rightframe, width = 70, height = 30)
        self.log.grid(row = 0, column = 0, sticky = 'w')
        
        # Set initial focus on enable button
        self.startButton.focus_set()
        
        # If go online at start is set, go online
        if self.widgets['RunDefinition']['go_online_at_start']['check'].get(): self.read_mod()
        
    def show_help(self):
        ''' Display help information in the log window '''
        self.log.delete(0.0, 'end')
        self.log.insert('end', help_text)

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
            disconnect_from_server() # Tell Zeuz_Node.py to stop
            self.log.insert('end', '\nDisconnecting from server\n')
            self.log.see('end')
        else:
            self.run = True
            self.startButton.configure(text = 'Offline')
            self.log.delete(0.0, 'end') # Clear previous log
            thread.start_new_thread(Login,()) # Execute Zeuz_Node.py
            if self.node_id.get() == '': root.after(5000, lambda: self.read_node_id(self.node_id)) # If no node id was read or specified, wait a few seconds for zeuz_node.py to populate the node id file, and read it 

    def read_log(self, data):
        # Determine log line type, so we can colour code it
        if data[:5] == 'DEBUG':
            colour = self.colour_debug
        elif data[:6] == 'PASSED':
            colour = self.colour_passed
        elif data[:7] == 'WARNING':
            colour = self.colour_warning
        elif data[:6] == 'FAILED':
            colour = self.colour_failed
        elif data[:5] == 'ERROR':
            colour = self.colour_failed
        elif 'online with name' in data:
            colour = self.colour_passed
        else:
            colour = self.colour_default

        # Set colour and print to textbox
        self.log.tag_config('a%s' % self.colour_tag, foreground = colour) # Colour code line
        self.log.insert('end', data, 'a%s' % self.colour_tag) # Insert into textbox
        self.log.see('end') # Keep end in sight
        self.colour_tag += 1 # Increment tag counter for next line
        
        # Check if node went offline, but we didn't tell it to. If so, flip the Offline button
        if data == 'Zeuz Node Offline' and self.run == True:
            self.read_mod()
        
    def password(self, encrypt, key, pw):
        ''' Encrypt, decrypt password and encode in plaintext '''
        # This is just an obfuscation technique, so the password is not immediately seen by users
        # Zeuz_Node.py has a similar function that will need to be updated if this is changed
        
        try:
            obj = ARC4.new(key)
            if encrypt == True:
                return b64encode(obj.encrypt(pw))
            else:
                return obj.decrypt(b64decode(pw))
        except:
            tkMessageBox.showerror('Error', 'Error decrypting password. Enter a new password')
            return ''
        
    def read_node_id(self, w):
        if os.path.exists(node_id_filename):
            node_id = ConfigModule.get_config_value('UniqueID', 'id', node_id_filename)
            w.insert('end', node_id.strip())
                
    def save_all(self, save = False):
        ''' Check for changes, and if found, save them to disk '''
        # If save = True, save any modified value to disk, if False, simply check if there were changes
        
        try:
            modified = False
            saved = False
            cnt = 0
            # Write node_id.conf
            node_id = str(self.node_id.get()).strip()
            node_id = node_id.replace(' ', '_')
            if node_id != '':
                if len(self.settings_modified) <= cnt: # First run, populate modifier check
                    self.settings_modified.append(node_id)
                elif save and node_id != self.settings_modified[cnt]: # Explicit save, and this value is changed
                    ConfigModule.add_config_value('UniqueID', 'id', node_id, node_id_filename) # Save to disk
                    self.settings_modified[cnt] = node_id # Update the modified check
                    saved = True # Indicate we should tell the user this was saved
                elif node_id != self.settings_modified[cnt]: # This value is different, signal to save
                    modified = True
            cnt += 1
            
            # Write settings.conf
            for section in self.widgets:
                for option in self.widgets[section]:
                    if option == 'team':
                        value = self.team.get()
                    elif option == 'project':
                        value = self.project.get()
                    elif 'check' in self.widgets[section][option]: # If checkbox, convert check/uncheck into text
                        if self.widgets[section][option]['check'].get() == 1: value = 'True'
                        else: value = 'False'
                    else:
                        value = str(self.widgets[section][option]['widget'].get()).strip() # Get value
                        if option == 'password': value = self.password(True, 'zeuz', value) # Encrypt password

                    if len(self.settings_modified) <= cnt: # First run, populate modifier check
                        self.settings_modified.append(value)
                    elif save and value != self.settings_modified[cnt]:
                        ConfigModule.add_config_value(section, option, value)
                        self.settings_modified[cnt] = value
                        saved = True
                    elif value != self.settings_modified[cnt]:
                        modified = True
                    cnt += 1
            
            # Check if we should save
            if saved: # Yes, explicit save call, so tell the user
                if int(time.time()) - self.settings_saved > 5: # But, not too often
                    self.log.insert('end', 'Settings Updated\n')
                    self.log.see('end')
                    self.settings_saved = int(time.time())
            elif modified: # Change occurred, call this function again, and tell it to save
                self.save_all(True)
            if not saved: root.after(500, lambda: thread.start_new_thread(root.save_all, ())) # Reschedule the settings modified check
        except Exception, e:
            #tkMessageBox.showerror('Error', 'Settings Not Saved - Trying again in 10 seconds: %s' % e)
            self.log.insert('end', 'Settings Not Saved - Trying again in 10 seconds: %s\n' % e)
            self.log.see('end')
            root.after(10000, lambda: thread.start_new_thread(root.save_all, ()))

    def switch_teams(self, a, b, c):
        self.project.set('') # Clear Project menu
        self.get_projects(self.team.get()) # Update available options in project menu
        
    def get_teams(self):
        self.team_choices = get_team_names()
        self.widgets['Authentication']['team']['widget']['menu'].delete(0, 'end')
        for team in self.team_choices:
            self.widgets['Authentication']['team']['widget']['menu'].add_command(label = team, command=tk._setit(self.team, team))
        if self.team_choices == []:
            tkMessageBox.showerror('Error', 'No teams could be found. Server, port, username, or password may be wrong')

    def get_projects(self, team):
        self.project_choices = get_project_names(team)
        self.widgets['Authentication']['project']['widget']['menu'].delete(0, 'end')
        for project in self.project_choices:
            self.widgets['Authentication']['project']['widget']['menu'].add_command(label = project, command=tk._setit(self.project, project))

    def teardown(self):
        logger_teardown()
        
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        #self.log = open("File.log", "w")

    def write(self, message):
        #self.terminal.write(message) # Print to terminal
        root.read_log(message) # Print to log window

    def close(self):
        pass
        #self.log.close()

def logger_setup():
    global root
    global log_window
    oerr = sys.stderr # Backup handle for STDOUT/ERR
    oout = sys.stdout
    Log = Logger() # Create Logging instance
    sys.stdout = Log # Capture STDOUT output
    sys.stderr = Log # Capture STDERR output
    return Log, oout, oerr

def logger_teardown():
    global Log, oout, oerr
    Log.close()
    sys.stderr = oerr
    sys.stdout = oout
    quit()


if __name__ == '__main__':
    # Root window setup
    Log, oout, oerr = (None, None, None) # Initilize logger variables
    r = tk.Tk() # Create instance of Tk for bind
    r.bind("<Escape>", lambda e: logger_teardown()) # Bind escape to exit
    r.protocol("WM_DELETE_WINDOW", logger_teardown) # Catch any types of exits and teardown properly
    if sys.platform == 'win32':
        icon_img = 'zeuz.gif'
    else:
        icon_img = 'zeuz.png'
    if os.path.exists(icon_img):
        try:
            icon = tk.PhotoImage(file = icon_img) # Import image into format that next line can understand
            r.call('wm', 'iconphoto', r._w, icon) # Put icon on titlebar
        except: pass # Not a big deal if this fails

    # Main window setup
    root = Application() # Create GUI instance
    root.master.title(gui_title) # Set title
    Log, oout, oerr = logger_setup() # Redirect STDOUT/ERR to log window
    root.after(500, lambda: thread.start_new_thread(root.save_all, ())) # Schedule the settings modified check

    # Execute GUI
    root.mainloop()
