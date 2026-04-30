import os, requests
import re
import json
import subprocess
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw

ADB_PATH = "adb"  # Ensure ADB is in PATH
LOGO_PATH = "zeuzlogo.png"  # Logo file in the same directory as the script
SCREENSHOT_PATH = "screen.png"
UI_XML_PATH = "ui.xml"


def run_adb_command(command):
    """Run an ADB command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


def capture_ui_dump():
    """Capture the current UI hierarchy from the device and take a screenshot."""
    xml_saved = False
    appium_driver = None
    try:
        from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as Shared_Resources
        appium_driver = Shared_Resources.Get_Shared_Variables("appium_driver", log=False)
        if appium_driver is not None:
            page_src = appium_driver.page_source
            with open(UI_XML_PATH, "w") as xml_file:
                xml_file.write(page_src)
            xml_saved = True
    except Exception:
        pass
    # even if it fails don't try adb if appium driver is available
    if not xml_saved and appium_driver is None:
        run_adb_command(f"{ADB_PATH} shell uiautomator dump /sdcard/ui.xml")
        run_adb_command(f"{ADB_PATH} pull /sdcard/ui.xml {UI_XML_PATH}")

    run_adb_command(f"{ADB_PATH} shell screencap -p /sdcard/screen.png")
    run_adb_command(f"{ADB_PATH} pull /sdcard/screen.png {SCREENSHOT_PATH}")
    update_treeview()
    update_screenshot(None)


def update_treeview():
    """Update the UI element tree."""
    global elements_map  # Use a global variable to store the mapping of bounds to treeview items
    elements_map = {}  # Reset the mapping
    elements = parse_ui_xml(UI_XML_PATH)
    tree.delete(*tree.get_children())
    flat_tree.delete(*flat_tree.get_children())
    populate_treeview(tree, "", elements)
    populate_flat_treeview(flat_tree, elements)


def populate_treeview(tree, parent, elements):
    """Recursively populate the treeview with hierarchical data."""
    for element in elements:
        # Build the node text dynamically based on available fields
        node_text_parts = [element['class']]
        if element['resource-id']:
            node_text_parts.append(f"ID: {element['resource-id']}")
        if element['text']:
            node_text_parts.append(f"Text: {element['text']}")
        node_text_parts.append(f"Bounds: {element['bounds']}")  # Always include bounds
        node_text = " - ".join(node_text_parts)

        # Insert the item into the treeview and tag it with the individual XML string
        node_id = tree.insert(parent, "end", text=node_text, tags=(element["xml"],))
        if element["bounds"]:  # Only map valid bounds
            elements_map[element["bounds"]] = node_id  # Map bounds to treeview item ID
        if "children" in element:
            populate_treeview(tree, node_id, element["children"])


def populate_flat_treeview(tree, elements):
    """Populate the flat treeview with all elements in a tabular format."""
    for element in elements:
        # Extract the required fields for the flat view
        class_name = element['class']
        resource_id = element['resource-id']
        text = element['text']

        # Add clickable/editable status to the flat view
        clickable = "Yes" if element.get('clickable') == "true" else "No"
        editable = "Yes" if element.get('editable') == "true" else "No"

        # Insert the item into the flat treeview
        tree.insert("", "end", values=(class_name, resource_id, text, clickable, editable), tags=(element["xml"],))
        if element["bounds"]:  # Only map valid bounds
            elements_map[element["bounds"]] = tree.get_children()[-1]  # Map bounds to treeview item ID
        if "children" in element:
            populate_flat_treeview(tree, element["children"])


def parse_ui_xml(xml_file):
    """Parse the UI XML and extract elements in a hierarchical structure."""
    if not os.path.exists(xml_file):
        return []
    tree_xml = ET.parse(xml_file)
    root = tree_xml.getroot()

    def extract_elements(node):
        # Create a shallow copy of the node (without children)
        shallow_node = ET.Element(node.tag, attrib=node.attrib)
        element = {
            "class": node.attrib.get("class", "Unknown"),
            "resource-id": node.attrib.get("resource-id", ""),
            "text": node.attrib.get("text", ""),
            "bounds": node.attrib.get("bounds", ""),  # Extract bounds attribute
            "clickable": node.attrib.get("clickable", "false"),
            "editable": node.attrib.get("editable", "false"),
            "xml": ET.tostring(shallow_node, encoding="unicode"),  # Store the XML of the individual node (no children)
            "children": []
        }
        for child in node:
            element["children"].append(extract_elements(child))
        return element

    return [extract_elements(root)]


def generate_zeuz_action(element_xml, action_type, action_value="Sample Text"):
    """
    Generate a Zeuz action in the required format.
    :param element_xml: The XML string of the selected element.
    :param action_type: The type of action to perform (e.g., "text", "click").
    :param action_value: The value associated with the action (e.g., "John", "click").
    :return: A Zeuz action in the required format (JSON with double quotes).
    """
    # Parse the XML to extract attributes using regex
    element = {}
    pattern = r'([\w:.]+)="([^"]*)"'
    matches = re.findall(pattern, element_xml)
    
    # Debugging: Print all parsed attributes
    print("Parsed Attributes:", matches)
    
    for key, value in matches:
        element[key] = value

    # Debugging: Print the final parsed dictionary
    print("Final Parsed Element:", element)

    # Determine the locator type and value
    if element.get("resource-id") or element.get("id"):
        locator_type = "resource-id"  # Always use "resource-id" as the locator type
        raw_locator_value = element.get("resource-id", element.get("id"))  # Use "id" as fallback
        
        # Clean up the locator value: Extract the part after the last slash
        locator_value = raw_locator_value.split("/")[-1]
    elif element.get("text"):
        locator_type = "text"
        locator_value = element["text"]  # Preserve the full text
    else:
        raise ValueError("Element must have either 'resource-id', 'id', or 'text' to generate an action.")

    # Set the action value based on the action type
    if action_type == "click":
        action_value = "click"

    # Construct the Zeuz action
    zeuz_action = [
        {
            "action_name": "None",
            "action_disabled": "false",
            "step_actions": [
                [locator_type, "element parameter", locator_value],
                [action_type, "appium action", action_value]
            ]
        }
    ]

    # Return the action as a JSON-formatted string with double quotes
    return json.dumps(zeuz_action)


def copy_zeuz_action():
    """Generate and copy the Zeuz action for the selected element."""
    selected_item = tree.selection() if view_mode.get() == "tree" else flat_tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select an element first.")
        return

    # Retrieve the full XML of the selected element
    full_xml = tree.item(selected_item, "tags")[0] if view_mode.get() == "tree" else flat_tree.item(selected_item, "tags")[0]

    # Get the selected action from the dropdown
    action_type = action_var.get()
    action_value = "Sample Text" if action_type == "text" else "click"

    # Generate the Zeuz action using the full XML
    try:
        zeuz_action = generate_zeuz_action(full_xml, action_type, action_value)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Copy the action to the clipboard
    root.clipboard_clear()
    root.clipboard_append(str(zeuz_action))
    root.update()  # Ensure the clipboard is updated

    # Display a confirmation message
    messagebox.showinfo("Action Copied", "Zeuz action copied to clipboard!")


def toggle_view():
    """Toggle between tree view and flat view."""
    if view_mode.get() == "tree":
        tree_frame.pack_forget()  # Hide tree view
        flat_tree_frame.pack(fill="both", expand=True)  # Show flat view
        view_mode.set("flat")
    else:
        flat_tree_frame.pack_forget()  # Hide flat view
        tree_frame.pack(fill="both", expand=True)  # Show tree view
        view_mode.set("tree")
    update_screenshot(None)

def find_matching_element(root, selected_element) -> bool:
    """Find an element in `root` that matches `selected_element` by tag, attributes, and text."""
    tag = selected_element.tag
    attribs = selected_element.attrib
    text = (selected_element.text or "").strip()

    # Iterate through all elements with the same tag in root
    for elem in root.iter(tag):
        if elem.attrib == attribs and (elem.text or "").strip() == text:
            elem.set("zeuz", "aiplugin")
            return True

    return False


def read_settings_conf():
    """Read settings from the Framework/settings.conf file."""
    try:
        import configparser
        import os
        
        # Get the current file's directory and navigate to Framework/settings.conf
        current_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'Framework', 'settings.conf')
        
        config = configparser.ConfigParser()
        config.read(settings_path)
        api_key = config.get('Authentication', 'api-key').strip()
        server_address = config.get('Authentication', 'server_address').strip()
        url = server_address + "/" if server_address[-1] != "/" else server_address
        return {
            'api_key': api_key,
            'url': url
        }
    except Exception as e:
        print(f"Error reading settings.conf: {str(e)}")
        return {'api_key': '', 'url': ''}

def send_to_zeuz():
    """Send the inspected Element and UI hierarchy to Zeuz."""
    selected_item = tree.selection() if view_mode.get() == "tree" else flat_tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select an element first.")
        return

    try:
        # Read settings
        settings = read_settings_conf()
        if not settings['api_key'] or not settings['url']:
            messagebox.showerror("Configuration Error", "API key or server address not found in settings.conf")
            return

        # Read the original UI XML file
        tree_xml = ET.parse(UI_XML_PATH)
        root = tree_xml.getroot()
        
        # Get the XML string of the selected element
        selected_xml = tree.item(selected_item, "tags")[0] if view_mode.get() == "tree" else flat_tree.item(selected_item, "tags")[0]
        
        # Create an ElementTree from the selected XML string
        selected_element = ET.fromstring(selected_xml)
        find_matching_element(root, selected_element)
        
        # Convert the modified XML tree to string
        modified_xml_string = ET.tostring(root, encoding='unicode')
        
        print("\n\n------------- Modified XML -------------------")
        print(modified_xml_string)
        print("---------------------------------------------\n\n")
        # Send the request to Zeuz server
        headers = {
            "X-Api-Key": settings['api_key'],
        }
        content = json.dumps({
            'page_src': modified_xml_string,
            "action_type": "android",
        })
        response = requests.post(
            f"{settings['url']}ai_record_single_action/",
            headers=headers,
            data=content,
            verify=False
        )
        
        if response.status_code == 200:
            messagebox.showinfo("Success", "Successfully sent to Zeuz!")
        else:
            messagebox.showerror("Error", f"Failed to send data: {response.text}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process UI hierarchy: {str(e)}")


def update_screenshot(event=None):
    """Update and highlight only the selected element in the screenshot."""
    if os.path.exists(SCREENSHOT_PATH):
        img = Image.open(SCREENSHOT_PATH)
        draw = ImageDraw.Draw(img)
        selected_item = tree.selection() if view_mode.get() == "tree" else flat_tree.selection()
        if selected_item:
            # Retrieve the full XML of the selected element
            full_xml = tree.item(selected_item, "tags")[0] if view_mode.get() == "tree" else flat_tree.item(selected_item, "tags")[0]

            # Extract bounds from the full XML
            bounds = extract_bounds_from_xml(full_xml)
            coords = extract_coordinates(bounds) if bounds else None
            if coords:
                x1, y1, x2, y2 = coords
                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

            # Display the full XML content in the bottom panel
            full_text_label.delete(1.0, tk.END)  # Clear previous content
            full_text_label.insert(tk.END, full_xml)  # Insert new content

        img.thumbnail((500, 500))  # Resize the image for display
        img = ImageTk.PhotoImage(img)
        screenshot_label.config(image=img)
        screenshot_label.image = img


def extract_bounds_from_xml(xml_string):
    """Extract the bounds attribute from the full XML string."""
    start = xml_string.find('bounds="') + len('bounds="')
    end = xml_string.find('"', start)
    return xml_string[start:end] if start != -1 and end != -1 else None


def extract_coordinates(bounds):
    """Extract x1, y1, x2, y2 coordinates from the bounds string."""
    if not bounds:
        return None
    parts = bounds.replace("[", "").replace("]", ",").split(",")
    try:
        return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    except (ValueError, IndexError):
        return None


def on_image_click(event):
    """Handle clicks on the screenshot image."""
    if not os.path.exists(SCREENSHOT_PATH):
        return
    img = Image.open(SCREENSHOT_PATH)
    img_width, img_height = img.size
    thumbnail_width, thumbnail_height = 500, 500  # Thumbnail size
    scale_x = img_width / thumbnail_width
    scale_y = img_height / thumbnail_height

    # Scale the click coordinates back to the original image dimensions
    x = int(event.x * scale_x)
    y = int(event.y * scale_y)

    # Find the deepest child element whose bounds contain the click coordinates
    selected_item = None
    for bounds, item_id in reversed(list(elements_map.items())):  # Reverse to prioritize child nodes
        coords = extract_coordinates(bounds)
        if coords and coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
            selected_item = item_id
            break

    if selected_item:
        # Highlight the corresponding treeview item
        tree.selection_set(selected_item) if view_mode.get() == "tree" else flat_tree.selection_set(selected_item)
        tree.see(selected_item) if view_mode.get() == "tree" else flat_tree.see(selected_item)
        update_screenshot()


def tap_element():
    """Tap on a selected UI element using ADB coordinates."""
    selected_item = tree.selection() if view_mode.get() == "tree" else flat_tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select an element first.")
        return

    # Retrieve the full XML of the selected element
    full_xml = tree.item(selected_item, "tags")[0] if view_mode.get() == "tree" else flat_tree.item(selected_item, "tags")[0]

    # Extract bounds from the full XML
    bounds = extract_bounds_from_xml(full_xml)
    coords = extract_coordinates(bounds) if bounds else None
    if coords:
        x, y = (coords[0] + coords[2]) // 2, (coords[1] + coords[3]) // 2
        run_adb_command(f"{ADB_PATH} shell input tap {x} {y}")
        messagebox.showinfo("Tap Successful", f"Tapped at coordinates ({x}, {y})")


# GUI Setup
root = tk.Tk()
root.title("ZeuZ Android Inspector")
root.geometry("1200x800")  # Increased vertical size
root.configure(bg="#1E1E1E")

if os.path.exists(LOGO_PATH):
    logo_image = Image.open(LOGO_PATH)
    logo_image.thumbnail((100, 100))
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo, bg="#1E1E1E")
    logo_label.image = logo_photo
    logo_label.pack(side="top", pady=10)

main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = ttk.Frame(main_frame)
left_frame.pack(side="left", fill="both", expand=True, padx=10)

# Button Frame for Horizontal Layout
button_frame = ttk.Frame(left_frame)
button_frame.pack(fill="x", pady=5)

btn_capture = ttk.Button(button_frame, text="Capture UI", command=capture_ui_dump)
btn_capture.pack(side="left", padx=5)

btn_tap = ttk.Button(button_frame, text="Tap Element", command=tap_element)
btn_tap.pack(side="left", padx=5)

btn_toggle_view = ttk.Button(button_frame, text="Toggle View", command=toggle_view)
btn_toggle_view.pack(side="left", padx=5)

btn_toggle_view = ttk.Button(button_frame, text="Send to Zeuz", command=send_to_zeuz)
btn_toggle_view.pack(side="left", padx=5)

# View mode (Tree or Flat)
view_mode = tk.StringVar(value="tree")

# Treeview (Hierarchical View)
tree_frame = ttk.Frame(left_frame)
tree_frame.pack(fill="both", expand=True)
tree = ttk.Treeview(tree_frame, show="tree")
tree.pack(fill="both", expand=True)
tree.bind("<<TreeviewSelect>>", lambda event: update_screenshot())

# Flat Treeview (Flat View)
flat_tree_frame = ttk.Frame(left_frame)
flat_tree = ttk.Treeview(flat_tree_frame, columns=("Class", "Resource-ID", "Text", "Clickable", "Editable"), show="headings")
flat_tree.heading("Class", text="Class")
flat_tree.heading("Resource-ID", text="Resource-ID")
flat_tree.heading("Text", text="Text")
flat_tree.heading("Clickable", text="Clickable")
flat_tree.heading("Editable", text="Editable")
flat_tree.column("Class", width=200, anchor="w")
flat_tree.column("Resource-ID", width=200, anchor="w")
flat_tree.column("Text", width=400, anchor="w")
flat_tree.column("Clickable", width=80, anchor="center")
flat_tree.column("Editable", width=80, anchor="center")
flat_tree.pack(fill="both", expand=True)
flat_tree.bind("<<TreeviewSelect>>", lambda event: update_screenshot())

# Right Panel (Screenshot Display)
right_frame = ttk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True, pady=5)

screenshot_label = tk.Label(right_frame, bg="#1E1E1E")
screenshot_label.pack()
screenshot_label.bind("<Button-1>", on_image_click)  # Bind left mouse click to the image

# Action Buttons Below the Screenshot
action_frame = ttk.Frame(right_frame)
action_frame.pack(fill="x", pady=5)

# Action Dropdown
action_var = tk.StringVar(value="click")
action_dropdown = ttk.Combobox(action_frame, textvariable=action_var, state="readonly", width=10)
action_dropdown["values"] = ("click", "text")
action_dropdown.pack(side="left", padx=5)

# Copy Zeuz Action Button
btn_copy_action = ttk.Button(action_frame, text="Copy Zeuz Action", command=copy_zeuz_action)
btn_copy_action.pack(side="left", padx=5)

# Bottom Panel (Full Text Display)
bottom_frame = ttk.Frame(root)
bottom_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)

bold_font = ("Arial", 10, "bold")
full_text_label = tk.Text(
    bottom_frame,
    bg="#2E2E2E",
    fg="white",
    relief="groove",
    padx=10,
    pady=5,
    font=bold_font,
    wrap="word",
    height=10  # Increased height for better visibility
)
full_text_label.pack(fill="both", expand=True)

# Start with tree view
tree_frame.pack(fill="both", expand=True)
flat_tree_frame.pack_forget()

# Global variable to store the mapping of bounds to treeview items
elements_map = {}

# Auto-capture UI on startup
capture_ui_dump()

root.mainloop()