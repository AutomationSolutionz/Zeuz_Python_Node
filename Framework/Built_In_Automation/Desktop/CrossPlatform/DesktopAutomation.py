# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import pyautogui as gui
import numpy as np
import imutils
import glob
import cv2
import os
from Framework.Utilities import CommonUtil
from Framework.Utilities import FileUtilities as FL

def locateCenter(file_name):
    try:
        x = gui.locateCenterOnScreen(str(file_name))[0]
        y = gui.locateCenterOnScreen(str(file_name))[1]
        return x,y
    except Exception, e:
        return "Failed"

def clickOnScreen(x,y):
    return gui.click(x,y)

def doubleClickOnScreen(x,y):
    return gui.doubleClick(x,y)

def ifOnScreen(x,y):
    return gui.onScreen(x,y)

def typeText(userText,interval=1):
    gui.typewrite(userText,interval)

#temp_fix
def type_text(userText):
    typeText(userText)

def getCenter(logo):
    template = cv2.imread(logo)
    # template = cv2.imread(args["template"])
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 50, 200)
    (tH, tW) = template.shape[:2]
    #cv2.imshow("Template", template)

    image_folder = FL.get_home_folder() + '/Desktop/AutomationLog/PyAutoGuiScreenShots/'
    ImageName = 'opencv'
    full_location = image_folder + os.sep + CommonUtil.TimeStamp("utc") + "_" + ImageName + '.png'
    #os.system("import -window root -delay 2000 %s" % full_location)
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    gui.screenshot(full_location)

    # loop over the images to find the template in
    for imagePath in glob.glob(full_location):
        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        image = cv2.imread(imagePath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = None

        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # check to see if the iteration should be visualized

            # draw a bounding box around the detected region
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                          (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            #cv2.imshow("Visualize", clone)
            cv2.waitKey(0)

            # if we have found a new maximum correlation value, then ipdate
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        # unpack the bookkeeping varaible and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        # draw a bounding box around the detected result and display the image
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        #cv2.imshow("Image", image)
        x = (startX + endX) / 2
        y = (startY + endY) / 2
        return x,y



def click(logo, num_of_clicks=1):

    try:
        result = locateCenter(logo)
        if result == 'Failed':
            x,y = getCenter(logo)
        else:
            print 'pyautogui'
            x,y =result

        if x and y:
            if num_of_clicks == 1:
                return clickOnScreen(x, y)
            elif num_of_clicks == 2:
                return doubleClickOnScreen(x, y)

        return "Failed"

    except Exception, e:
        return "Failed"

'''def main():
    click('/home/batman/Desktop/Untitled Folder/template4.png',1)




if __name__ == '__main__':
    main()'''
