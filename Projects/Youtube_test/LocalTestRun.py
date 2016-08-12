'''
Created on July 4, 2016

@author: Riasat Rakin
'''
import sys
import os
import time
sys.path.append(os.path.dirname(os.getcwd()))
from Projects.Youtube_test import Youtube_Search as YTS


def Create_Site_Content():
    YTS.BuiltInFunctions.Open_Browser('firefox')
    Test_For_Validate_Table()
#     Test_For_Get_Table_Elements()
#     Test_For_Compare_Text()
#     Test_For_Double_Matching()
#     Test_For_Get_All_Elements()
#     Test_For_Get_Elements()
#     Test_For_Individual_Actions()
#     Test_For_Sequential_Actions()
# #    Nissan_Test_Page()
#     Test_For_Get_Elements()
#     Test_For_Double_Matching()
#     Test_For_Get_All_Elements()
##    Henry's Test Page:
    print "test complete"
#    YTS.Item_Search('webdriver')

def Test_For_Get_Elements():
    YTS.BuiltInFunctions.Go_To_Link('http://www.kijiji.ca/h-kitchener-waterloo/1700212')
#    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/Categories/67-Digital-Cameras-Compare-and-Buy.aspx?source=Cornerstone_Henry%27s+Canada&bypassredirect=true&gclid=CKLv3b3F380CFZY1aQod4jMI2w')
    #Case 1: ref_parent_or_child == false
    #Case 1.A: ref value and elem = false: single matching
    YTS.BuiltInFunctions.Get_Element('id','SearchInput')
    print "Case 1.A"
    #Case 1.B: ref value and elem != false: double matching
    YTS.BuiltInFunctions.Get_Element('id','SearchInput','name','keywords')
    print "Case 1.B"

    #Case 2: ref_parent_or_child == parent
    YTS.BuiltInFunctions.Get_Element('id','SearchInput','id','InputContainer','parent')
    print "Case 2"
#   YTS.BuiltInFunctions.Get_Element('text','Accessories','id','header-menus','parent')
    print "end of parent"

    #Case 3: ref_parent_or_child == child (uses table cases - using Henry's website
#    YTS.BuiltInFunctions.Get_Element('text','Lighting & Studio','text','Studio Strobes','child')
#    print "end of child"

def Test_For_Get_All_Elements():
    #Case 1: Parent = False
    #Case 1.A: Param type = text
    YTS.BuiltInFunctions.Get_All_Elements('text', 'Search')
    print "end of text test case"
    #Case 1.B: Param type = tag name
    YTS.BuiltInFunctions.Get_All_Elements('tag_name', 'div')
    print "end of tag test case"
    #Case 1.C: Param type = link text
    YTS.BuiltInFunctions.Get_All_Elements('link_text', 'Lighting & Studio')
    print "end of link test case"
    #Case 1.D: Param type = css
    YTS.BuiltInFunctions.Get_All_Elements('css_selector', 'li.A')
    print "end of css case"
    #Case 1.E: Param type = others /by xpath
    YTS.BuiltInFunctions.Get_All_Elements('id', 'header_lstCategories_dropNav_4')
    print "end of xpath case"
    
    
def Test_For_Double_Matching():
    #text, tagname,linktext/href,css,partiallinktext
    YTS.BuiltInFunctions.Go_To_Link('https://www.henrys.com/SignIn.aspx')
    #Text and tag
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('text', 'Email', 'tag', 'td')
    print "end text tag"
    #Text and partial link text
    #Text and link text
    #Text and CSS
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('css', 'td.field', 'text', 'Email')
    print "end text css"
    #Tag and CSS
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('tag', 'td', 'css', 'td.field')
    print "end css tag"
    #Tag and partial link text
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('tag', 'a', 'partial_link_text', 'Print')
    print "end partiallinktext tag"
    #Tag and link text
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('tag', 'a', 'link_text', 'Printers')
    print "end linktext tag"    
    #CSS and link text
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('css', 'td.field', 'link_text', 'Password')
    print "end linktext css"
    #CSS and partial link text
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('css', 'td.field', 'partial_link_text', 'word')
    print "end partiallinktext css"
      
def Nissan_Test_Page():
    YTS.BuiltInFunctions.Go_To_Link('http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0')
    step_data_nissan = [ [ ( 'class' , 'btnCenter-blue' , False , False ) , ( 'class' , 'basevehicle' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action_click_hover' , 'click' , False , False ) ] , [ ( 'class' , 'x-form-trigger x-form-trigger-arrow ' , False , False ) , ( 'class' , 'gwt-PopupPanel' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action' , 'click' , False , False ) ] ]    
    YTS.BuiltInFunctions.Sequential_Actions(step_data_nissan)

def Test_For_Individual_Actions():
    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/')
    step_data_text_new = [ [ ( 'id' , 'txtSearch' , False , False ) , ( 'enter_text' , 'action' , 'camera' , False , False ) ] ]
    step_data_wait_new = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'wait_for_element' , 'action' , '10' , False , False ) ] ]
    step_data_click_new = [ [ ( 'id' , 'btnSearch' , False , False ) , ( 'click_hover' , 'action' , 'click' , False , False ) ] ]
    step_data_hover_new = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'click_hover' , 'action' , 'hover' , False , False ) ] ]
    step_data_keystroke = [ [ ( 'id' , 'txtSearch' , False , False ) , ( 'keystroke_chars' , 'action' , 'AbCd' , False , False ) ] ]
    #YTS.BuiltInFunctions.Enter_Text_In_Text_Box(step_data_text_new)
    #YTS.BuiltInFunctions.Click_Element(step_data_click_new)
    #YTS.BuiltInFunctions.Wait_For_New_Element(step_data_wait_new)
    #YTS.BuiltInFunctions.Hover_Over_Element(step_data_hover_new)
    YTS.BuiltInFunctions.Keystroke_For_Element(step_data_keystroke)
  
def Test_For_Sequential_Actions():
    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/')
    #YTS.BuiltInFunctions.Go_To_Link('http://qa-factory.assetscience.com/totalanalysis/login/auth')
    step_data_mod = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] , [ ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] , [ ( 'id' , 'txtSearch' , False , False ) , ( 'text' , 'action' , 'camera' , False , False ) ] , [ ( 'id' , 'middle-storelocation' , False , False ) , ( 'true' , 'logic' , '5,7' , False , False ) , ( 'false' , 'logic' , '6' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_1' , False , False ) , ( 'class' , 'B' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False )] , [  ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'click' , 'action' , 'click' , False , False )  ] ]##[ [ ( 'id' , 'username' , False , False ) , ( 'text' , 'action' , 'rrakin' , False , False ) ] , [ ( 'id' , 'password' , False , False ) , ( 'text' , 'action' , 'password' , False , False ) ] , [ ( 'id' , 'submit' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] ]#[ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] , [ ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] , [ ( 'id' , 'txtSearch' , False , False ) , ( 'text' , 'action' , 'camera' , False , False ) ] , [ ( 'id' , 'middle-storelocation' , False , False ) , ( 'true' , 'logic' , '4,6' , False , False ) , ( 'false' , 'logic' , '5' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_1' , False , False ) , ( 'class' , 'B' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False )] , [  ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'click' , 'action' , 'click' , False , False )  ] ]
    #step_data = [ [ ( 'id' , 'txtSearch' , False , False ) , ( 'text' , 'action' , 'camera' , False , False ) ] , [ ( 'id' , 'btnSearch' , False , False ) , ( 'keystroke_keys' , 'action' , 'Enter' , False , False ) ] ]
    #YTS.BuiltInFunctions.Go_To_Link('http://www.inflightintegration.com/')
    #step_data = [ [ ( 'href' , 'Schedule a Demo' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ]  , [ ( 'name' , 'element_1_1' , False , False ) , ( 'text' , 'action' , 'Zeuz' , False , False ) ]  , [ ( 'id' , 'saveForm' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] ]
    #step_data = [ [ ( 'current_page' , 'current_page' , False , False ) , ( 'validate full text' , 'action' , 'Henrys - Photo - Video - Digital' , False , False ) ] ]#[ [ ( 'id' , 'header-nav-custcare' , False , False ) , ( 'validate partial text' , 'action' , 'Customer Care' , False , False ) ] ]
    YTS.BuiltInFunctions.Sequential_Actions(step_data_mod)

def Test_For_Get_Table_Elements():
    #YTS.BuiltInFunctions.Go_To_Link('http://www.bestbuy.ca/en-CA/product/lg-electronics-lg-24-fhd-60hz-5ms-gtg-tn-led-monitor-24m38d-b-aus-black-24m38d-b-aus/10440826.aspx?icmp=Homepage_BTS_SectionF_weeklydeals_1Big_computing_monitors_QL_Lgmonitoroffer')
    #YTS.BuiltInFunctions.Get_Table_Elements('class', 'std-tablist')
    YTS.BuiltInFunctions.Go_To_Link('http://qa-factory.assetscience.com/totalanalysis/devicesearch/list')
    YTS.BuiltInFunctions.Login_To_Application('rrakin', 'password', 'username', 'password', 'submit')
    YTS.BuiltInFunctions.Get_Table_Elements('tag', 'tbody')
    

def Test_For_Validate_Table():
    YTS.BuiltInFunctions.Go_To_Link('http://www.bestbuy.ca/en-CA/product/nikon-nikon-d5200-dslr-camera-with-af-s-dx-nikkor-18-55mm-vr-ii-lens-kit-refurbished-33887b/10450965.aspx?path=ba7ae6c53f36742b9bfe6848e8c22878en02')
    step_data = [ [ ( 'class' , 'std-tablist' , False , False ) , ( 'table' , 'table_validate' , 'table' , False , False ) , ( 'col1' , '1' , 'Camera Model' , False , False ) , ( 'col2' , '1' , 'Nikon D5200 Kit' , False , False ) , ( 'col1' , '2' , 'Lens Mount' , False , False ) , ( 'col2' , '2' , 'Nikon F Bayonet Mount' , False , False ) , ( 'col1' , '3' , 'Image Sensor' , False , False ) , ( 'col2' , '3' , ' ' , False , False ) , ( 'col1' , '4' , 'Sensor Type' , False , False ) , ( 'col2' , '4' , 'CMOS' , False , False ) ] ]        
    #YTS.BuiltInFunctions.Go_To_Link('http://qa-factory.assetscience.com/totalanalysis/devicesearch/list')
    #YTS.BuiltInFunctions.Login_To_Application('rrakin', 'password', 'username', 'password', 'submit')
    YTS.BuiltInFunctions.Validate_Table(step_data)

def Test_For_Compare_Text():
    #step_data_text = [ [ ( 'text','Drones' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_1' , False , False ) , ( 'class' , 'B' , False , False ) ] ]
    #step_data_new = [ [ ( 'current_page' , 'current_page' , False , False ) , ( 'expected text' , 'full match' , 'Henrys - Photo - Video - Digital' , False , False ) ] ]
    step_data_element = [ [ ( 'id' , 'header-nav-custcare' , False , False ) , ( 'validate partial text' , 'action' , 'Customer Care' , False , False ) ] ]
    YTS.BuiltInFunctions.Go_To_Link('https://www.henrys.com')
    YTS.BuiltInFunctions.Validate_Text(step_data_element)

Create_Site_Content()
