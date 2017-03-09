__author__='minar'
import os, sys, subprocess, inspect
from Utilities import CommonUtil

from lxml import etree
from StringIO import StringIO
from xml.etree import ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from glob import glob


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
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
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
        except Exception, e:
            CommonUtil.ExecLog(sModuleInfo, "%s file is not validated. %s" % (filepath, e), 3)
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "Exception: %s" % e, 3)


def check_form(filepath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        x = ET.fromstring(filepath)
        CommonUtil.ExecLog(sModuleInfo, "%s file is well-formed. %s" % filepath, 1)
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "%s file is not well-formed. %s" % (filepath, e), 3)

def check_wellformed(filename):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    #filename = "/home/asci/AssetScience/recell_dse-in-test/Launcher/resource/configurations/desktop-fail-codes.xml"
    try:
        parser = make_parser( )
        parser.setContentHandler(ContentHandler( ))
        parser.parse(filename)
        CommonUtil.ExecLog(sModuleInfo, "%s is well-formed. %s" % filename, 1)
    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "%s is NOT well-formed! %s" % (filename, e), 3)


def check_exist(filepath):

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        if os.path.isfile(filepath):
            CommonUtil.ExecLog(sModuleInfo, "%s file is found." % filepath, 1)
            return "Passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "%s file is not found." % filepath, 3)
            return "Failed"

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "%s file existence is not checked. %s" % (filepath, e), 3)
        return "Failed"


def check_tags_exist(filepath, tag, subtag):

    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

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

    except Exception, e:
        CommonUtil.ExecLog(sModuleInfo, "%s - %s tag existence is not checked. %s" % (filepath, tag, e), 3)
        return "Failed"
