__author__ = 'asci'
import ConfigParser,os
'''constants'''
file_name='global_config.ini'

def get_config_value(section,key):
    config=ConfigParser.SafeConfigParser()
    config.read(os.getcwd()+os.sep+file_name)
    return config.get(section,key)

def remove_config_value(section,value):
    config=ConfigParser.SafeConfigParser()
    config.read(os.getcwd()+os.sep+file_name)
    config.remove_option(section,value)
    with(open(os.getcwd()+os.sep+file_name,'w')) as open_file:
        config.write(open_file)

def add_config_value(section,key,value):
    config=ConfigParser.SafeConfigParser()
    config.read(os.getcwd()+os.sep+file_name)
    config.set(section,key,value)
    with(open(os.getcwd()+os.sep+file_name,'w')) as open_file:
        config.write(open_file)