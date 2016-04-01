
#coding: UTF8
import os
import md5
import hashlib
import subprocess
import codecs






def md5(filename):
    '''
    Description:
        This Module can give you MD5 of any given file.  You will need to send the full path of the file
                  
                        
    Parameter Description:
        - filename : full path with file name and extension 
                
    Example: 
        - md5 (C:\MD5\Output.txt)
            
    ======= End of Instruction: =========
    
    '''
    
    try:
        m = hashlib.md5()
        fd = open(filename, "rb")
        #content = fd.readlines()
        #fd.close()
        #for eachline in content:
        while True:
            data = fd.read(8192)
            if not data:
                break
            m.update(data)
        fd.close()
        return m.hexdigest()
    except Exception,e:
        print "Exception: ",e
        print "unable to open the file in read mode: ", filename
        return "ErrorGetMD5"


def Generate_Expected_Data (path):
    '''
    Description:
        This Module generates some given string and file path that we use to create expected data for file verification.
        If MD5 folder does not exists, it will create one
        It will delete any previous output file from C:\MD5 folder
        It will opent the folder location of the output file at the end. 
                 
    Parameter Description:
        - path : folder path that you want to generate the MD5 of    
    Example: 
        - Generate_Expected_Data ('C:\Users\ihossain\Videos\yaseen')   
    Output:
        - it will output to C:\MD5\Output.txt 
            
    ======= End of Instruction: =========

'''
    
    MD5Path = "C:\MD5"
    OutputPath = "C:\MD5\Output.txt"
    if not os.path.exists(MD5Path):
        os.makedirs(MD5Path)
    
        
        
    
    if os.path.exists: os.remove(OutputPath)
        
    

    for root, dirs, files in os.walk(path):
       #print dirs
       for name in files:       
           filename = os.path.join(root, name)
           print filename
           #print name
           
           print md5(filename)
           initial_string = "('~MKSID~','~SectionName~',E'"
           middle_string = "','"
           last_string = "'),"
           md5_of_file = md5(filename)
           
           trim_file_name_remove_original_path = filename.replace(path, "")
           trim_file_name_add_extra_quote = trim_file_name_remove_original_path.replace("'", "''")
           trim_file_name = trim_file_name_add_extra_quote.replace("\\","\\\\")
           
           full_string = initial_string + trim_file_name + middle_string + md5_of_file + last_string 
           file = codecs.open("C:\MD5\Output.txt", "a", "utf-8")
           #file.write(name)
           #file.write (" : ")
           #file.write(md5_of_file) 
           file.write(full_string) 
           file.write ("\n") 
           file.write(codecs.BOM_UTF8)     
           file.close()
    subprocess.Popen('explorer ' + MD5Path)


Generate_Expected_Data ('C:\Users\ihossain\Videos\yaseen')   

#print md5("Y:\\Video\\AVI\\XVID\\Hot Tub Time Machine (2010) R5 DVDRip XviD-MAXSPEED www.torentz.3xforum.ro.avi")