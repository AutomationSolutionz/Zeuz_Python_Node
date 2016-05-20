'''
Created on May 16, 2016

@author: hossa
'''
from Drivers import AutoData
from Drivers import Built_In_Selenium_Web as s
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions as bf
from Projects.AutoData import Browser_Functions as ad

import Queue
if __name__=='__main__':
    """"q=Queue.Queue()
    s.open_browser({},{},[[('browser','chrome',False,False)]],{},q)
    s.go_to_webpage({},{},[[('web_link','http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0',False,False)]],{},q)
    AutoData.check_nissan_advantage_tag({},{},[[('tag','Recommended fuel',False,False)]],{},q)
    #open_detail_pop_up({},[[('tag','Body material',False,False),('description','The front bumper is body color.',False,False)]],{},q)
    #car_selection({},[ [ ( 'car 1' , 'model' , 'GT-R Coupe' , False , False ) , ( 'car 1' , 'year' , '2015' , False , False ) , ( 'car 1' , 'version' , 'Premium' , False , False ) , ( 'car 2' , 'year' , '2015' , False , False ) , ( 'car 2' , 'make' , 'Mitsubishi' , False , False ) , ( 'car 2' , 'model' , 'Lancer' , False , False ) , ( 'car 2' , 'trim' , 'SE 4dr 4WD Sedan' , False , False ) ] ],{},q)
    #verify_data({},[[('tag','Pricing',False,False),('tag','Fuel Economy',False,False)]],{},q)
    #lock_car({},[[('car_number',2,False,False)]],{},q)
    #unlock_car({},[[('car_number',2,False,False)]],{},q)
    s.close_browser({},{},[],{},q)"""
    
    bf.Open_Browser('Chrome')
    bf.Go_To_Link('http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0')
    ad.check_nissan_adv_tag([('tag','Recommended fuel',False,False)])
    bf.Tear_Down()
