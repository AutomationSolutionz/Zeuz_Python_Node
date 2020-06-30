# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
@author: Automation Solutionz
'''
import sys
import os
import time

sys.path.append(os.path.dirname(os.getcwd()))
from Projects.Sample_Amazon_Testing import Amazon as amazon
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as Sequential_Actions


web_link_step = [ ( 'web_page' , '' , 'http://amazon.ca' , False , False , '' ) ]
dependency = {'Browser': 'chrome'}



def Search_In_Amazon_Test_Case():
    amazon.BuiltInFunctions.Open_Browser(dependency)
    amazon.BuiltInFunctions.Go_To_Link(web_link_step)
    time.sleep(5)
    amazon.Item_Search('Camera')
    time.sleep(5)
    amazon.BuiltInFunctions.Tear_Down_Selenium()

def Add_To_Cart_Amazon_Test_Case():
    amazon.BuiltInFunctions.Open_Browser(dependency)
    amazon.BuiltInFunctions.Go_To_Link(web_link_step)
    time.sleep(5)
    amazon.Add_to_Cart('Camera')
    time.sleep(5)
    amazon.BuiltInFunctions.Tear_Down_Selenium()

def Add_To_Cart_Amazon_Test_Case_With_New_Seq_Actions():
    Dataset = [
        [
            ['open browser','selenium action','%|Browser|%',False,False]
        ],
        [
            ['go to link', 'selenium action', 'http://amazon.ca', False, False]
        ],
        [
            ['id', 'element parameter', 'twotabsearchtextbox', False, False],
            ['text', 'selenium action', 'Camera', False, False]
        ],
        [
            ['sleep', 'selenium action', '3', False, False]
        ]
        ,
        [
            ['value', 'element parameter', 'Go', False, False],
            ['click', 'selenium action', 'click', False, False]
        ],
        [
            ['sleep', 'selenium action', '3', False, False]
        ],
        [
            ['tag', 'element parameter', 'a', False, False],
            ['class', 'reference parameter', 's-item-container', False, False],
            ['relation', 'relation type', 'parent', False, False],
            ['click', 'selenium action', 'click', False, False]
        ],
        [
            ['sleep', 'selenium action', '3', False, False]
        ],
        [
            ['id', 'element parameter', 'add-to-cart-button', False, False],
            ['click', 'selenium action', 'click', False, False]
        ],
        [
            ['sleep', 'selenium action', '3', False, False]
        ],
        [
            ['tear down browser', 'selenium action', '', False, False]
        ]
    ]
    Sequential_Actions.Sequential_Actions(Dataset,{'Browser': 'chrome'})



if __name__ == '__main__':
    #Test Case 1
    #Search_In_Amazon_Test_Case()
    #Test Case 2
    #Add_To_Cart_Amazon_Test_Case()
    #Test Case 3 with new seq actions
    Add_To_Cart_Amazon_Test_Case_With_New_Seq_Actions()
