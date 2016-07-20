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
#    Nissan_Test_Page()
#   Test_For_Get_Elements()
#   Test_For_Double_Matching()
#   Test_For_Get_All_Elements()
##    Henry's Test Page:
#    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/Categories/67-Digital-Cameras-Compare-and-Buy.aspx?source=Cornerstone_Henry%27s+Canada&bypassredirect=true&gclid=CKLv3b3F380CFZY1aQod4jMI2w')
#    YTS.BuiltInFunctions.Get_Element('link_text','Lighting & Studio','id','header_lstCategories_category_4','parent')    

##    Quest Test Page:
#    YTS.BuiltInFunctions.Go_To_Link('https://uwaterloo.ca/quest/')
#    YTS.BuiltInFunctions.Get_Element('link_text','//uwaterloo.ca/')
#    YTS.BuiltInFunctions.Click_Element('class','leaf about-quest mid-453')
#    YTS.BuiltInFunctions.Get_Element('link_text','About Quest','class','leaf about-quest mid-453','parent')
#    YTS.BuiltInFunctions.Enter_Text_In_Text_Box('id', 'masthead-search-term','coldplay', 'placeholder', 'Search')

##    Youtube Test Page:
#[ [ ( 'id' , 'id_val' , False , False ) , ( 'ref' , 'ref_val' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action' , 'hover' , False , False ) ] , [ ( 'id' , 'id2' , False , False ) , ( 'ref2' , 'val2' , False , False ) , ( 'rel2' , 'parent2' , False , False ) ] , [ ( 'action' , 'hover' , False , False ) ] , [ ( 'id3' , 'idval3' , False , False ) , ( 'ref3' , 'refval3' , False , False ) , ( 'rel3' , 'parent3' , False , False ) ] , [ ( 'action' , 'click' , False , False ) ] ]
#    step_data_navigation = [ [ ( 'id' , 'search-btn' , False , False ) , ( 'class' , 'yt-uix-button yt-uix-button-size-default yt-uix-button-default search-btn-component search-button' , False , False ) ] , [ ( 'action' , 'click' , False , False ) ] ]
    step_data_navigation = [ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) ] , [ ( 'action_click_hover' , 'hover' , False , False ) ] , [ ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_dropContent_4' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action_click_hover' , 'click' , False , False ) ] , [ ( 'id' , 'txtSearch' , False , False ) ] , [ ( 'action_enter_text' , 'camera' , False , False ) ] ]
    step_data_mod=[ [ ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'class' , 'A' , False , False ) , ( 'action_click_hover' , 'hover' , False , False ) ] , [ ( 'text' , 'Studio Strobes' , False , False ) , ( 'id' , 'header_lstCategories_category_4' , False , False ) , ( 'relation' , 'parent' , False , False ) , ( 'action_click_hover' , 'click' , False , False ) ] , [ ( 'id' , 'txtSearch' , False , False ) , ( 'action_enter_text' , 'camera' , False , False ) ] ]
    step_data_click =  [ [ ( 'id' , 'search-btn' , False , False ) , ( 'class' , 'yt-uix-button yt-uix-button-size-default yt-uix-button-default search-btn-component search-button' , False , False ) ] ] 
    step_data_wait = [ ( 'class' , 'num-results first-focus' , False , False ) ]  , [ ( 'timeout' , '30' , False , False ) ] 
    step_data_text =[ [ ( 'id' , 'masthead-search-term' , False , False ) , ( 'placeholder' , 'Search' , False , False ) ]  , [ ( 'text_value' , 'coldplay' , False , False ) ] ]    
#     YTS.BuiltInFunctions.Go_To_Link('https://www.youtube.com/?hl=en&gl=CA')
    YTS.BuiltInFunctions.Go_To_Link('http://www.henrys.com/')
    YTS.BuiltInFunctions.Sequential_Actions(step_data_navigation)
#     YTS.BuiltInFunctions.Enter_Text_In_Text_Box('id', 'masthead-search-term','coldplay','placeholder', 'Search')
#     YTS.BuiltInFunctions.Enter_Text_In_Text_Box(step_data_text)
#     YTS.BuiltInFunctions.Click_Element(step_data_click)
#     YTS.BuiltInFunctions.Click_Element('id', 'search-btn','class','yt-uix-button yt-uix-button-size-default yt-uix-button-default search-btn-component search-button')
#     YTS.BuiltInFunctions.Wait_For_New_Element(step_data_wait)
    
#    YTS.BuiltInFunctions.Go_To_Link('http://www.bestbuy.ca/en-CA/product/hewlett-packard-hp-officejet-pro-8710-wireless-colour-all-in-one-inkjet-printer-8710/10419576.aspx?path=1b43ebda1b346b9d5a595ee064882e90en02')
#    YTS.BuiltInFunctions.Go_To_Link('http://assetscience.automationsolutionz.com/Home/ManageTestCases/SearchEdit/') 
#    YTS.BuiltInFunctions.Go_To_Link('http://qa-factory.assetscience.com/totalanalysis/devicesearch/list')    
#    YTS.BuiltInFunctions.Login_To_Application('rrakin', 'password', 'username', 'password', 'submit')#'loginbtn')
#    time.sleep(10)
#    YTS.BuiltInFunctions.Get_Table_Elements('css_selector', 'ul.std-tablist', 'tag_name', 'li', 'tag_name', 'span')
#    YTS.BuiltInFunctions.Get_Table_Elements('tag_name', 'tbody', 'tag_name', 'tr', 'tag_name','td','class','table visible table-striped table-bordered table-hover','parent')
#    YTS.BuiltInFunctions.Get_Table_Elements('tag_name', 'tbody', 'tag_name', 'tr', 'tag_name', 'td')
    #for each_row in list_1:
    #    row_element = list_1[each_row]
    #    print row_element
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

Create_Site_Content()
