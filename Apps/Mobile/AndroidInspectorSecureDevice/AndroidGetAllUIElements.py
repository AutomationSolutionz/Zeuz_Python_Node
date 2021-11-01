import subprocess, os, platform
import xml.etree.ElementTree as ET

output = subprocess.check_output(
    "adb exec-out uiautomator dump --ignore-secure-device  /dev/tty", shell=True
)  # output uiautomator screen layout
output_str = str(output)
string_raw = output_str.replace(">", "> \n")
# pretty_string = indent(string_raw)
xml_tree = ET.fromstring(output.decode()[56:-33])
xml_str = ""
def traverse(parent, parethesis=0):
    global xml_str
    xml_str += "\n" + "  "*parethesis + "<div " + "".join('%s="%s" ' % (i, parent.attrib[i]) for i in parent.attrib) + ">"
    for each in parent:
        traverse(each, parethesis+1)
    xml_str += "\n" + "  "*parethesis + "</div>"
traverse(xml_tree)
print(xml_str)
with open("App2.xml", "w") as f:
    f.write(xml_str)
list_ = string_raw.split("\n")
clean_list = []
for each in list_:
    # if 'text=""' not in each or 'resource-id=""' not in each or 'content-desc=""' not in each:
    clean_list.append(each + "\n")

if os.path.exists("AndroidScreenOut.txt"):
    os.remove("AndroidScreenOut.txt")

with open("AndroidScreenOut.txt", "w") as outfile:
    outfile.write("\n".join(clean_list))

if platform.system() == "Darwin":  # macOS
    subprocess.call(("open", "AndroidScreenOut.txt"))
elif platform.system() == "Windows":  # Windows
    os.startfile("AndroidScreenOut.txt")
else:  # linux variants
    subprocess.call(("xdg-open", "AndroidScreenOut.txt"))
