from pynput import mouse
import pyautogui as gui
from pathlib import Path
import os
import time
from PIL import Image
import json
import argparse


mouse_click_counter = 0
coords = []

# function to get the coordinate once a right click occurs and append them in the coords list
def on_click(x, y, button, pressed):
    global mouse_click_counter, coords
    if pressed:
         if button == mouse.Button.right:
            mouse_click_counter += 1
            coords.append([x,y])
            print(f"Mouse clicked at ({x}, {y})")


# function to take a screenshot according to the coordinates and save the image
def take_partial_screenshot(left, top, right, bottom, path=None):
    if path is None:
        home_path = str(Path.home())
        downloads_folder = os.path.join(home_path, "Downloads")
        file_format = "%Y_%m_%d_%H-%M-%S"
        file_name = time.strftime(file_format) + ".png"
        if os.path.exists(downloads_folder):
            path = os.path.join(downloads_folder, file_name)
    gui.screenshot(path)
    im = Image.open(path)
    im1 = im.crop((left, top, right, bottom))
    im1.save(path)
    return path


def main(name, path=None):
    try:
        global coords
        mouse_listener = None

        parser = argparse.ArgumentParser()
        parser.add_argument("name", type=str, help="Enter the name of the tester")
        parser.add_argument("--path", type=str, help="The path to folder where the image will be saved. Example E:\Automations Solutionz\GeoSoftware\image1.png. Default is the Download folder")

        print("The program has started...")
        print("Click the Right mouse button on the top-left point of the screen which will be the starting point of the screenshot")
        print("Click the Right mouse button on the bottom-right point of the screen which will be the end point of the screenshot")
        print("If no --path parameter is provided the image will be saved in the Download folder")

        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()
        while mouse_click_counter < 2:
            pass
        mouse_listener.stop()
        
        left = coords[0][0]
        top = coords[0][1]
        right = coords[1][0]
        bottom = coords[1][1]
        attachment_path = take_partial_screenshot(left, top, right, bottom, path)

        data = {
            name:{
                "coords": [left, top, right-left, bottom-top],
                "attachment_path": attachment_path
            }
        }
        json_str = json.dumps(data, indent=4)
        print(json_str)
    except Exception as e:
        if mouse_listener:
            mouse_listener.stop()
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Enter the name of the tester")
    parser.add_argument("--path", type=str, help="The path to folder where the image will be saved. Example E:\Automations Solutionz\GeoSoftware\image1.png. Default is the Download folder")
    args = parser.parse_args()
    main(args.name, args.path)