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
#    Test_For_Compare_Text()
#     Test_For_Double_Matching()
#     Test_For_Get_All_Elements()
#     Test_For_Get_Elements()
#     Test_For_Individual_Actions()
    Test_For_Sequential_Actions()
#    Nissan_Test_Page()
#   Test_For_Get_Elements()
#   Test_For_Double_Matching()
#   Test_For_Get_All_Elements()
##    Henry's Test Page:
#    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/Categories/67-Digital-Cameras-Compare-and-Buy.aspx?source=Cornerstone_Henry%27s+Canada&bypassredirect=true&gclid=CKLv3b3F380CFZY1aQod4jMI2w')
#    YTS.BuiltInFunctions.Get_Element('link_text','Lighting & Studio','id','header_lstCategories_category_4','parent')    

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
#     YTS.BuiltInFunctions.Get_All_Elements('text', 'Search')
#     print "end of text test case"
#     #Case 1.B: Param type = tag name
#     YTS.BuiltInFunctions.Get_All_Elements('tag_name', 'div')
#     print "end of tag test case"
#     #Case 1.C: Param type = link text
#     YTS.BuiltInFunctions.Get_All_Elements('link_text', 'Lighting & Studio')
#     print "end of link test case"
#     #Case 1.D: Param type = css
#     YTS.BuiltInFunctions.Get_All_Elements('css_selector', 'li.A')
#     print "end of css case"
#     #Case 1.E: Param type = others /by xpath
#     YTS.BuiltInFunctions.Get_All_Elements('id', 'header_lstCategories_dropNav_4')
#     print "end of xpath case"
    
    ##Testing YouTube Stuff:
    YTS.BuiltInFunctions.Go_To_Link('https://www.youtube.com/?hl=en&gl=CA')
    YTS.BuiltInFunctions.Get_All_Elements('link_text', 'Best of Youtube')

def Test_For_Double_Matching():
    #Text and tag
    YTS.BuiltInFunctions.Go_To_Link('https://www.henrys.com/SignIn.aspx')
    YTS.BuiltInFunctions.Get_Double_Matching_Elements('text', 'Email', 'tag_name', 'd')

def Nissan_Test_Page():
    YTS.BuiltInFunctions.Go_To_Link('http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0')
    step_data_nissan = [ [ ( 'class' , 'btnCenter-blue' , False , False ) , ( 'class' , 'basevehicle' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action_click_hover' , 'click' , False , False ) ] , [ ( 'class' , 'x-form-trigger x-form-trigger-arrow ' , False , False ) , ( 'class' , 'gwt-PopupPanel' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action' , 'click' , False , False ) ] ]    
    YTS.BuiltInFunctions.Sequential_Actions(step_data_nissan)

def Test_For_Individual_Actions():
    step_data_text_new = [ [ ( 'id' , 'txtSearch' , False , False ) , ( 'enter_text' , 'action' , 'camera' , False , False ) ] ]
    step_data_wait_new = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'wait_for_element' , 'action' , '10' , False , False ) ] ]
    step_data_click_new = [ [ ( 'id' , 'btnSearch' , False , False ) , ( 'click_hover' , 'action' , 'click' , False , False ) ] ]
    step_data_hover_new = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'click_hover' , 'action' , 'hover' , False , False ) ] ]
    YTS.BuiltInFunctions.Enter_Text_In_Text_Box(step_data_text_new)
    YTS.BuiltInFunctions.Click_Element(step_data_click_new)
    YTS.BuiltInFunctions.Wait_For_New_Element(step_data_wait_new)
    YTS.BuiltInFunctions.Hover_Over_Element(step_data_hover_new)
  
def Test_For_Sequential_Actions():
    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/')
    step_data_mod = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] , [ ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] , [ ( 'id' , 'txtSearch' , False , False ) , ( 'text' , 'action' , 'camera' , False , False ) ] , [ ( 'id' , 'middle-storelocation' , False , False ) , ( 'true' , 'logic' , '4,6' , False , False ) , ( 'false' , 'logic' , '5' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_1' , False , False ) , ( 'class' , 'B' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False )] , [  ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'click' , 'action' , 'click' , False , False )  ] ]
    YTS.BuiltInFunctions.Sequential_Actions(step_data_mod)


def Test_For_Compare_Text():
    step_data_text = [ [ ( 'text' , 'Drones' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_1' , False , False ) , ( 'class' , 'B' , False , False ) ] ]
    YTS.BuiltInFunctions.Go_To_Link('https://www.henrys.com')
    YTS.BuiltInFunctions.Compare_Text_Data(step_data_text)

Create_Site_Content()
