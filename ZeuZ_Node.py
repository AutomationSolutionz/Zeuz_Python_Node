#!/usr/bin/env python
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/tkinter.pdf
# Written by Lucas Donkers
# Function: Front-end to Zeuz_Node.py and settings.conf

import Tkinter as tk
from Crypto.Cipher import ARC4 # Password encryption
from base64 import b64encode, b64decode # Password encoding
import tkMessageBox
import os.path, thread, sys, time

os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Framework')) # Move to Framework directory, so all modules can be seen
from Framework.Utilities import ConfigModule
from Framework.ZN_CLI import Login, disconnect_from_server, get_team_names, get_project_names, check_server_online

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
    show_adv_settings = False # Toggles settings button
    run = False # Toggles online button
    widgets = {} # Holds the text entry widget handles under the line name
    settings_modified = [] # Holds the last seen settings, so we can check if we need to auto-save
    settings_saved = int(time.time()) # "Settings updated" timer
    advanced_settings_frames = []

    # Widget settings
    entry_width = 50
    button_width = 20
    node_id_size = 10 # Max length of node ID - must match that specified in CommonUtil.MachineInfo()
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
        self.node_id = tk.Entry(self.topframe, validate = "key", validatecommand = (self.register(self.onValidate), '%d', '%S')) # See onValidate() for more info
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
        
        # Read the remaining settings data, and add widgets to window
        self.settings_frame = tk.Frame(self.leftframe)
        self.settings_frame.grid(sticky = 'w')
        row = 0
        sections = ConfigModule.get_all_sections()
        if sections:
            for section in sections:
                self.widgets[section] = {}
                self.widgets[section]['widget'] = {}
                self.widgets[section]['frame'] = tk.Frame(self.settings_frame)
                self.advanced_settings_frames.append(section) # Store all section names, so we know which to display when we click the show advanced settings button
                tk.Label(self.widgets[section]['frame'], text = section, fg="red").grid(row = row, column = 0, pady = 10, columnspan = 2)
                row += 1
                options = ConfigModule.get_all_option(section)
                if options:
                    for option in options:
                        self.widgets[section]['widget'][option] = {}
                        value = ConfigModule.get_config_value(section, option)
                        tk.Label(self.widgets[section]['frame'], text = option).grid(row = row, column = 0, sticky = 'w')
                        
                        if option == 'password': # Add asterisk to hide password
                            if value != '': value = self.password(False, 'zeuz', value) # Decrypt password
                            self.widgets['Authentication']['widget'][option]['widget'] = tk.Entry(self.widgets[section]['frame'], show = '*', width = self.entry_width)
                            self.widgets['Authentication']['widget'][option]['widget'].insert('end', value)
                        
                        elif option in ('team', 'project'): # Set these as drop down menus
                            if option == 'team': # Put refresh link beside team
                                # Setup refresh link
                                self.team_refresh = tk.Label(self.widgets[section]['frame'], text = 'Refresh', fg = 'blue', cursor = 'hand2')
                                self.team_refresh.grid(row = row, column = 1, sticky = 'e')
                                self.team_refresh.bind('<Button-1>', lambda e: self.get_teams()) # Bind label to action
                            
                            # Configure drop down menu
                            self.widgets['Authentication']['widget'][option]['dropdown'] = tk.StringVar(self) # Initialize drop down variable
                            self.widgets['Authentication']['widget'][option]['dropdown'].set('') # Need to initialize this, so OptionMenu will work
                            self.widgets['Authentication']['widget'][option]['choices'] = []
                            self.widgets['Authentication']['widget'][option]['choices'].append(value) # Need to initialize this, so OptionMenu will work
                            self.widgets['Authentication']['widget'][option]['widget'] = tk.OptionMenu(self.widgets[section]['frame'], self.widgets['Authentication']['widget'][option]['dropdown'], *self.widgets['Authentication']['widget'][option]['choices'])
                            if option == 'team': self.get_teams(True) # Get list of teams from the server, populate the list
                            self.widgets['Authentication']['widget'][option]['dropdown'].set(value) # Set menu to value in config file
                        
                        elif value.lower() in ('true', 'false'):
                            self.widgets[section]['widget'][option]['check'] = tk.IntVar()
                            self.widgets[section]['widget'][option]['widget'] = tk.Checkbutton(self.widgets[section]['frame'], variable = self.widgets[section]['widget'][option]['check'])
                            if value.lower() == 'true': self.widgets[section]['widget'][option]['check'].set(1) # Enable checkbox
                            else: self.widgets[section]['widget'][option]['check'].set(0) # Disable checkbox
                        
                        else:
                            self.widgets[section]['widget'][option]['widget'] = tk.Entry(self.widgets[section]['frame'], width = self.entry_width)
                            self.widgets[section]['widget'][option]['widget'].insert('end', value)
                        self.widgets[section]['widget'][option]['widget'].grid(row = row, column = 1, sticky = 'w')
                        row += 1
        
        # Put a trace on the team field, so we can automatically change the project when the team is changed
        self.widgets['Authentication']['widget']['team']['dropdown'].trace('w', self.switch_teams)
        if self.widgets['Authentication']['widget']['team']['dropdown'].get() != '':
            self.get_projects(self.widgets['Authentication']['widget']['team']['dropdown'].get()) # Get list of projects from the server for the curent team, populate the list

        # Create text area for log output
        self.log = tk.Text(self.rightframe, width = 70, height = 30)
        self.log.grid(row = 0, column = 0, sticky = 'w')
        
        # Set initial focus on enable button
        self.startButton.focus_set()
        
        # If go online at start is set, go online
        if self.widgets['RunDefinition']['widget']['go_online_at_start']['check'].get(): self.read_mod()
        
    def start_up_display(self):
        text_check = self.widgets['Authentication']['widget']['team']['dropdown'].get()
        if text_check == 'YourTeamNameGoesHere':
            self.widgets['Server']['frame'].grid(row = 0, column = 0, sticky = 'w')
            self.continuous_server_check() # Tell program to constantly check for server connection until we connect
        else: # Show default section
            self.widgets['Authentication']['frame'].grid(row = 0, column = 0, sticky = 'w')
        
    def continuous_server_check(self, check = True):
        # Helps the user provide required login information by showing specific fields polling the server until everyting is set
        # Check if server address is set
        if check: result = check_server_online()
        else: result = True
        
        if result == False: # Server likely not configured, or not fully entered
            root.after(1000, self.continuous_server_check)
            
        else: # Server is fully set. Now need to check if we can login with user/pass
            self.widgets['Authentication']['frame'].grid(row = 1, column = 0, sticky = 'w')
            user = self.widgets['Authentication']['widget']['username']['widget'].get()
            pw = self.widgets['Authentication']['widget']['password']['widget'].get()
            if user != '' and pw != '': # User/pass set, so try to login
                result = self.get_teams(True) # Check if user/password is set, and populate team
                if result == False: # Can't login, try again
                    root.after(1000, lambda: self.continuous_server_check(False))
                else: # First run completed, everything is properly set. Clear the team/project, so the user knows to set them
                    self.widgets['Authentication']['widget']['team']['dropdown'].set('')
                    self.widgets['Authentication']['widget']['project']['dropdown'].set('')
            else: # No user/pass, try again
                root.after(1000, lambda: self.continuous_server_check(False))
            
        
    def onValidate(self, ctype, S):
        # Limit text to specified length and characters
        # https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter/4140988#4140988
        # Caveats: Can't copy/paste/w.insert() more than one character at a time
        
        chars = '0123456789abcdefghijklmnopqrstuvwxyz-_'

        if int(ctype) == 0: return True # Allow deletions
    
        if len(self.node_id.get()) < self.node_id_size: # Allow this length
            if S in chars: return True # Allow these characters
            else: return False
        else: return False
        
    def show_help(self):
        ''' Display help information in the log window '''
        self.log.delete(0.0, 'end')
        self.log.insert('end', help_text)

    def advanced_settings(self):
        ''' Dynamically load the rest of the settings and display, or if already displayed, remove them '''

        if self.show_adv_settings:
            self.show_adv_settings = False
            self.settings_button.configure(text='Show Advanced Settings')
            for section in self.advanced_settings_frames:
                self.widgets[section]['frame'].grid_forget()
            self.widgets['Authentication']['frame'].grid(row = 0, column = 0, sticky = 'w')
        else:
            self.show_adv_settings = True
            self.settings_button.configure(text='Hide Advanced Settings')
            self.widgets['Authentication']['frame'].grid(row = 0, column = 0, sticky = 'w')
            row = 1
            for section in self.advanced_settings_frames:
                self.widgets[section]['frame'].grid(row = row, column = 0, sticky = 'w')
                row += 1
            

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
        # This is a separate file on the desktop
        if os.path.exists(node_id_filename):
            node_id = ConfigModule.get_config_value('UniqueID', 'id', node_id_filename).strip()
            for c in node_id: w.insert('end', c) # We have to write characters one at a time due to how onValidate() works
                
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
                for option in self.widgets[section]['widget']:
                    if 'dropdown' in self.widgets[section]['widget'][option]: # Has a drop down menu
                        value = self.widgets[section]['widget'][option]['dropdown'].get()
                    
                    elif 'check' in self.widgets[section]['widget'][option]: # If checkbox, convert check/uncheck into text
                        if self.widgets[section]['widget'][option]['check'].get() == 1: value = 'True'
                        else: value = 'False'
                    
                    else: # Widget is a textbox
                        value = str(self.widgets[section]['widget'][option]['widget'].get()).strip() # Get value
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
        # When user changes the team, pull the list of projects for that team
        self.widgets['Authentication']['widget']['project']['dropdown'].set('') # Clear Project menu
        self.get_projects(self.widgets['Authentication']['widget']['team']['dropdown'].get()) # Update available options in project menu
        
    def get_teams(self, noerror = False):
        # Populate drop down with teams user has access to
        self.widgets['Authentication']['widget']['team']['choices'] = get_team_names() # Get list of teams from server
        self.widgets['Authentication']['widget']['team']['widget']['menu'].delete(0, 'end') # Clear drop down menu
        for team in self.widgets['Authentication']['widget']['team']['choices']: # For each new team
            self.widgets['Authentication']['widget']['team']['widget']['menu'].add_command(label = team, command=tk._setit(self.widgets['Authentication']['widget']['team']['dropdown'], team)) # Add the team to the drop down menu
        if self.widgets['Authentication']['widget']['team']['choices'] == []: # If nothing was returned
            if noerror == False: tkMessageBox.showerror('Error', 'No teams could be found. Server, port, username, or password may be wrong') # Display an error
            return False
        return True

    def get_projects(self, team):
        # Populate drop down with projects user has access to, for a given team
        self.widgets['Authentication']['widget']['project']['choices'] = get_project_names(team) # Get list of projects for the selected team
        self.widgets['Authentication']['widget']['project']['widget']['menu'].delete(0, 'end') # Clear drop down menu
        for project in self.widgets['Authentication']['widget']['project']['choices']: # For each new project
            self.widgets['Authentication']['widget']['project']['widget']['menu'].add_command(label = project, command=tk._setit(self.widgets['Authentication']['widget']['project']['dropdown'], project)) # Add the project to the drop down menu

    def teardown(self):
        logger_teardown()
        
class Logger(object):
    # Redirects all stdout/err to the GUI log window
    # This is the simplest method for getting all Framework to log to the window. Due to how different modules are started, we can't get a centralized system to record and feed back to the GUI
    def __init__(self):
        self.terminal = sys.stdout
        #self.log = open("File.log", "w") # Save in case we want to start logging to disk

    def write(self, message):
        #self.terminal.write(message) # Print to terminal (DEBUGGING)
        root.read_log(message) # Print to log window

    def close(self):
        pass
        #self.log.close() # Save in case we want to start logging to disk

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
    root.start_up_display() # Determine if this is the first run, and display widgets accordingly
        

    # Execute GUI
    root.mainloop()
