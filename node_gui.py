#!/usr/bin/env python
# Written by Lucas Donkers
# Function: Front-end to node_cli.py and settings.conf
# Issues: try/except doesn't always work for everything on windows (base64). Python crashes on windows when we use root.after() to poll the widgets

import os.path, _thread, sys, time, traceback, base64
import webbrowser
# Import colorama for console color support
from colorama import init as colorama_init
from colorama import Fore

# Initialize colorama for the current platform
from utils import MyDialogBox

colorama_init(autoreset=True)



def detect_admin():
    # Windows only - Return True if program run as admin

    import subprocess as s
    if sys.platform == 'win32':
        command = 'net session >nul 2>&1' # This command can only be run by admin
        try: output = s.check_output(command, shell=True) # Causes an exception if we can't run
        except: return False
    return True


def pass_encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = (ord(clear[i]) + ord(key_c)) % 256
        enc.append(enc_c)
    return base64.urlsafe_b64encode(bytes(enc))

def install_missing_modules(req_file_path=True):
    '''
    Purpose: This function will check all the installed modules, compare with what is in requirements.txt file 
    If anything is missing from requirements.txt file, it will install them only
    '''
    try:
        #get all the pip modules that are installed
        #getting all pip from requirements.txt file
        if req_file_path == True:
            req_file_path = os.path.dirname(os.path.abspath(__file__))+os.sep + 'requirements.txt'
        with open(req_file_path) as fd:
            req_list = fd.read().splitlines()
        #get all the modules installed from freeze
        try:
            from pip._internal.operations import freeze
        except ImportError:  # pip < 10.0
            from pip.operations import freeze
        freeze_list = freeze.freeze()
        alredy_installed_list = []
        for p in freeze_list:
            alredy_installed_list.append(str (p.split("==")[0]))
        #installing any missing modules
        for each in req_list:
            if each not in alredy_installed_list:
                subprocess.check_call([sys.executable, "-m", "pip", "install", each])        
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print (Error_Detail)
        return True
        
# Have user install Tk if this fails - we try to do it for them first
try:
    import tkinter as tk # http://infohost.nmt.edu/tcc/help/pubs/tkinter/tkinter.pdf
    import subprocess
except:
    import subprocess as s
    print(Fore.RED + "Tkinter is not installed. This is required to start the graphical interface. Please enter the root password to install if asked.")

    if sys.platform == 'win32':
        try:
            # Elevate permissions
            if not detect_admin():
                os.system('powershell -command Start-Process "python \'%s\'" -Verb runAs' % sys.argv[0].split(os.sep)[-1]) # Re-run this program with elevated permissions to admin
                sys.exit(1)
            # Install
            # Note: Tkinter is not available through pip nor easy_install, we assume it was packaged with Python
            print(s.check_output('pip install setuptools'))
        except:
            print(Fore.RED + "Failed to install. Please run: pip download pillow & pip install pillow")
            input('Press ENTER to exit')
            sys.exit(1)
    elif sys.platform == 'linux2':
        print(s.Popen('sudo apt-get update'.split(' '), stdout = s.PIPE, stderr = s.STDOUT).communicate()[0])
        print(s.Popen('sudo apt-get -y install python-tk'.split(' '), stdout = s.PIPE, stderr = s.STDOUT).communicate()[0])
    else:
        print(Fore.RED + "Could not automatically install required modules")
        input('Press ENTER to exit')
        quit()

    try:
        import tkinter as tk
        import subprocess
    except:
        input('Could not install Tkinter. Please do this manually by running: sudo apt-get install python-tk')
        quit()

import tkinter.messagebox
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Framework')) # Move to Framework directory, so all modules can be seen
# install_missing_modules(req_file_path=True)
from Framework.Utilities import ConfigModule, FileUtilities, self_updater # Modifing settings files
from node_cli import Login, disconnect_from_server, get_team_names, get_project_names, check_server_online, processing_test_case # Controlling node status and logging in

# Find node id file
if sys.platform  == 'win32':
    node_id_filename = os.path.join(os.getenv('USERPROFILE'), 'Desktop', 'node_id.conf')
else:
    node_id_filename = os.path.join(os.getenv('HOME'), 'Desktop', 'node_id.conf')

# Set title with version
version_path = os.path.join(os.getcwd(), 'Version.txt')
try: local_version = ConfigModule.get_config_value('ZeuZ Python Version', 'version', version_path)
except: local_version = ''
gui_title = 'ZeuZ Node v%s' % str(local_version)

help_text = "\
Zeuz Node Help\n\n\
Description:\n\
This is a graphical front-end for the node_gui.py script. It provides an interface to configure the settings, running the Zeuz Node, and displaying the output. Either this, or the node_gui.py script can be run with the same effect.\n\n\
Show Advance Settings:\tDisplay more settings including server, port, screenshot, etc\n\
Save Settings:\tSave all settings (whether displayed or not)\n\
Quit: Exit immediately - Any running automation will be stopped\n\
Online: Start the Zeuz_Node.py script, login to the Zeuz server, and wait for a Test Case to be deployed\n\
Scroll Lock Checkbox: Enable this checkbox (above the log window) to always show the last log lines. Uncheck to disable this which allows you to scroll the window while new log lines are coming in\n\
Refresh: Gets the list of Teams the current user has access to\n\n\
"

class Application(tk.Frame):
    show_adv_settings = False # Toggles settings button
    run = False # Toggles online button
    widgets = {} # Holds the text entry widget handles under the line name
    settings_modified = [] # Holds the last seen settings, so we can check if we need to auto-save
    settings_saved = int(time.time()) # "Settings updated" timer
    advanced_settings_frames = [] # List of settings sections

    # Widget settings
    scroll_lock = None
    entry_width = 30
    button_width = 15
    node_id_size = 10  # Max length of node ID - must match that specified in CommonUtil.MachineInfo()
    padx = 8
    pady = 8

    colour_tag = 0

    max_log_size = 1000  # Maximum number of lines allowed before we truncate the log
    update_interval = 1  # Time in hours to check for updates. We never check less than this time

    colour_debug = 'blue'  # http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
    colour_passed = 'green4'
    colour_warning = 'orange'
    colour_failed = 'red'
    colour_default = 'black'

    def __init__(self, master=None):
        try:
            # Initialize window
            tk.Frame.__init__(self, master)
            self.pack(fill = 'both', expand = True)  # Need to pack top level, to allow widgets to expand when window is resized
            tk.Grid.columnconfigure(self, 0, weight=1)  # Allows mainframe to expand
            tk.Grid.rowconfigure(self, 0, weight=1)  # Allows mainframe to expand

            # Populate window
            self.createFrames()
            self.createButtons()
            self.createWidgets()

            # Populate modified settings checker, so we know if changes were made
            self.save_all(save=False)

            # If go online at start is set, go online
            try:
                if 'go_online_at_start' in self.widgets['Advanced Options']['widget'] and self.widgets['Advanced Options']['widget']['go_online_at_start']['check'].get(): self.read_mod(at_start=True)
            except: pass # Exception Advanced Options section doesn't exist (old settings format)

            self.start_up_display() # Determine if this is the first run, and display widgets accordingly
            # self.read_log() # Start the log reader timer

            # Check for updates, if enabled
            try:
                if 'check_for_updates' in self.widgets['Advanced Options']['widget'] and self.widgets['Advanced Options']['widget']['check_for_updates']['check'].get(): self.check_for_updates(check = True) # Check for updates
            except: pass # Exception Advanced Options section doesn't exist (old settings format)

            # Maximize or Minimize, depending on settings.conf
            if 'Advanced Options' in self.advanced_settings_frames: # Make sure this section is in the config file
                if 'maximize_at_start' in self.widgets['Advanced Options']['widget'] and self.widgets['Advanced Options']['widget']['maximize_at_start']['check'].get():
                    sw = r.winfo_screenwidth()
                    sh = r.winfo_screenheight()
                    r.geometry("%dx%d+%d+%d" % (sw, sh, 0, 0)) # Set window to size of screen
                elif 'minimize_at_start' in self.widgets['Advanced Options']['widget'] and self.widgets['Advanced Options']['widget']['minimize_at_start']['check'].get():
                    r.iconify()

        except Exception as e:
            print("Exception in init {}".format(e))
            tkinter.messagebox.showerror('Error 01', 'Exception caught: %s' % e)

    def createFrames(self):
        try:
            # Mainframe contains everything
            self.mainframe = tk.Frame(self)
            self.mainframe.grid(sticky = 'snew', padx=self.padx, pady=self.pady)
            tk.Grid.columnconfigure(self.mainframe, 1, weight=1) # Allows to expand
            tk.Grid.rowconfigure(self.mainframe, 0, weight=1) # Allows to expand

            # Contains settings and buttons
            self.leftframe = tk.Frame(self.mainframe)
            self.leftframe.grid(row = 0, column = 0, sticky = 'snew')

            # Top Left buttons
            self.topframe = tk.Frame(self.leftframe)
            self.topframe.grid(sticky = 'w')

            # Read the settings data, and dynamically add widgets to window
            self.settings_frame = tk.Frame(self.leftframe)
            self.settings_frame.grid(sticky = 'w')
        except Exception as e:
            print("Exception in createframes {}".format(e))
            tkinter.messagebox.showerror('Error 02', 'Exception caught: %s' % e)


    def createButtons(self):
        try:
            # Connect/Disconnect button
            # self.startButton = tk.Button(self.topframe, text='Connect', fg = self.colour_passed, width = self.button_width, command=self.read_mod)
            # self.startButton.grid(row = 0, column = 0, columnspan = 2, pady=(0, self.pady))

            # All buttons
            self.help_button = tk.Button(self.topframe, text = 'Help', width = self.button_width, command = self.show_help)
            self.help_button.grid(row = 1, column = 1, sticky = 'w')

            self.quitButton = tk.Button(self.topframe, text='Quit', width = self.button_width, command=teardown)
            self.quitButton.grid(row = 1, column = 0)

            self.settings_selection = tk.StringVar(self)
            self.settings_selection.set('Authentication')
            self.advanced_settings_frames.append('Authentication') # Need a default value, so we can create the menu
            self.settings_menu = tk.OptionMenu(self.topframe, self.settings_selection, *self.advanced_settings_frames) # Create drop down
            self.settings_menu.grid(row = 2, column = 0)
            self.settings_selection.trace('w', self.show_settings) # Bind function to this drop down menu

            # self.save_button = tk.Button(self.topframe, text='Save', width=self.button_width, command=lambda: self.save_all(True))
            # self.save_button.grid(row = 2, column = 1)

            # Node ID
            tk.Label(self.topframe, text = 'Node ID', fg="blue")\
                .grid(row = 3, column = 0, pady=self.pady, sticky = 'w')
            self.node_id = tk.Entry(self.topframe, validate = "key", validatecommand = (self.register(self.onValidate), '%d', '%S')) # See onValidate() for more info
            self.node_id.grid(row = 3, column = 1, sticky = 'w')
            self.read_node_id(self.node_id)

        except Exception as e:
            print("Exception in createbuttons {}".format(e))
            tkinter.messagebox.showerror('Error 03', 'Exception caught: %s' % e)

    def createWidgets(self):
        # Sub-frames are created for each section, which allows us to show/hide tem dynamically
        # Widget types of determined on the fly (Entry, drop down, checkbox, etc)

        try:
            self.settings_menu['menu'].delete(0, 'end') # Clear initial settings menu item, so we can populate it properly
            row = 0
            sections = ConfigModule.get_all_sections() # All sections in the config file
            if sections:
                for section in sections:  # For each section
                    self.widgets[section] = {}  # Initialize dictionary
                    self.widgets[section]['widget'] = {}  # Initialize widget dictionary
                    self.widgets[section]['frame'] = tk.Frame(self.settings_frame) # Create frame
                    self.advanced_settings_frames.append(section)  # Store all section names, so we know which to display when we click the show advanced settings button
                    self.settings_menu['menu'].add_command(label = section, command=tk._setit(self.settings_selection, section))  # Add the team to the drop down menu
                    tk.Label(self.widgets[section]['frame'], text = section, fg="blue").grid(row = row, column = 0, pady = 10, sticky = 'w', columnspan = 2)  # Create Section label
                    row += 1
                    options = ConfigModule.get_all_option(section) # Read all options (keys) for this section
                    if options:
                        for option in options: # For each option
                            if option == 'server_port':
                                continue
                            self.widgets[section]['widget'][option] = {} # Initilize dictionary
                            value = ConfigModule.get_config_value(section, option) # Read value from file
                            tk.Label(self.widgets[section]['frame'], text = option.replace('_', ' ').capitalize()).grid(row = row, column = 0, sticky = 'w') # Create Option label

                            # Create the widget for this Option/Key, depending on the type
                            if option == 'password': # Add asterisk to hide password

                                if value != '':
                                    value = self.password(False, 'zeuz', value) # Decrypt password read from settings file
                                self.widgets['Authentication']['widget'][option]['widget'] = tk.Entry(self.widgets[section]['frame'], show = '*', width = self.entry_width) # Password textbox which hides the password with asterisks
                                self.widgets['Authentication']['widget'][option]['widget'].insert('end', value) # Enter decrypted password

                            # # Set these as drop down menus
                            # elif option in ('team', 'project'):
                            #     # Configure drop down menu
                            #     self.widgets['Authentication']['widget'][option]['dropdown'] = tk.StringVar(self) # Initialize drop down variable
                            #     self.widgets['Authentication']['widget'][option]['dropdown'].set('') # Need to initialize this, so OptionMenu will work
                            #     self.widgets['Authentication']['widget'][option]['choices'] = [] # Initizlize list of available menu items
                            #     self.widgets['Authentication']['widget'][option]['choices'].append(value) # Need to initialize this, so OptionMenu will work
                            #     self.widgets['Authentication']['widget'][option]['widget'] = tk.OptionMenu(self.widgets[section]['frame'], self.widgets['Authentication']['widget'][option]['dropdown'], *self.widgets['Authentication']['widget'][option]['choices']) # Create drop down
                            #     if option == 'team': self.get_teams(True) # Get list of teams from the server, populate the list
                            #     self.widgets['Authentication']['widget'][option]['dropdown'].set(value) # Set menu to value in config file

                            # True/False checkbox
                            elif value.lower() in ('true', 'false'):
                                self.widgets[section]['widget'][option]['check'] = tk.IntVar() # Initilize checkbox variable
                                self.widgets[section]['widget'][option]['widget'] = tk.Checkbutton(self.widgets[section]['frame'], variable = self.widgets[section]['widget'][option]['check']) # Checkbox widget
                                if value.lower() == 'true': self.widgets[section]['widget'][option]['check'].set(1) # Enable checkbox if "True"
                                else: self.widgets[section]['widget'][option]['check'].set(0) # Disable checkbox if "False"

                            # Anything else is a text Entry widget
                            else:
                                self.widgets[section]['widget'][option]['widget'] = tk.Entry(self.widgets[section]['frame'], width = self.entry_width) # Create Entry textbox widget
                                self.widgets[section]['widget'][option]['widget'].insert('end', value)

                            # Pack widgets
                            self.widgets[section]['widget'][option]['widget'].grid(row = row, column=1, sticky = 'w')
                            row += 1

                    if section == "Authentication":
                        # Connect/Disconnect button
                        self.startButton = tk.Button(self.widgets[section]['frame'], text='Connect', fg=self.colour_passed,
                                                     width=self.button_width, command=self.read_mod)
                        self.startButton.grid(row=row+1, column=0, columnspan=2, padx=50, pady=10)

            # # Put a trace on the team field, so we can automatically change the project when the team is changed
            # self.widgets['Authentication']['widget']['team']['dropdown'].trace('w', self.switch_teams) # Bind function to this drop down menu
            # if self.widgets['Authentication']['widget']['team']['dropdown'].get() != '':
            #     self.get_projects(self.widgets['Authentication']['widget']['team']['dropdown'].get()) # Get list of projects from the server for the curent team, populate the list
        except Exception as e:
            print("Exception in createwidgets {}".format(e))
            tkinter.messagebox.showerror('Error 05', 'Exception caught: %s' % e)

    def check_for_updates(self, check = False):
        # Check if there's a new update for zeuz node - this is triggered upon startup or periodically via tk.after()
        # Always check for updates, but depending on user's settings, either update automatically or inform user of update

        try:
            # Just check for updates, and schedule testing to see if updates checking is complete
            if check:
                print('Checking last update time')
                # Read from temp config last time we checked for updates. If over maximum time, check again
                temp_ini_file = os.path.join(os.path.join(FileUtilities.get_home_folder(), os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Advanced Options', '_file')))))
                try:
                    last_update = ConfigModule.get_config_value('sectionOne', 'last_update', temp_ini_file)
                    update_interval = self.update_interval * 3600 # Convert interval into seconds for easy comparison
                except: # If temp ini doesn't exist, or last_update line is missing or has a blank value, set defaults
                    last_update = ''
                    update_interval = 0

                if last_update == '' or (float(last_update) + update_interval) < time.time(): # If we have reached the allowed time to check for updates or nothing was previously set. Assume this is the first time, check for updates.
                    print('Checking for software updates')
                    ConfigModule.add_config_value('sectionOne', 'last_update', str(time.time()), temp_ini_file) # Record current time as update time

                    _thread.start_new_thread(self_updater.check_for_updates, ()) # Check for updates in a separate thread
                    self.after(15000, self.check_for_updates) # Tests if check for updates is complete
                    self.after(self.update_interval * 3600 * 1000, lambda: self.check_for_updates(True)) # Reschedule next check for updates (calculates from hours to ms)

            # root.after() brings us here
            else:
                # No update, do nothing, and thus stop checking
                if self_updater.check_complete == 'noupdate':
                    print('No software updates available')
                    pass

                # Update check complete, we have an update, start install
                elif self_updater.check_complete[0:6] == 'update':
                    # Print update notes
                    try:
                        print("\nUpdate notes:")
                        for note in str(self_updater.check_complete[7:]).split(';'): print(note)
                        print('')
                    except: pass

                    # Read update settings
                    try:
                        if 'auto-update' in self.widgets['Advanced Options']['widget'] and self.widgets['Advanced Options']['widget']['auto-update']['check'].get(): auto_update = True
                        else: auto_update = False
                    except: auto_update = False

                    # If auto-update is true, then perform update
                    if auto_update:
                        print('*** A new update is available. Automatically installing.')
                        _thread.start_new_thread(self_updater.main, (os.path.dirname(os.path.realpath(__file__)).replace(os.sep + 'Framework', ''),))
                        self.after(10000, self.check_for_updates) # Checks if install is complete
                    # If auto-update is false, notify user via dialogue that there's a new update available, and ask if they want to download and install it
                    else:
                        # if tkinter.messagebox.askyesno('Update', 'A Zeuz Node update is available. Do you want to download and install it?'):
                        #     _thread.start_new_thread(self_updater.main, (os.path.dirname(os.path.realpath(__file__)).replace(os.sep + 'Framework', ''),))
                        #     self.after(10000, self.check_for_updates) # Checks if install is complete
                        # else:
                        #     pass # Do nothing if the user doens't want to update. We'll check again tomorrow
                        self.updateDialog()

                # Still installing, check again later
                elif self_updater.check_complete == 'installing':
                        self.after(10000, self.check_for_updates) # Checks if install is complete

                # Update installed. Now we have to restart Zeuz Node for changes to take effect
                elif self_updater.check_complete == 'done':
                    # Read update settings
                    try:
                        if 'auto-restart' in self.widgets['Advanced Options']['widget'] and self.widgets['Advanced Options']['widget']['auto-restart']['check'].get(): auto_restart = True
                        else: auto_restart = False
                    except: auto_update = False

                    # If auto-reboot is true, then reboot the next time zeuz node is not in the middle of a run
                    if auto_restart:
                        print('*** Update installed. Automatically restarting. ***')
                        time.sleep(1) # Wait a bit, so they can see the message
                        self.self_restart()

                    # If auto-reboot is false, then notify user via dialogue that the installation is complete and ask to reboot
                    else:
                        if tkinter.messagebox.askyesno('Update', "New Zeuz Node software was successfully installed. Would you like to restart Zeuz Node (when we're not testing) to start using it?"):
                            self.self_restart()
                        else:
                            pass # Do nothing. User will have to restart manually

                # Some error occurred during updating
                elif 'error' in self_updater.check_complete:
                    tkinter.messagebox.showerror('Update', "An error occurred during update: %s" % self_updater.check_complete)
        except Exception as e:
            print("Exception in CheckUpdates {}".format(e))
            tkinter.messagebox.showerror('Error 06', 'Exception caught: %s' % e)


    def updateDialog(self):
        dialog = MyDialogBox(self)

    def self_restart(self):
        try:
            if processing_test_case: # If we are in the middle of a run, try to restart again later
                self.after(60000, self.self_restart)
            else: # Not running a test case, so it should be safe to restart
                subprocess.Popen('python "%s"' % os.path.realpath(sys.argv[0]).replace(os.sep + 'Framework', ''), shell = True) # Restart zeuz node
                quit() # Exit this process
        except Exception as e:
            print("Exception in selfRestart {}".format(e))
            tkinter.messagebox.showerror('Error 07', 'Exception caught: %s' % e)

    def start_up_display(self):
        # Check if this is the first run (team widget is set to default string), and if so, rearrange, so the server/port is above the user/pass to help user understand what needs to be populated

        try:
            # text_check = self.widgets['Authentication']['widget']['team']['dropdown'].get() # Read team selection
            # if text_check == 'YourTeamNameGoesHere': # If it is the default selection
            #     self.widgets['Server']['frame'].grid(row = 0, column = 0, sticky = 'w') # Show the server/port section
            #     self.continuous_server_check() # Tell program to constantly check for server connection until we connect
            # else: # Show default section
            self.widgets['Authentication']['frame'].grid(row = 0, column = 0, sticky = 'w') # Show authentication section on subsequent runs
        except Exception as e:
            print("Exception in startupdisplay {}".format(e))
            tkinter.messagebox.showerror('Error 08', 'Exception caught: %s' % e)

    def continuous_server_check(self, check = True):
        # Helps the user provide required login information by showing specific fields polling the server until everyting is set
        # Check if server address is set
        try:
            print() # This prevents freezing up on windows for some reason
            if check:
                result = check_server_online()
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
                        pass
                        #root.after(1000, lambda: self.continuous_server_check(False))
                    else: # First run completed, everything is properly set. Clear the team/project, so the user knows to set them
                        self.widgets['Authentication']['widget']['team']['dropdown'].set('')
                        self.widgets['Authentication']['widget']['project']['dropdown'].set('')
                else: # No user/pass, try again
                    root.after(1000, self.continuous_server_check)
        except Exception as e:
            print("Exception in continuous_server_check {}".format(e))
            tkinter.messagebox.showerror('Error 09', 'Exception caught: %s' % e)

    def onValidate(self, ctype, S):
        # Limit text to specified length and characters
        # https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter/4140988#4140988
        # Caveats: Can't copy/paste/w.insert() more than one character at a time

        chars = '0123456789abcdefghijklmnopqrstuvwxyz-_' # Allowed characters for the Node ID

        if int(ctype) == 0: return True # Allow deletions

        if len(self.node_id.get()) < self.node_id_size: # Allow up to this length
            if S in chars: return True # Allow these characters
            else: return False # Invalid character
        else: return False # Invalid length


    def show_help(self):
        ''' Display help information in the log window '''
        help_url = "https://www.zeuz.ai/forums/"
        webbrowser.open(help_url,new=1)
        # print(help_text)


    def show_settings(self, a, b, c):
        ''' Display different settings sections depending on drop down menu selection '''

        try:
            for section in self.advanced_settings_frames: self.widgets[section]['frame'].grid_forget()
            section = self.settings_selection.get()
            self.widgets[section]['frame'].grid(row = 0, column = 0, sticky = 'w')
        except Exception as e:
            print("Exception in show_settings {}".format(e))
            tkinter.messagebox.showerror('Error 17', 'Exception caught: %s' % e)


    def read_mod(self, at_start=False):
        '''
        :param at_start: Indicates whether this function is being called automatically when the gui boots up
        :return:
        '''
        # Toggle online/offline button - Puts node online or takes it offline
        try:
            if self.run:
                self.run = False
                self.startButton.configure(text='Connect', fg=self.colour_passed)
                disconnect_from_server() # Tell Zeuz_Node.py to stop
                print("Disconnecting from server...")
            else:
                # Save settings and connect
                if not at_start:
                    self.save_all(save=True)

                self.run = True
                self.startButton.configure(text='Disconnect', fg=self.colour_failed)
                _thread.start_new_thread(Login,()) # Execute Zeuz_Node.py
                if self.node_id.get() == '': self.after(5000, lambda: self.read_node_id(self.node_id)) # If no node id was read or specified, wait a few seconds for zeuz_node.py to populate the node id file, and read it
        except Exception as e:
            print("Exception in read_mod {}".format(e))
            tkinter.messagebox.showerror('Error 11', 'Exception caught: %s' % e)


    def password(self, encrypt, key, pw):
        ''' Encrypt, decrypt password and encode in plaintext '''
        # This is just an obfuscation technique, so the password is not immediately seen by users
        # Zeuz_Node.py has a similar function that will need to be updated if this is changed

        try:
            result = pass_encode(key,pw)

            return result
        except Exception as e:
            print("Exception in password {}".format(e))
            tkinter.messagebox.showerror('Error', 'Error decrypting password. Enter a new password {}'.format(e))
            return ''

    def read_node_id(self, w):
        # This is a separate file on the desktop
        try:
            if os.path.exists(node_id_filename):
                node_id = ConfigModule.get_config_value('UniqueID', 'id', node_id_filename).strip()
                for c in node_id: w.insert('end', c) # We have to write characters one at a time due to how onValidate() works
        except Exception as e:
            print("Exception in read_node_id {}".format(e))
            tkinter.messagebox.showerror('Error 13', 'Exception caught: %s' % e)

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
                        if option == 'password':
                            value = self.password(True, 'zeuz', value) # Encrypt password

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
            if save:  # Yes, explicit save call, so tell the user
                # self.get_teams()
                print("Settings saved.")

        except Exception as e:
            print("Exception in save settings {}".format(e))
            traceback.print_exc()
            print(Fore.RED + "Failed to save settings. Trying again in 10 seconds...")

    def switch_teams(self, a, b, c):
        # When user changes the team, pull the list of projects for that team
        try:
            self.widgets['Authentication']['widget']['project']['dropdown'].set('') # Clear Project menu
            self.get_projects(self.widgets['Authentication']['widget']['team']['dropdown'].get()) # Update available options in project menu
        except Exception as e:
            print("Exception in switch_teams {}".format(e))
            tkinter.messagebox.showerror('Error 14', 'Exception caught: %s' % e)

    def get_teams(self, noerror = False):
        # Populate drop down with teams user has access to
        try:
            self.widgets['Authentication']['widget']['team']['choices'] = get_team_names(noerror)  # Get list of teams from server
            self.widgets['Authentication']['widget']['team']['widget']['menu'].delete(0, 'end')  # Clear drop down menu
            for team in self.widgets['Authentication']['widget']['team']['choices']:  # For each new team
                self.widgets['Authentication']['widget']['team']['widget']['menu'].add_command(label = team, command=tk._setit(self.widgets['Authentication']['widget']['team']['dropdown'], team)) # Add the team to the drop down menu
            if self.widgets['Authentication']['widget']['team']['choices'] == []:  # If nothing was returned
                if noerror == False: tkinter.messagebox.showerror('Error', 'No teams could be found. Server, port, username, or password may be wrong') # Display an error
                return False
            return True
        except Exception as e:
            print("Exception in get_teams {}".format(e))
            tkinter.messagebox.showerror('Error 15', 'Exception caught: %s' % e)
            return False

    def get_projects(self, team):
        # Populate drop down with projects user has access to, for a given team
        try:
            self.widgets['Authentication']['widget']['project']['choices'] = get_project_names(team) # Get list of projects for the selected team
            self.widgets['Authentication']['widget']['project']['widget']['menu'].delete(0, 'end') # Clear drop down menu
            for project in self.widgets['Authentication']['widget']['project']['choices']: # For each new project
                self.widgets['Authentication']['widget']['project']['widget']['menu'].add_command(label = project, command=tk._setit(self.widgets['Authentication']['widget']['project']['dropdown'], project)) # Add the project to the drop down menu
        except Exception as e:
            print("Exception in get_projects {}".format(e))
            tkinter.messagebox.showerror('Error 16', 'Exception caught: %s' % e)

    def rClicker(self, e):
        ''' right click context menu for all Tk Entry and Text widgets '''

        try:
            # Bind events to menu items
            def rClick_Copy(e, apnd=0): e.widget.event_generate('<Control-c>')
            def rClick_Cut(e): e.widget.event_generate('<Control-x>')
            def rClick_Paste(e): e.widget.event_generate('<Control-v>')

            # Define menu items and commands
            e.widget.focus()
            nclst=[
                (' Cut', lambda e=e: rClick_Cut(e)),
                (' Copy', lambda e=e: rClick_Copy(e)),
                (' Paste', lambda e=e: rClick_Paste(e)),
            ]

            # Create menu, and add menu items
            rmenu = tk.Menu(None, tearoff=0, takefocus=0)
            for (txt, cmd) in nclst: rmenu.add_command(label=txt, command=cmd)
            rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")
        except Exception as e:
            print("Exception in rClicker {}".format(e))
            pass


def teardown():
    disconnect_from_server()
    quit()


if __name__ == '__main__':
    # Root window setup
    r = tk.Tk()  # Create instance of Tk for bind
    r.bind("<Escape>", lambda e: teardown)  # Bind escape to exit
    r.protocol("WM_DELETE_WINDOW", teardown)  # Catch any types of exits and teardown properly

    if sys.platform == 'win32':
        icon_img = 'zeuz.gif'
    else:
        icon_img = 'zeuz.png'

    if os.path.exists(icon_img):
        try:
            icon = tk.PhotoImage(file = icon_img)  # Import image into format that next line can understand
            r.call('wm', 'iconphoto', r._w, icon)  # Put icon on titlebar
        except:
            pass  # Not a big deal if this fails

    # Main window setup
    root = Application() # Create GUI instance
    root.master.title(gui_title) # Set title

    # Execute GUI
    root.mainloop()
