#coding: UTF8
"""
System File Locations
Retrieves common system path names on Windows XP/Vista
Depends only on ctypes, and retrieves path locations in Unicode
"""

import ctypes
from ctypes import windll, wintypes
import win32com.client as WC
import tempfile

class FoldersConstants():
    """
    Define constants here to avoid dependency on shellcon.
    Put it in a class to avoid polluting namespace
    """

    DESKTOP = 0
    PROGRAMS = 2
    PERSONAL = 5
    FAVORITES = 6
    STARTUP = 7
    RECENT = 8
    SENDTO = 9
    BITBUCKET = 10
    STARTMENU = 11
    MYDOCUMENTS = 12
    MYMUSIC = 13
    MYVIDEO = 14
    DESKTOPDIRECTORY = 16
    DRIVES = 17
    NETWORK = 18
    NETHOOD = 19
    FONTS = 20
    TEMPLATES = 21
    COMMONSTARTMENU = 22
    COMMONPROGRAMS = 23
    COMMONSTARTUP = 24
    COMMONDESKTOPDIRECTORY = 25
    APPDATA = 26
    PRINTHOOD = 27
    LOCAL_APPDATA = 28
    ALTSTARTUP = 29
    COMMONALTSTARTUP = 30
    COMMONFAVORITES = 31
    INTERNETCACHE = 32
    COOKIES = 33
    HISTORY = 34
    COMMONAPPDATA = 35
    WINDOWS = 36
    SYSTEM = 37
    PROGRAM_FILES = 38
    MYPICTURES = 39
    PROFILE = 40
    SYSTEMX86 = 41
    PROGRAMFILESX86 = 42
    PROGRAM_FILES_COMMON = 43
    PROGRAMFILESCOMMONX86 = 44
    COMMONTEMPLATES = 45
    COMMONDOCUMENTS = 46
    COMMONADMINTOOLS = 47
    ADMINTOOLS  = 48
    CONNECTIONS = 49
    COMMONMUSIC = 53
    COMMONPICTURES = 54
    COMMONVIDEO = 55
    RESOURCES = 56
    RESOURCESLOCALIZED = 57
    COMMONOEMLINKS = 58
    CDBURNAREA = 59
    # 60 unused
    COMPUTERSNEARME = 61


class WinPathsException(Exception):
    pass


def _err_unless_zero(result):
    if result == 0:
        return result
    else:
        raise WinPathsException("Failed to retrieve windows path: %s" % result)
    
_SHGetFolderPath = windll.shell32.SHGetFolderPathW
_SHGetFolderPath.argtypes = [wintypes.HWND,
                            ctypes.c_int,
                            wintypes.HANDLE,
                            wintypes.DWORD, wintypes.LPCWSTR]
_SHGetFolderPath.restype = _err_unless_zero

def _get_path_buf(csidl):
    path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
    result = _SHGetFolderPath(0, csidl, 0, 0, path_buf)
    return path_buf.value

def Get_local_Appdata_Path():
    return _get_path_buf(FoldersConstants.LOCAL_APPDATA)

def Get_Appdata_Path():
    return _get_path_buf(FoldersConstants.APPDATA)

def Get_Desktop_Path():
    return _get_path_buf(FoldersConstants.DESKTOP)

def Get_Programs_Path():
    """current user -> Start menu -> Programs"""
    return _get_path_buf(FoldersConstants.PROGRAMS)

def Get_Admin_Tools_Path():
    """current user -> Start menu -> Programs -> Admin tools"""
    return _get_path_buf(FoldersConstants.ADMINTOOLS)

def Get_Common_Admin_Tools_Path():
    """all users -> Start menu -> Programs -> Admin tools"""
    return _get_path_buf(FoldersConstants.COMMON_ADMINTOOLS)

def Get_Common_Appdata_Path():
    return _get_path_buf(FoldersConstants.COMMONAPPDATA)

def Get_Common_Documents_Path():
    return _get_path_buf(FoldersConstants.COMMONDOCUMENTS)

def Get_Cookies_Path():
    return _get_path_buf(FoldersConstants.COOKIES)

def Get_History_Path():
    return _get_path_buf(FoldersConstants.HISTORY)

def Get_Internet_Cache_Path():
    return _get_path_buf(FoldersConstants.INTERNET_CACHE)

def Get_My_Pictures_Path():
    """Get the user's My Pictures folder"""
    return _get_path_buf(FoldersConstants.MYPICTURES)

def Get_My_Videos_Path():
    """Get the user's My Pictures folder"""
    return _get_path_buf(FoldersConstants.MYVIDEO)

def Get_My_Documents_Path():
    """Get the user's My Pictures folder"""
    objShell = WC.Dispatch("WScript.Shell")
    DocPath = objShell.SpecialFolders("MyDocuments")
    return DocPath

def Get_Personal_Path():
    """AKA 'My Documents'"""
    return _get_path_buf(FoldersConstants.PERSONAL)

get_my_documents = Get_Personal_Path

def Get_Program_Files_Path():
    return _get_path_buf(FoldersConstants.PROGRAM_FILES)

def Get_Program_Files_Common_Path():
    return _get_path_buf(FoldersConstants.PROGRAM_FILES_COMMON)

def Get_System_Path():
    """Use with care and discretion"""
    return _get_path_buf(FoldersConstants.SYSTEM)

def Get_Windows_Path():
    """Use with care and discretion"""
    return _get_path_buf(FoldersConstants.WINDOWS)

def Get_Favorites_Path():
    return _get_path_buf(FoldersConstants.FAVORITES)

def Get_Startup_Path():
    """current user -> start menu -> programs -> startup"""
    return _get_path_buf(FoldersConstants.STARTUP)

def Get_Recent_Path():
    return _get_path_buf(FoldersConstants.RECENT)

def Get_Profile_Path():
    return _get_path_buf(FoldersConstants.PROFILE)

def Get_MyMusic_Path():
    return _get_path_buf(FoldersConstants.MYMUSIC)

def Get_CommonMusic_Path():
    return _get_path_buf(FoldersConstants.COMMONMUSIC)

def Get_CommonPictures_Path():
    return _get_path_buf(FoldersConstants.COMMONPICTURES)

def Get_CommonVideos_Path():
    return _get_path_buf(FoldersConstants.COMMONVIDEO)

def Get_TempFolder_Path():
    return tempfile.gettempdir()


def main():
    #obj = WinCommonFoldersPath()
    #print Get_local_Appdata_Path()
#    print Get_My_Pictures_Path()
#    print Get_My_Videos_Path()
    #print Get_Personal_Path()
    #print Get_MyMusic_Path()
    pass

if __name__ == "__main__": 
    main()
