'''
Created on May 16, 2016

@author: hossa
'''
from Drivers import AutoData
from Drivers import Built_In_Selenium_Web as s
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions as bf
from Projects.AutoData import Browser_Functions as ad



def chek_nissan_adv_tag ():    
    bf.Open_Browser('Firefox')
    bf.Go_To_Link('http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0')
    ad.check_nissan_adv_tag([('tag','Recommended fuel',False,False)])
    bf.Tear_Down()

def lock_unlock_car():
    bf.Open_Browser('Firefox')
    bf.Go_To_Link('http://compare.nissanusa.com/nissan_compare/NNAComparator/Compare.jsp?clientID=273266&modelName=z&#params:main=competitorselect~acode=XGC60NIC041A0')    
    ad.lock_unlock_car(2)
    bf.Tear_Down()    


lock_unlock_car()