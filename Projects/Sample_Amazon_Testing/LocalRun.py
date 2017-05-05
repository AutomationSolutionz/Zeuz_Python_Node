'''
@author: Automation Solutionz
'''
import sys
import os
import time

sys.path.append(os.path.dirname(os.getcwd()))
from Projects.Sample_Amazon_Testing import Amazon as amazon


web_link_step = [ [ ( 'web_page' , '' , 'http://amazon.ca' , False , False , '' ) ] ]
dependency = {'Browser': 'chrome'}



def Search_In_Amazon_Test_Case():
    amazon.BuiltInFunctions.Open_Browser(dependency)
    amazon.BuiltInFunctions.Go_To_Link(web_link_step)
    time.sleep(5)
    amazon.Item_Search('Camera')
    time.sleep(5)
    amazon.BuiltInFunctions.Tear_Down()

def Add_To_Cart_Amazon_Test_Case():
    amazon.BuiltInFunctions.Open_Browser(dependency)
    amazon.BuiltInFunctions.Go_To_Link(web_link_step)
    time.sleep(5)
    amazon.Add_to_Cart('Camera')
    time.sleep(5)
    amazon.BuiltInFunctions.Tear_Down()


Search_In_Amazon_Test_Case()

    #Test Case 2
    #Add_To_Cart_Amazon_Test_Case()