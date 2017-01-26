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
    time.sleep(10)
    amazon.Item_Search('Camera')
    time.sleep(10)
    amazon.BuiltInFunctions.Tear_Down()

if __name__ == '__main__':
    Search_In_Amazon_Test_Case()