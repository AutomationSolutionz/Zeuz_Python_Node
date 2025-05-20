import threading
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import pyperclip  # Add this import for clipboard functionality

from inspector import WindowsInspector, Authenticate, inspect


class InspectorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZeuZ Windows Inspector GUI")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = int(screen_width * 0.7)
        height = int(screen_height * 0.9)
        x = 0
        y = 0
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.inspector = WindowsInspector()
        self.node_ids = {}  # Dictionary to store node IDs
        self.path_sections = []  # Store path section widgets

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Inspect.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=10)
        self.style.configure('Copy.TButton',
                           font=('Segoe UI', 9),
                           padding=5)

        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tree view section
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.treeview = ttk.Treeview(tree_frame)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=tree_scroll.set)

        # Configure tags for different element types
        self.treeview.tag_configure('highlight', background='lightgreen')  # For selected path
        self.treeview.tag_configure('inspected', background='#90EE90')    # For inspected element (light green)

        # Log section
        log_frame = ttk.LabelFrame(main_container, text="Log Messages")
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        self.log = scrolledtext.ScrolledText(log_frame, height=6, state=tk.NORMAL)
        self.log.pack(fill=tk.X, padx=5, pady=5)

        # Path sections container
        self.path_container = ttk.Frame(main_container)
        self.path_container.pack(fill=tk.X, padx=5, pady=5)

        # Inspect button
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        self.inspect_btn = ttk.Button(btn_frame, 
                                    text="🔍 Inspect Element", 
                                    command=self._start_inspection_thread,
                                    style='Inspect.TButton')
        self.inspect_btn.pack(pady=5)

    def create_path_section(self, title, path):
        """Create a new section for displaying a path with copy button."""
        section = ttk.LabelFrame(self.path_container, text=title)
        section.pack(fill=tk.X, padx=5, pady=5)

        # Create a frame for the path and copy button
        content_frame = ttk.Frame(section)
        content_frame.pack(fill=tk.X, padx=5, pady=5)

        # Path label
        path_label = ttk.Label(content_frame, text=path, wraplength=600)
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Copy button
        copy_btn = ttk.Button(content_frame, 
                            text="Copy", 
                            command=lambda: self.copy_to_clipboard(path),
                            style='Copy.TButton')
        copy_btn.pack(side=tk.RIGHT, padx=5)

        self.path_sections.append(section)
        return section

    def copy_to_clipboard(self, text):
        """Copy text to clipboard and show feedback."""
        pyperclip.copy(text)
        self.log_message(f"Copied to clipboard: {text}")

    def clear_path_sections(self):
        """Remove all path sections."""
        for section in self.path_sections:
            section.destroy()
        self.path_sections.clear()

    def log_message(self, msg: str):
        """Append a message to the log area."""
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def clear_tree(self):
        """Remove all items from the treeview."""
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        self.node_ids.clear()  # Clear the node IDs dictionary

    def populate_tree(self, xml_elem, parent=""):
        """Recursively populate the treeview from the XML element."""
        for child in xml_elem:
            name = child.attrib.get("Name", "")
            aid = child.attrib.get("AutomationId", "")
            control = child.attrib.get("LocalizedControlType", "")
            class_name = child.attrib.get("ClassName", "")

            display = f'< Name="{name}" AutomationId="{aid}" LocalizedControlType="{control}" ClassName="{class_name}" >'
            
            elem_key = f"{name}_{aid}_{control}_{class_name}"
            
            node = self.treeview.insert(parent, tk.END, text=display)
            self.node_ids[elem_key] = node

            if child.get('zeuz') == 'aiplugin':
                self.treeview.item(node, tags=('inspected',))

            self.populate_tree(child, node)

    def expand_all(self):
        """Recursively expand all nodes in the treeview."""
        def _expand(node):
            self.treeview.item(node, open=True)
            for child in self.treeview.get_children(node):
                _expand(child)

        for root in self.treeview.get_children():
            _expand(root)

    def highlight_selected_path(self, path_elements):
        """Highlight the selected element based on path."""
        def find_node_by_path(node_id, remaining_path):
            if not remaining_path:
                return node_id
            for child_id in self.treeview.get_children(node_id):
                if remaining_path[0] in self.treeview.item(child_id, 'text'):
                    return find_node_by_path(child_id, remaining_path[1:])
            return None

        root_ids = self.treeview.get_children()
        for root_id in root_ids:
            selected_node = find_node_by_path(root_id, path_elements)
            if selected_node:
                current_tags = self.treeview.item(selected_node, 'tags')
                if 'inspected' in current_tags:
                    self.treeview.item(selected_node, tags=('inspected', 'highlight'))
                else:
                    self.treeview.item(selected_node, tags=('highlight',))
                break

    def _start_inspection_thread(self):
        """Run the inspection process in a separate thread to keep UI responsive."""
        thread = threading.Thread(target=self._inspect_element)
        thread.daemon = True
        thread.start()

    def _inspect_element(self):
        """Perform element inspection and update the GUI accordingly."""
        self.log_message("Hover over the element and press Ctrl to inspect...")

        x, y = inspect()
        self.log_message(f"x,y position: {x}, {y}")

        cleanup = self.inspector.inspect_element(x, y)

        self.clear_tree()
        self.clear_path_sections()  # Clear existing path sections

        try:
            root = ET.fromstring(self.inspector.xml_str)
            self.populate_tree(root)
            self.expand_all() 
            cleanup()
        except ET.ParseError:
            self.log_message("Failed to parse XML from inspector.")

        try:
            Authenticate(self.inspector.xml_str, self.inspector.window_name, self.inspector.paths[0]["path"])
            self.log_message("Content successfully uploaded to AI")
        except Exception as e:
            self.log_message(f"Failed to upload content: {e}")

        for i, path in enumerate(self.inspector.paths):
            text = f"Alternative Path (Area: {path['area']})" if i > 0 else f"Exact Path (Area: {path['area']})"
            self.create_path_section(text, path["path"])


if __name__ == '__main__':
    app = InspectorGUI()
    app.mainloop()
