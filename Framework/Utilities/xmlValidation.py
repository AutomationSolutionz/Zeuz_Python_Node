# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import os, sys, subprocess, inspect
from Framework.Utilities import CommonUtil

from lxml import etree
from StringIO import StringIO
from xml.etree import ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob


MODULE_NAME = inspect.getmoduleinfo(__file__).name


def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def validate_xml(filepath):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        f = StringIO('''\
         <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
         <xsd:element name="a" type="AType"/>
         <xsd:complexType name="AType">
           <xsd:sequence>
             <xsd:element name="b" type="xsd:string" />
           </xsd:sequence>
         </xsd:complexType>
         </xsd:schema>
         ''')
        xmlschema_doc = etree.parse(f)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        f = open(filepath)
        xml = f.read()
        f.close()

        valid = StringIO(xml)
        doc = etree.parse(valid)
        try:
            xmlschema.validate(doc)
            CommonUtil.ExecLog(sModuleInfo, "%s file is validated." % filepath, 1)

        except Exception:
            errMsg = "%s file is not validated." % filepath
            return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def check_form(filepath):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        x = ET.fromstring(filepath)
        CommonUtil.ExecLog(sModuleInfo, "%s file is well-formed. %s" % filepath, 1)

    except Exception:
        errMsg = "%s file is not well-formed." % filepath
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def check_wellformed(filename):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    #filename = "/home/asci/AssetScience/recell_dse-in-test/Launcher/resource/configurations/desktop-fail-codes.xml"
    try:
        parser = make_parser( )
        parser.setContentHandler(ContentHandler( ))
        parser.parse(filename)
        CommonUtil.ExecLog(sModuleInfo, "%s is well-formed. %s" % filename, 1)

    except Exception:
        errMsg = "%s is NOT well-formed! " % filename
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


def check_exist(filepath):

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        if os.path.isfile(filepath):
            CommonUtil.ExecLog(sModuleInfo, "%s file is found." % filepath, 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "%s file is not found." % filepath, 3)
            return "Failed"


    except Exception:
        errMsg = "%s file existence is not checked." % filepath
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


def check_tags_exist(filepath, tag, subtag):

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        doc = ET.parse(filepath).getroot()
        for event in doc.findall(tag):
            if event is None:
                CommonUtil.ExecLog(sModuleInfo, "%s tag is not found." % tag, 3)
            else:
                CommonUtil.ExecLog(sModuleInfo, "%s tag is found." % tag, 1) 

            for host in event.findall(subtag):
                if host is None:
                    CommonUtil.ExecLog(sModuleInfo, "%s tag is not found." % subtag, 3)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "%s tag is found in %s." % (subtag, tag), 1) 


    except Exception:
        errMsg = "%s - %s tag existence is not checked. " % (filepath, tag)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
