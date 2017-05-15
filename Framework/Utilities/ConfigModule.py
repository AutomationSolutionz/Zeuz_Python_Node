# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import ConfigParser,os
'''constants'''
file_name='settings.conf'


def get_config_value(section,key,location=False):
    """
    :param section: name of section
    :param key: name of key
    :return: value of the key in that section
    """
    try:
        config=ConfigParser.SafeConfigParser()
        if not location:
            _file_name=os.getcwd()+os.sep+file_name
        else:
            _file_name=location
        config.read(_file_name)
        return config.get(section,key)
    except ConfigParser.NoSectionError:
        #print "No section in that name: %s"%section
        return ""
    except ConfigParser.NoOptionError:
        #print "No option in that name: %s"%key
        return ""


def remove_config_value(section,value,location=False):
    config=ConfigParser.SafeConfigParser()
    if not location:
        _file_name=os.getcwd()+os.sep+file_name
    else:
        _file_name=location
    config.read(_file_name)
    config.remove_option(section,value)
    with(open(_file_name,'w')) as open_file:
        config.write(open_file)
    open_file.close()


def add_config_value(section,key,value,location=False):
    try:
        config=ConfigParser.SafeConfigParser()
        if not location:
            _file_name=os.getcwd()+os.sep+file_name
        else:
            _file_name=location
        config.read(_file_name)
        config.set(section,key,value)
        with(open(_file_name,'w')) as open_file:
            config.write(open_file)
        open_file.close()
        return True
    except ConfigParser.NoSectionError:
        #print "No section in that name: %s"%section
        return ""
    except ConfigParser.NoOptionError:
        #print "No option in that name: %s"%key
        return ""


def get_all_option(section_name,location=False):
    """
    :param section_name: given section name
    :return: list of all option on that section
    """
    try:
        config=ConfigParser.SafeConfigParser()
        if not location:
            _file_name=os.getcwd()+os.sep+file_name
        else:
            _file_name=location
        config.read(_file_name)
        return config.options(section_name)
    except ConfigParser.NoSectionError,e:
        print 'found no section with name %s'%section_name
        return []
    except ConfigParser.NoOptionError,e:
        print 'found no options on the section %s'%section_name
        return []


def add_section(section_name,location=False):
    """
    :param section_name: name of the section to add
    :return: true or false
    """
    try:
        config=ConfigParser.SafeConfigParser()
        if not location:
            _file_name=os.getcwd()+os.sep+file_name
        else:
            _file_name=location
        config.read(_file_name)
        config.add_section(section_name)
        with(open(_file_name,'w')) as open_file:
            config.write(open_file)
        open_file.close()
        return True
    except ConfigParser.NoSectionError,e:
        print 'found no section with name %s'%section_name
        return []
    except ConfigParser.NoOptionError,e:
        print 'found no options on the section %s'%section_name
        return []


def clean_config_file(location=False):
    try:
        config=ConfigParser.SafeConfigParser()
        if not location:
            _file_name=os.getcwd()+os.sep+file_name
        else:
            _file_name=location
        get_all_section=config.sections()
        for each in get_all_section:
            config.remove_section(each)
        with(open(_file_name,'w')) as open_file:
            config.write(open_file)
        open_file.close()
        return True
    except Exception, e:
        print e
        return False
