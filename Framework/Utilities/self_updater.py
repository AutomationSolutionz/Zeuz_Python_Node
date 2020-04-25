#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

'''
    :Function: Automatically updates Zeuz Node software
    :Author: Lucas Donkers
    :Date: Nov 2017
    
    check_for_updates() should be called by Zeuz_Node.py to check for a new version
    main(Install_Location) should be called by Zeuz_Node.py, which will download and install new software
'''

# Import modules
import sys, os, os.path, shutil, requests, urllib3, zipfile, glob, subprocess
urllib3.disable_warnings() # Hide warnings from requests module

# Import local modules
from . import ConfigModule

# Global variables
version_url = 'https://raw.githubusercontent.com/AutomationSolutionz/Zeuz_Python_Node/master/Framework/Version.txt' # Version of newest software
version_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Version.txt') # Version of installed software
zeuz_node_package = 'https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/master.zip' # Location of newest software
skip = ['Framework' + os.sep + 'settings.conf',
        'Projects',
        'Drivers',
        'iosSimulator'
        ] # Any files or directories we don't want to delete not longer existing files from
check_complete = 'no' # 'no', 'yes', 'error'. Used by Zeuz Node to check if install is complete

def copytree(src_dir, dst_dir, skip = []):
    ''' Copy entire directory, overwrite exsting files '''
    # shutil.copytree only works if dst directory doesn't exist. Won't work for us, so we do it ourselves
    
    try:
        for root, subdirs, files in os.walk(src_dir):
            # Copy directories
            for subdir in subdirs:
                try:
                    src = os.path.join(root, subdir) # Source directory
                    dst = src.replace(src_dir, dst_dir) # Create destination directory from source
                    if not os.path.exists(dst):
                        die = False
                        for f in skip:
                            if f in dst: 
                                die = True
                                break
                        if die: continue

                        os.mkdir(dst)
                        #print "NEW DIR:", dst
                except:
                    print("ERR1", dst)

            # Copy files
            for filename in files:
                try:
                    src = os.path.join(root, filename)
                    dst = src.replace(src_dir, dst_dir)
                    
                    die = False
                    for f in skip:
                        if f in dst: 
                            die = True
                            break
                    if die: continue

                    shutil.copy(src, dst)
                    #print "NEW File:", dst
                except Exception as e:
                    print("ERR3: ", e, src, dst)
    except Exception as e:
        print("Err", e)

def remove_deleted(src_dir, dst_dir, skip = []):
    ''' Delete files and directories from dst, that do not exist in src '''

    try:
        # Create full paths for skip items
        for i in range(len(skip)):
            skip[i] = os.path.join(dst_dir, skip[i])
            
        for root, subdirs, files in os.walk(dst_dir):
            # Do not remove if in skip list
            if root in skip: continue
            
            # Delete directories
            for subdir in subdirs:
                try:
                    dst = os.path.join(root, subdir)
                    src = dst.replace(dst_dir, src_dir)
                    if not os.path.exists(src) and src not in skip:
                        die = False
                        for f in skip:
                            if f in dst: 
                                die = True
                                break
                        if die: continue

                        shutil.rmtree(dst)
                        #print "DEL DIR:", dst
                except:
                    print("ERR", dst)

            # Delete files
            for filename in files:
                try:
                    dst = os.path.join(root, filename)
                    src = dst.replace(dst_dir, src_dir)
                    if not os.path.exists(src) and src not in skip:
                        die = False
                        for f in skip:
                            if f in dst: 
                                die = True
                                break
                        if die: continue
                        
                        if os.path.exists(dst): os.unlink(dst) # Check in case file was deleted by above
                        #print "DEL File:", dst
                except:
                    print("ERR2: ", dst)
    except Exception as e:
        print("Err", e)
        
def Download_File(url, filename = ''):
    ''' Download a file with progress update in percentage '''
    # If no filename provided, we will try to get it from the url
    
    chunk_size = 4096 # Size in bytes of data to download at a time
    try:
        if filename == '': filename = url.split('/')[-1] # No filename given. Try to get the filename automatically
        
        r = requests.get(url, stream=True, timeout=2*60) # Create object to get file
        with open(filename, 'wb') as f: # Open file on disk
            for data in r.iter_content(chunk_size): # Download and write contents to disk
                if data: f.write(data) # Write data to disk

        if os.sep not in filename: filename = os.path.join(os.getcwd(), filename)
        return filename
    except Exception as e:
        print("Error downloading: %s" % e)
        return False

def unzip(zipFilePath, destDir):
    ''' Unzip archived files '''
    
    try:
        zfile = zipfile.ZipFile(zipFilePath)
        if destDir and not os.path.exists(destDir): os.mkdir(destDir) 
        for name in zfile.namelist():
            (dirName, fileName) = os.path.split(name)
            if fileName == '': # Create sub-directory
                newDir = os.path.join(destDir, dirName)
                if not os.path.exists(newDir): os.mkdir(newDir)
            else: # Create file
                with open(os.path.join(destDir, name), 'wb') as fd: fd.write(zfile.read(name))
        zfile.close()
        return True
    except Exception as e: 
        print("Err", e)
        return False


def check_for_updates():
    ''' Check if the installed version differs from the newest '''

    global check_complete
    try:
        check_complete = 'check'
        section = 'ZeuZ Python Version' # Must match what's in the version file
        key = 'version' # Must match what's in the version file
        section_key = 'Release Note' # Must match the key in the version file
        note_key = 'Note' # Must match the key in the version file
        if sys.platform == 'win32': version_tmp = os.path.join(os.getenv('TMP'), 'version.txt')
        else: version_tmp = '/tmp/version.txt'
        
        local_version = ConfigModule.get_config_value(section, key, version_path)
        remote_version = ConfigModule.get_config_value(section, key, Download_File(version_url, version_tmp))
        
        # We have an update available
        if local_version != remote_version and remote_version != '' and local_version != '':
            try: note = ConfigModule.get_config_value(section_key, note_key, version_tmp) # Get update notes
            except: note = ''
            check_complete = 'update:' + note # Sends command along with note to zeuz node

        # Clean up no longer needed file
        if os.path.exists(version_tmp): os.unlink(version_tmp)
                
        # No update
        else: check_complete = 'noupdate'
    except:
        print("Error")
        return False

def download_new_version(zeuz_node_package):
    ''' Download the newest archive of the software '''

    # Directory where installer files will be kept
    if sys.platform == 'win32': tmp = os.getenv('TEMP')
    else: tmp = '/tmp'
    installer_location = os.path.join(tmp, 'zeuz_node') # Temp directory (can be anything)
    if not os.path.exists(installer_location): os.mkdir(installer_location) # Create temp directory
    zipname = os.path.join(installer_location, 'zeuz_node.zip') # Filename of temp archive that we'll save to
    
    # Download and unzip
    if Download_File(zeuz_node_package, zipname): # Download to temp directory
        if unzip(zipname, installer_location): # Unzip to temp directory
            for f in glob.glob(os.path.join(installer_location, '*')): # Find the unzip directory
                if os.path.isdir(f): 
                    return f # This is the directory containing the new software
    # Bitter failure
    return False
            
            
def main(dst_dir):
    ''' Perform update '''
    # dst_dir: The location that Zeuz Node is installed to
    # Assumes user has already verified there's a new software release
    # We communicate with Zeuz Node via variable "check_complete"
    
    global skip, check_complete
    try:
        check_complete = 'installing'
        src_dir = download_new_version(zeuz_node_package) # Download and unpack the new software
        if src_dir: # If we downloaded successfully
            copytree(src_dir, dst_dir, skip) # Copy it to the install location
            remove_deleted(src_dir, dst_dir, skip) # Remove any extra files that were removed from the new software version
            if os.path.exists(src_dir): shutil.rmtree(src_dir) # Remove downloaded software from temp location
            path_of_requirements_file =os.path.join( dst_dir, 'requirements.txt')
            subprocess.run('pip install -r {}'.format(path_of_requirements_file),shell=True)
            check_complete = 'done'
        else: check_complete = 'error'
    except:
        check_complete = 'error'

