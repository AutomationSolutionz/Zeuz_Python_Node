import os
import subprocess
import base64
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

ADB_PATH = "adb"  # Ensure ADB is in PATH
UI_XML_PATH = "ui.xml"
SCREENSHOT_PATH = "screen.png"

router = APIRouter(prefix="/mac", tags=["mac"])

class DumpDriverResponse(BaseModel):
    """Response model for the /dump/driver endpoint."""

    status: Literal["ok", "error", "not_found"] = "ok"
    ui_xml: str | None = None
    error: str | None = None

@router.get("/dump/driver")
def dump_driver():
    """Dump the current driver."""
    try:
        from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium.BuiltInFunctions import appium_driver
        if appium_driver is None:
            result = DumpDriverResponse(status="not_found", error="No driver found")
        else:
            result = DumpDriverResponse(status="ok", ui_xml=appium_driver.page_source)
        return result
    except Exception as e:
        return DumpDriverResponse(status="error", error=str(e))
