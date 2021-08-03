import keyboard, autoit, pyautogui
import os, sys

new_line = True
import clr, System

dll_path = os.getcwd().split("Apps")[0] + "Framework" + os.sep + "windows_dll_files" + os.sep
clr.AddReference(dll_path + "UIAutomationClient")
clr.AddReference(dll_path + "UIAutomationTypes")
clr.AddReference(dll_path + "UIAutomationProvider")
clr.AddReference( "System.Windows.Forms")
x, y = 0, 0
from System.Windows.Automation import *

def _found(Element):
    try:
        left = Element.Current.BoundingRectangle.Left
        right = Element.Current.BoundingRectangle.Right
        bottom = Element.Current.BoundingRectangle.Bottom
        top = Element.Current.BoundingRectangle.Top
        if left <= x <= right and top <= y <= bottom:
            return True
        return False
    except Exception:
        print(sys.exc_info())
        return False

def create_index(index_trace: dict, element):
    NameE = element.Current.Name
    ClassE = element.Current.ClassName
    AutomationE = element.Current.AutomationId
    LocalizedControlTypeE = element.Current.LocalizedControlType

    s = 'automationid="%s"' % AutomationE
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'name="%s"' % NameE
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'class="%s"' % ClassE
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if s in index_trace: index_trace[s] += 1
    else: index_trace[s] = 0

def create_path(index_trace: dict, element):
    NameE = element.Current.Name
    ClassE = element.Current.ClassName
    AutomationE = element.Current.AutomationId
    LocalizedControlTypeE = element.Current.LocalizedControlType

    s = 'automationid="%s"' % AutomationE
    if AutomationE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""
    s_name = 'name="%s"' % NameE
    if NameE and s_name not in index_trace:
        return s_name + ">" + "\n" if new_line else ""
    s_name_control = 'name="%s",control="%s"' % (NameE, LocalizedControlTypeE)
    if NameE and LocalizedControlTypeE and s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    s_class = 'class="%s"' % ClassE
    if ClassE and s_class not in index_trace:
        return s_class + ">" + "\n" if new_line else ""
    s = 'name="%s",class="%s"' % (NameE, ClassE)
    if NameE and ClassE and s not in index_trace:
        return s + ">" + "\n" if new_line else ""

    if NameE and s in index_trace:
        return s_name + ">" + ',index="%s">' % (index_trace[s_name] + 1) + "\n" if new_line else ""
    if s_class and s in index_trace:
        return s_class + ">" + ',index="%s">' % (index_trace[s_class] + 1) + "\n" if new_line else ""

    if s_name not in index_trace:
        return s_name + ">" + "\n" if new_line else ""
    if s_name_control not in index_trace:
        return s_name_control + ">" + "\n" if new_line else ""
    return s_name_control + ',index="%s">' % (index_trace[s_name_control] + 1) + "\n" if new_line else ""


def _child_search(ParentElement):
    try:
        path = ""
        child_elements = ParentElement.FindAll(TreeScope.Children, Condition.TrueCondition)
        if child_elements.Count == 0:
            return path

        index_trace = {}
        for each_child in child_elements:
            if _found(each_child):
                path += create_path(index_trace, each_child)
                # path += 'name="%s",control="%s",automationid="%s",class="%s">\n' % (NameE, LocalizedControlTypeE, AutomationE, ClassE)
                temp = _child_search(each_child)
                return path + temp
            create_index(index_trace, each_child)

        return path

    except Exception:
        print(sys.exc_info())
        return ""


def main():
    try:
        global x, y
        while True:
            keyboard.wait("ctrl")
            x, y = pyautogui.position()
            # print(x, y)
            res = _child_search(AutomationElement.RootElement)[:-1] + "\n"
            print(res)
    except:
        print(sys.exc_info())


if __name__ == "__main__":
    main()
