'''
Created on Jun 8, 2012

@author: administrator
'''
#coding: UTF8
"""
System File Locations
Retrieves common system path names on MAC
"""
import sys
#sys.path.append("..")

try:
    from Carbon import Folder, Folders
except:
    pass

def Get_Appdata_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
        Folders.kApplicationSupportFolderType, False)
    docs = folderref.as_pathname()
    return docs


def Get_Desktop_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kDesktopFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_Common_Documents_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_My_Documents_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs
    

def Get_Current_User_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kCurrentUserFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_My_Pictures_Path():
    """Get the user's My Pictures folder"""
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kPictureDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_CommonPictures_Path():
    #return _get_path_buf(FoldersConstants.COMMONPICTURES)
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kPictureDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_My_Videos_Path():
    """Get the user's My Pictures folder"""
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kMovieDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_CommonVideos_Path():
    #return _get_path_buf(FoldersConstants.COMMONVIDEO)
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kMovieDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_MyMusic_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kMusicDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

def Get_CommonMusic_Path():
    folderref = Folder.FSFindFolder(Folders.kUserDomain,
    Folders.kMusicDocumentsFolderType, False)
    docs = folderref.as_pathname()
    return docs

    

def main():
    #obj = WinCommonFoldersPath()
    #print Get_local_Appdata_Path()
#    print Get_My_Pictures_Path()
#    print Get_My_Videos_Path()
    #print Get_Personal_Path()
    print "Mac CommonFolderPaths"

if __name__ == "__main__": 
    main()
