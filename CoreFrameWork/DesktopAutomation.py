__author__ = 'asci'
import pyautogui as gui

def locateCenter(file_name):
    return gui.locateCenterOnScreen(file_name)

def clickOnScreen(x,y):
    return gui.click(x,y)

def doubleClickOnScreen(x,y):
    return gui.doubleClick(x,y)

def ifOnScreen(x,y):
    return gui.onScreen(x,y)

def typeText(userText,interval=1):
    gui.typewrite(userText,interval)