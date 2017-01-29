'''
@author: Automation Solutionz
'''
import sys
import os
import time

sys.path.append(os.path.dirname(os.getcwd()))
from Projects.Amazon_test import Amazon as amazon

def Search_In_Amazon_Test_Case():
    amazon.BuiltInFunctions.Open_Browser('Chrome')
    amazon.BuiltInFunctions.Go_To_Link('https://www.amazon.ca/')
    time.sleep(5)
    amazon.Item_Search('Camera')
    time.sleep(5)
    amazon.BuiltInFunctions.Tear_Down()

def Add_To_Cart_Amazon_Test_Case():
    amazon.BuiltInFunctions.Open_Browser('Chrome')
    amazon.BuiltInFunctions.Go_To_Link('https://www.amazon.ca/')
    time.sleep(5)
    amazon.Add_to_Cart('Camera')
    time.sleep(5)
    amazon.BuiltInFunctions.Tear_Down()

if __name__ == '__main__':
    #Test Case 1
    #Search_In_Amazon_Test_Case()

    #Test Case 2
    Add_To_Cart_Amazon_Test_Case()