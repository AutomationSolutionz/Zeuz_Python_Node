'''
Created on July 4, 2016

@author: Riasat Rakin
'''
import sys
import os
import time
sys.path.append(os.path.dirname(os.getcwd()))
from Projects.Bunz import DesktopWeb as DesktopWeb
from Projects.Bunz import Mobile_Functions as MobileFunctions

#temp_config=os.path.join(os.path.join(FL.get_home_folder(),os.path.join('Desktop',os.path.join('AutomationLog',ConfigModule.get_config_value('Temp','_file')))))


def Create_Site_Content():
    DesktopWeb.BuiltInFunctions.Open_Browser('chrome')
#    Test_For_Validate_Table()
#     Test_For_Get_Table_Elements()
#     Test_For_Compare_Text()
#     Test_For_Double_Matching()
#     Test_For_Get_All_Elements()
#     Test_For_Get_Elements()
#     Test_For_Individual_Actions()
    Test_For_Sequential_Actions()
# #    Nissan_Test_Page()
#     Test_For_Get_Elements()
#     Test_For_Double_Matching()
#     Test_For_Get_All_Elements()
##    Henry's Test Page:
    print "test complete"
#    DesktopWeb.Item_Search('webdriver')

def Test_For_Get_Elements():
    DesktopWeb.BuiltInFunctions.Go_To_Link('http://www.kijiji.ca/h-kitchener-waterloo/1700212')
#    DesktopWeb.BuiltInFunctions.Go_To_Link('http://www.henrys.com/Categories/67-Digital-Cameras-Compare-and-Buy.aspx?source=Cornerstone_Henry%27s+Canada&bypassredirect=true&gclid=CKLv3b3F380CFZY1aQod4jMI2w')
    #Case 1: ref_parent_or_child == false
    #Case 1.A: ref value and elem = false: single matching
    DesktopWeb.BuiltInFunctions.Get_Element('id','SearchInput')
    print "Case 1.A"
    #Case 1.B: ref value and elem != false: double matching
    DesktopWeb.BuiltInFunctions.Get_Element('id','SearchInput','name','keywords')
    print "Case 1.B"

    #Case 2: ref_parent_or_child == parent
    DesktopWeb.BuiltInFunctions.Get_Element('id','SearchInput','id','InputContainer','parent')
    print "Case 2"
#   DesktopWeb.BuiltInFunctions.Get_Element('text','Accessories','id','header-menus','parent')
    print "end of parent"

    #Case 3: ref_parent_or_child == child (uses table cases - using Henry's website
#    DesktopWeb.BuiltInFunctions.Get_Element('text','Lighting & Studio','text','Studio Strobes','child')
#    print "end of child"

def Test_For_Get_All_Elements():
    #Case 1: Parent = False
    #Case 1.A: Param type = text
    DesktopWeb.BuiltInFunctions.Get_All_Elements('text', 'Search')
    print "end of text test case"
    #Case 1.B: Param type = tag name
    DesktopWeb.BuiltInFunctions.Get_All_Elements('tag_name', 'div')
    print "end of tag test case"
    #Case 1.C: Param type = link text
    DesktopWeb.BuiltInFunctions.Get_All_Elements('link_text', 'Lighting & Studio')
    print "end of link test case"
    #Case 1.D: Param type = css
    DesktopWeb.BuiltInFunctions.Get_All_Elements('css_selector', 'li.A')
    print "end of css case"
    #Case 1.E: Param type = others /by xpath
    DesktopWeb.BuiltInFunctions.Get_All_Elements('id', 'header_lstCategories_dropNav_4')
    print "end of xpath case"
    
    
def Test_For_Double_Matching():
    #text, tagname,linktext/href,css,partiallinktext
    DesktopWeb.BuiltInFunctions.Go_To_Link('https://www.henrys.com/SignIn.aspx')
    #Text and tag
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('text', 'Email', 'tag', 'td')
    print "end text tag"
    #Text and partial link text
    #Text and link text
    #Text and CSS
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('css', 'td.field', 'text', 'Email')
    print "end text css"
    #Tag and CSS
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('tag', 'td', 'css', 'td.field')
    print "end css tag"
    #Tag and partial link text
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('tag', 'a', 'partial_link_text', 'Print')
    print "end partiallinktext tag"
    #Tag and link text
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('tag', 'a', 'link_text', 'Printers')
    print "end linktext tag"    
    #CSS and link text
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('css', 'td.field', 'link_text', 'Password')
    print "end linktext css"
    #CSS and partial link text
    DesktopWeb.BuiltInFunctions.Get_Double_Matching_Elements('css', 'td.field', 'partial_link_text', 'word')
    print "end partiallinktext css"
      
def Nissan_Test_Page():
    DesktopWeb.BuiltInFunctions.Go_To_Link('http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0')
    step_data_nissan = [ [ ( 'class' , 'btnCenter-blue' , False , False ) , ( 'class' , 'basevehicle' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action_click_hover' , 'click' , False , False ) ] , [ ( 'class' , 'x-form-trigger x-form-trigger-arrow ' , False , False ) , ( 'class' , 'gwt-PopupPanel' , False , False ) , ( 'relation' , 'parent' , False , False ) ] , [ ( 'action' , 'click' , False , False ) ] ]    
    DesktopWeb.BuiltInFunctions.Sequential_Actions(step_data_nissan)

def Test_For_Individual_Actions():
    DesktopWeb.BuiltInFunctions.Go_To_Link('http://bunz.com/')
    step_data_text_new = [ [ ( 'id' , '', 'txtSearch' , False , False ), ( 'text' , 'action' , 'camera' , False , False ) ] ]
    step_data_wait_new = [ [ ( 'id' , '', 'header_lstCategories_category_4' , False , False ) , ( 'wait' , 'action' , '10' , False , False ) ] ]
    step_data_click_new = [ [ ( 'id' , '', 'btnSearch' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] ]
    step_data_hover_new = [ [ ( 'id' , '', 'header_lstCategories_category_4' , False , False ) , ( 'hover' , 'action' , 'hover' , False , False ) ] ]
    step_data_keystroke = [ [ ( 'id' , '', 'txtSearch' , False , False ) , ( 'keystroke_chars' , 'action' , 'AbCd' , False , False ) ] ]
    DesktopWeb.BuiltInFunctions.Enter_Text_In_Text_Box(step_data_text_new)
    DesktopWeb.BuiltInFunctions.Click_Element(step_data_click_new)
    DesktopWeb.BuiltInFunctions.Wait_For_New_Element(step_data_wait_new)
    DesktopWeb.BuiltInFunctions.Hover_Over_Element(step_data_hover_new)
    DesktopWeb.BuiltInFunctions.Keystroke_For_Element(step_data_keystroke)
  
def Test_For_Sequential_Actions():
    DesktopWeb.BuiltInFunctions.Go_To_Link('http://bunz.com/')
    step_data_mod = [ [ ( 'partial_link_text' , '' , 'Login or Signup' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ]  , [ ( 'name' , '' , 'Login with Email' , False , False ) , ( 'wait' , 'action' , '10' , False , False ) ]  , [ ( 'name' , '' , 'Login with Email' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] , [ ( 'name' , '' , 'email' , False , False ) , ( 'text' , 'action' , 'test@bunz.com' , False , False ) ]  ,  [ ( 'name' , '' , 'password' , False , False ) , ( 'text' , 'action' , 'password' , False , False ) ]  ,  [ ( 'name' , '' , 'create' , False , False ) , ( 'click' , 'action' , 'click' , False , False ) ] ]
    DesktopWeb.BuiltInFunctions.Sequential_Actions(step_data_mod)

def Test_For_Get_Table_Elements():
    DesktopWeb.BuiltInFunctions.Go_To_Link('http://www.bestbuy.ca/en-CA/product/lg-electronics-lg-24-fhd-60hz-5ms-gtg-tn-led-monitor-24m38d-b-aus-black-24m38d-b-aus/10440826.aspx?icmp=Homepage_BTS_SectionF_weeklydeals_1Big_computing_monitors_QL_Lgmonitoroffer')
    DesktopWeb.BuiltInFunctions.Get_Table_Elements('class', 'std-tablist')
    

def Test_For_Validate_Table():
    DesktopWeb.BuiltInFunctions.Go_To_Link('http://www.bestbuy.ca/en-CA/product/nikon-nikon-d5200-dslr-camera-with-af-s-dx-nikkor-18-55mm-vr-ii-lens-kit-refurbished-33887b/10450965.aspx?path=ba7ae6c53f36742b9bfe6848e8c22878en02')
    step_data =[ [ ('class' , '', 'std-tablist' , False , False ) , ( 'ignore_row' , 'table_validate' , 'default' , False , False ) , (' 1 ', ' 1 ', ' Camera Model ') ,('2', '1', ' Nikon D5200 Kit ') ,('1', '2', 'Lens Mount') ,('2', '2', 'Nikon F Bayonet Mount') ,('1', '3', 'Image Sensor') ,('2', '3', '') ,('1', '4', 'NFC Enabled') ,('2', '4', 'No') ,('1', '5', 'Sensor Type') ,('2', '5', 'CMOS') ,('1', '6', 'Sensor Size Format') ,('2', '6', 'DX') ,('1', '7', 'Effective Pixels') ,('2', '7', '24.1 MP') ,('1', '8', 'Total Pixels') ,('2', '8', '24.71 MP') ,('1', '9', 'Colour Filter System') ,('2', '9', 'Yes') ,('1', '10', 'Colour Space') ,('2', '10', 'Yes') ,('1', '11', 'Dust Reduction') ,('2', '11', 'Yes') ,('1', '12', 'Processor') ,('2', '12', 'EXPEED') ,('1', '13', 'Viewfinder') ,('2', '13', '') ,('1', '14', 'Viewfinder Type') ,('2', '14', 'Eye-Level Pentamirror Single-Lens Reflex Viewfinder') ,('1', '15', 'Effective Magnification') ,('2', '15', '0.78x (Approx.)') ,('1', '16', 'Diopter Adjustment') ,('2', '16', '') ,('1', '17', 'LCD Features') ,('2', '17', '') ,('1', '18', 'LCD Size') ,('2', '18', '3 in') ,('1', '19', 'LCD Resolution') ,('2', '19', '921,000 Dots') ,('1', '20', 'Swivel LCD') ,('2', '20', 'Yes') ,('1', '21', 'Live Preview') ,('2', '21', 'Yes') ,('1', '22', 'Auto Focus') ,('2', '22', '') ,('1', '23', 'AF Type') ,('2', '23', '9, 21 or 39 point Dynamic-area AF; Auto-area AF; Single-point AF; 3D-tracking (39 points)') ,('1', '24', 'Focusing Modes 1') ,('2', '24', 'Auto AF-S/AF-C selection (AF-A); Continuous-servo (AF-C); Face-Priority AF available in Live View only and D-Movie only; Full-time Servo (AF-A) available in Live View only and D-Movie') ,('1', '25', 'Focusing Modes 2') ,('2', '25', 'Manual (M) with electronic rangefinder; Normal area; Single-servo AF (AF-S); Wide Area') ,('1', '26', 'AF Points') ,('2', '26', '39') ,('1', '27', 'Exposure') ,('2', '27', '') ,('1', '28', 'ISO') ,('2', '28', '100 - 6400') ,('1', '29', 'White Balance Settings 1') ,('2', '29', 'Auto; Cloudy; Direct Sunlight; Flash; Fluorescent (7 Types); Incandescent; Preset Manual; Shade') ,('1', '30', 'Auto White Balance') ,('2', '30', 'Yes') ,('1', '31', 'White Balance Bracketing') ,('2', '31', 'Yes') ,('1', '32', 'Exposure Compensation') ,('2', '32', '15 EV in Increments of 1/3 or 1/2 EV') ,('1', '33', 'Shutter') ,('2', '33', '') ,('1', '34', 'Shutter Type') ,('2', '34', 'Electronically Controlled Vertical-Travel Focal-Plane') ,('1', '35', 'Shutter Speeds') ,('2', '35', '1/4000 to 30 sec. in steps of 1/3 or 1/2 EV') ,('1', '36', 'Self-Timer') ,('2', '36', 'Yes') ,('1', '37', 'Drive') ,('2', '37', '') ,('1', '38', 'Flash') ,('2', '38', '') ,('1', '39', 'Built-in Flash Type') ,('2', '39', 'TTL: i-TTL Flash') ,('1', '40', 'Flash Sync') ,('2', '40', 'Yes') ,('1', '41', 'Video') ,('2', '41', '') ,('1', '42', 'Video Output Format') ,('2', '42', 'NTSC') ,('1', '43', 'Movie File Formats') ,('2', '43', 'MOV') ,('1', '44', 'Max Video Resolution-24 fps Minimum') ,('2', '44', '1920 x 1080') ,('1', '45', 'Playback') ,('2', '45', '') ,('1', '46', 'Image Playback Modes 1') ,('2', '46', 'Auto Image Rotation; Full-Frame and Thumbnail (4, 9, or 72 images or calendar); Highlights; Histogram Display; Image Comment; Movie Playback; Movie Slideshow; Playback with Zoom; Slideshow') ,('1', '47', 'Storage & Interface') ,('2', '47', '') ,('1', '48', 'Storage Media') ,('2', '48', 'SD; SDHC; SDXC') ,('1', '49', 'Data Interface') ,('2', '49', 'HDMI Output: Type C Mini-Pin HDMI Connector; Hi-Speed USB; Stereo Microphone Input') ,('1', '50', 'Wi-Fi') ,('2', '50', 'Yes') ,('1', '51', 'NFC') ,('2', '51', 'No') ,('1', '52', 'Bluetooth') ,('2', '52', 'Yes') ,('1', '53', 'Jpeg') ,('2', '53', 'Yes') ,('1', '54', 'Raw') ,('2', '54', 'Yes') ,('1', '55', 'Raw+Jpeg') ,('2', '55', 'Yes') ,('1', '56', 'Guided Shooting Mode') ,('2', '56', 'Yes') ,('1', '57', 'Languages Supported') ,('2', '57', 'Arabic; Brazilian Portuguese; Chinese (Simplified and Traditional); Czech; Danish; Dutch; English; Finnish; French; German; Greek; Hindi; Hungarian; Indonesian; Italian; Japanese; Korean; Norwegian; Polish; Portuguese; Romanian; Russian; Spanish; Swedish; Thai; Turkish; Ukrainian') ,('1', '58', 'Included Lens') ,('2', '58', '') ,('1', '59', 'Lens Frame Colour') ,('2', '59', 'Black') ,('1', '60', 'Lens Range') ,('2', '60', '18-55mm') ,('1', '61', 'Stabilized') ,('2', '61', 'Yes') ,('1', '62', 'Model Number') ,('2', '62', '18-55MM') ,('1', '63', 'Lens Weight') ,('2', '63', '0.35G') ,('1', '64', 'Body Features') ,('2', '64', '') ,('1', '65', 'Stabilized Body') ,('2', '65', 'Yes') ,('1', '66', 'Body Colour') ,('2', '66', 'Black') ,('1', '67', 'Intelligent Shoe') ,('2', '67', 'Yes') ,('1', '68', 'Cable Release') ,('2', '68', 'Yes') ,('1', '69', 'Weather Sealed') ,('2', '69', 'No') ,('1', '70', 'Power') ,('2', '70', '') ,('1', '71', 'Battery Type') ,('2', '71', '1 x EN-EL14a Rechargeable Li-ion Battery; EN-EL14 Rechargeable Li-ion Battery') ,('1', '72', 'Power Saving Modes') ,('2', '72', 'EN-EL14') ,('1', '73', 'Physical Features') ,('2', '73', '') ,('1', '74', 'Width') ,('2', '74', '12.9 cm') ,('1', '75', 'Height') ,('2', '75', '3.9 cm') ,('1', '76', 'Depth') ,('2', '76', '7.8 cm') ,('1', '77', 'Weight') ,('2', '77', '505 g') ,('1', '78', u"What's in the Box") ,('2', '78', '') ,('1', '79', 'Warranty Labour') ,('2', '79', '180 Day(s)') ,('1', '80', 'Warranty Parts') ,('2', '80', '180 Day(s)') ] ]        
    #DesktopWeb.BuiltInFunctions.Go_To_Link('http://qa-factory.assetscience.com/totalanalysis/devicesearch/list')
    #DesktopWeb.BuiltInFunctions.Login_To_Application('rrakin', 'password', 'username', 'password', 'submit')
    DesktopWeb.BuiltInFunctions.Validate_Table(step_data)

def Test_For_Compare_Text():
    #step_data_text = [ [ ( 'text','Drones' , False , False ) ] , [ ( 'id' , 'header_lstCategories_category_1' , False , False ) , ( 'class' , 'B' , False , False ) ] ]
    #step_data_new = [ [ ( 'current_page' , 'current_page' , False , False ) , ( 'expected text' , 'full match' , 'Henrys - Photo - Video - Digital' , False , False ) ] ]
    step_data_element = [ [ ( 'id' , 'header-nav-custcare' , False , False ) , ( 'validate partial text' , 'action' , 'Customer Care' , False , False ) ] ]
    DesktopWeb.BuiltInFunctions.Go_To_Link('https://www.henrys.com')
    DesktopWeb.BuiltInFunctions.Validate_Text(step_data_element)

Create_Site_Content()
