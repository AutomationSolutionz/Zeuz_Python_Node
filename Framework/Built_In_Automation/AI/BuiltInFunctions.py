import sys, os, inspect
from pathlib import Path
import base64
from io import BytesIO

sys.path.append("..")
from selenium import webdriver

from Framework.Utilities import CommonUtil, ConfigModule
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Utilities.decorators import logger

try:
    import pyautogui
except:
    pyautogui = None

try:
    from PIL import Image
except:
    Image = None

MODULE_NAME = inspect.getmodulename(__file__)

StepDataType = list[list[str, str, str]]
ReturnType = "passed" | "zeuz_failed"

temp_config = os.path.join(
    os.path.join(
        os.path.abspath(__file__).split("Framework")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)

@logger
def natural_language_action(step_data: StepDataType) -> ReturnType:
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    
    
    images = []
    texts = []
    action_type = ""
    var_name = ""
    instruction = ""
    
    try:
        for left, mid, right in step_data:
            left_lower = left.lower().strip()
            mid_lower = mid.lower().strip()
            right_stripped = right.strip()
            
            if left_lower == "image":
                if right_stripped == "selenium_screenshot":
                    if Shared_Resources.Test_Shared_Variables("selenium_driver"):
                        selenium_driver = Shared_Resources.Get_Shared_Variables("selenium_driver")
                    else:
                        selenium_driver = None
                    if selenium_driver:
                        screenshot = selenium_driver.get_screenshot_as_png()
                        images.append({
                            "type": "selenium_screenshot",
                            "data": base64.b64encode(screenshot).decode('utf-8')
                        })
                        CommonUtil.ExecLog(sModuleInfo, "Captured Selenium screenshot", 1)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Selenium driver not available", 2)
                
                elif right_stripped == "desktop_screenshot":
                    if pyautogui and Image:
                        try:
                            screenshot = pyautogui.screenshot()
                            buffered = BytesIO()
                            screenshot.save(buffered, format="PNG")
                            img_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            images.append({
                                "type": "pyautogui_screenshot",
                                "data": img_data
                            })
                            CommonUtil.ExecLog(sModuleInfo, "Captured PyAutoGUI screenshot", 1)
                        except Exception as e:
                            CommonUtil.ExecLog(
                                sModuleInfo, 
                                f"Failed to capture desktop screenshot (headless environment?): {str(e)}", 
                                2
                            )
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "PyAutoGUI not available", 2)
                else:
                    image_path = CommonUtil.path_parser(right_stripped)
                    if os.path.exists(image_path):
                        with open(image_path, "rb") as image_file:
                            image_data = image_file.read()
                            images.append({
                                "type": "image",
                                "data": base64.b64encode(image_data).decode('utf-8')
                            })
                    else:
                        CommonUtil.ExecLog(sModuleInfo, f"Image file not found: {image_path}", 2)
                    images.append({
                        "type": "image",
                        "data": right_stripped
                    })
            elif left_lower == "text":
                if right_stripped == "selenium_dom":
                    if selenium_driver:
                        dom = Shared_Resources.get_cleaned_selenium_dom(selenium_driver)
                        if dom:
                            texts.append({
                                "type": "dom",
                                "data": dom
                            })
                        else:
                            CommonUtil.ExecLog(sModuleInfo, "Failed to capture cleaned DOM", 2)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Selenium driver not available for DOM", 2)

                else:
                    texts.append({
                        "type": "text",
                        "data": right_stripped
                    })
            
            elif left_lower == "action":
                action_type = right_stripped
            
            elif left_lower == "natural language action":
                var_name = right_stripped
        
        result_data = {
            "images": images,
            "texts": texts,
            "action": action_type,
            "instruction": instruction
        }
        
        payload_dir = Path(__file__).parent / "payload"
        payload_dir.mkdir(exist_ok=True)
        
        for img in images:
            if img["type"] == "selenium_screenshot":
                img_path = payload_dir / "selenium_screenshot.png"
                img_bytes = base64.b64decode(img["data"])
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
                CommonUtil.ExecLog(sModuleInfo, f"Saved selenium screenshot to {img_path}", 1)
        
        for text in texts:
            if text["type"] == "dom":
                dom_path = payload_dir / "selenium_dom.txt"
                with open(dom_path, "w", encoding="utf-8") as f:
                    f.write(text["data"])
                CommonUtil.ExecLog(sModuleInfo, f"Saved selenium DOM to {dom_path}", 1)
        
        text_counter = 1
        for text in texts:
            if text["type"] == "text":
                text_path = payload_dir / f"text{text_counter}.txt"
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(text["data"])
                CommonUtil.ExecLog(sModuleInfo, f"Saved text to {text_path}", 1)
                text_counter += 1
        
        image_counter = 1
        for img in images:
            if img["type"] in ["image", "pyautogui_screenshot"]:
                img_path = payload_dir / f"image{image_counter}.png"
                img_bytes = base64.b64decode(img["data"])
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
                CommonUtil.ExecLog(sModuleInfo, f"Saved image to {img_path}", 1)
                image_counter += 1
        
        CommonUtil.ExecLog(
            sModuleInfo,
            f"Natural language action executed with {len(images)} images, {len(texts)} texts",
            1
        )
        
        return Shared_Resources.Set_Shared_Variables(var_name, result_data)
        
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def switch_iframe(step_data: StepDataType) -> ReturnType:
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    
    try:
        selenium_driver = Shared_Resources.Get_Shared_Variables("selenium_driver")
    except:
        selenium_driver = None
    
    try:
        for left, mid, right in step_data:
            left = left.lower().strip()
            if "action" in mid.lower() and left == "switch iframe":
                pass
            elif left == "index" and "default" in right.lower():
                if selenium_driver:
                    selenium_driver.switch_to.default_content()
                    CommonUtil.ExecLog(
                        sModuleInfo, "Exited all iframes and switched to default content", 1
                    )
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

