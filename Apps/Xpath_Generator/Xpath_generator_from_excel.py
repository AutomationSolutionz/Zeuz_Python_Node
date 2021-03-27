import xlwings as xw
import pathlib
driver_type = "selenium"
def _construct_query(step_data_set, web_element_object=False):
    """
    first find out if in our dataset user is using css or xpath.  If they are using css or xpath, they cannot use any
    other feature such as child parameter or multiple element parameter to locate the element.
    If web_element_object = True then it will generate a xpath so that find_elements can find only the child elements
    inside the given parent element
    """
    try:
        collect_all_attribute = [x[0] for x in step_data_set]
        # find out if ref exists.  If it exists, it will set the value to True else False
        child_ref_exits = any("child parameter" in s for s in step_data_set)
        parent_ref_exits = any("parent parameter" in s for s in step_data_set)
        sibling_ref_exits = any("sibling parameter" in s for s in step_data_set)
        unique_ref_exists = any("unique parameter" in s for s in step_data_set)
        # get all child, element, and parent only
        child_parameter_list = [x for x in step_data_set if "child parameter" in x[1]]
        element_parameter_list = [
            x for x in step_data_set if "element parameter" in x[1]
        ]
        parent_parameter_list = [x for x in step_data_set if "parent parameter" in x[1]]
        sibling_parameter_list = [
            x for x in step_data_set if "sibling parameter" in x[1]
        ]
        unique_parameter_list = [x for x in step_data_set if "unique parameter" in x[1]]

        if (
            unique_ref_exists
            and (driver_type == "appium" or driver_type == "selenium")
            and len(unique_parameter_list) > 0
        ):  # for unique identifier
            return (
                [unique_parameter_list[0][0], unique_parameter_list[0][2]],
                "unique",
            )
        elif "css" in collect_all_attribute and "xpath" not in collect_all_attribute:
            # return the raw css command with css as type.  We do this so that even if user enters other data, we will ignore them.
            # here we expect to get raw css query
            return (([x for x in step_data_set if "css" in x[0]][0][2]), "css")
        elif "xpath" in collect_all_attribute and "css" not in collect_all_attribute:
            # return the raw xpath command with xpath as type. We do this so that even if user enters other data, we will ignore them.
            # here we expect to get raw xpath query
            return (([x for x in step_data_set if "xpath" in x[0]][0][2]), "xpath")
        elif (
            child_ref_exits == False
            and parent_ref_exits == False
            and sibling_ref_exits == False
            and web_element_object == False
        ):
            """  If  there are no child or parent as reference, then we construct the xpath differently"""
            # first we collect all rows with element parameter only
            xpath_element_list = _construct_xpath_list(element_parameter_list)
            return (_construct_xpath_string_from_list(xpath_element_list), "xpath")

        elif (
            child_ref_exits == True
            and parent_ref_exits == False
            and sibling_ref_exits == False
        ):
            """  If  There is child but making sure no parent or sibling
            //<child_tag>[child_parameter]/ancestor::<element_tag>[element_parameter]
            """
            xpath_child_list = _construct_xpath_list(child_parameter_list)
            child_xpath_string = (
                _construct_xpath_string_from_list(xpath_child_list) + "/ancestor::"
            )

            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            element_xpath_string = element_xpath_string.replace("//", "")

            full_query = child_xpath_string + element_xpath_string
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and parent_ref_exits == True
            and sibling_ref_exits == False
            and (driver_type == "appium" or driver_type == "selenium")
        ):
            """  
            parent as a reference
            '//<parent tag>[<parent attributes>]/descendant::<target element tag>[<target element attribute>]'
            """
            xpath_parent_list = _construct_xpath_list(parent_parameter_list)
            parent_xpath_string = (
                _construct_xpath_string_from_list(xpath_parent_list) + "/descendant::"
            )

            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            element_xpath_string = element_xpath_string.replace("//", "")

            full_query = parent_xpath_string + element_xpath_string
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and web_element_object == True
            and sibling_ref_exits == False
            and (driver_type == "appium" or driver_type == "selenium")
            and parent_ref_exits == False
        ):
            """
            'descendant::<target element tag>[<target element attribute>]'
            """
            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            element_xpath_string = element_xpath_string.replace("//", "")

            full_query = "descendant::" + element_xpath_string
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and parent_ref_exits == True
            and sibling_ref_exits == True
            and (driver_type == "appium" or driver_type == "selenium")
        ):
            """  for siblings, we need parent, siblings and element.  Siblings cannot be used with just element
            xpath_format = '//<sibling_tag>[<sibling_element>]/ancestor::<immediate_parent_tag>[<immediate_parent_element>]//<target_tag>[<target_element>]'
            """
            xpath_sibling_list = _construct_xpath_list(sibling_parameter_list)
            sibling_xpath_string = (
                _construct_xpath_string_from_list(xpath_sibling_list) + "/ancestor::"
            )

            xpath_parent_list = _construct_xpath_list(parent_parameter_list)
            parent_xpath_string = _construct_xpath_string_from_list(xpath_parent_list)
            parent_xpath_string = parent_xpath_string.replace("//", "")

            xpath_element_list = _construct_xpath_list(element_parameter_list)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)

            full_query = (
                sibling_xpath_string + parent_xpath_string + element_xpath_string
            )
            return (full_query, "xpath")

        elif (
            child_ref_exits == False
            and parent_ref_exits == True
            and sibling_ref_exits == False
            and (driver_type == "xml")
        ):
            """  If  There is parent but making sure no child"""
            xpath_parent_list = _construct_xpath_list(parent_parameter_list)
            parent_xpath_string = _construct_xpath_string_from_list(xpath_parent_list)
            # For xml we just put parent first and element later
            xpath_element_list = _construct_xpath_list(element_parameter_list, True)
            element_xpath_string = _construct_xpath_string_from_list(xpath_element_list)
            xpath_element_list_combined = parent_xpath_string + element_xpath_string
            return (
                _construct_xpath_string_from_list(xpath_element_list_combined),
                "xpath",
            )

        elif child_ref_exits == True and (driver_type == "xml"):
            """Currently we do not support child as reference for xml"""
            return False, False

        else:
            return False, False
    except Exception as e:
        print(e)

def _construct_xpath_list(parameter_list, add_dot=False):
    """
    This function constructs the raw data from step data into a xpath friendly format but in a list
    """
    try:
        # Setting the list empty
        element_main_body_list = []
        # these are special cases where we cannot treat their attribute as any other attribute such as id, class and so on...
        excluded_attribute = [
            "*text",
            "text",
            "tag",
            "css",
            "index",
            "xpath",
            "switch frame",
            "switch window",
            "switch alert",
            "switch active",
        ]
        for each_data_row in parameter_list:
            attribute = each_data_row[0].strip()
            attribute_value = each_data_row[2]
            if attribute == "text" and (
                driver_type == "selenium" or driver_type == "xml"
            ):
                text_value = '[text()="%s"]' % attribute_value
                element_main_body_list.append(text_value)
            elif attribute == "*text" and (
                driver_type == "selenium" or driver_type == "xml"
            ):  # ignore case
                # text_value = '[contains(translate(text(),"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"%s")]'%str(attribute_value).lower()
                text_value = '[contains(text(),"%s")]' % (str(attribute_value))
                element_main_body_list.append(text_value)
            elif attribute not in excluded_attribute and "*" not in attribute:
                other_value = '[@%s="%s"]' % (attribute, attribute_value)
                element_main_body_list.append(other_value)
            elif (
                attribute not in excluded_attribute and "*" in attribute
            ):  # ignore case
                if driver_type == "appium":
                    other_value = '[contains(@%s,"%s")]' % (
                        attribute.split("*")[1],
                        str(attribute_value),
                    )
                else:
                    other_value = '[contains(@%s,"%s")]' % (
                        attribute.split("*")[1],
                        str(attribute_value),
                    )
                element_main_body_list.append(other_value)
        if "tag" in [x[0] for x in parameter_list]:
            tag_item = "//" + [x for x in parameter_list if "tag" in x][0][2]
        else:
            tag_item = "//*"
        if add_dot != False and driver_type != "xml":
            tag_item = "." + tag_item
        element_main_body_list.append(tag_item)
        # We need to reverse the list so that tag comes at the begining
        return list(reversed(element_main_body_list))
    except Exception as e:
        print(e)


def _construct_xpath_string_from_list(xpath_list):
    """
    in this function, we simply take the list and construct the actual query in string
    """
    try:
        xpath_string_format = ""
        for each in xpath_list:
            xpath_string_format = xpath_string_format + each
        return xpath_string_format
    except Exception as e:
        print(e)

if __name__ == "__main__":
    path = pathlib.Path(__file__).parent
    path = path/"dataset.xlsx"
    wb = xw.Book(path)
    sheet = wb.sheets["Sheet1"]
    expand = "table"
    cell_range = "A1:A3"
    while True:
        cell_data = sheet.range(cell_range).expand(expand).value
        # print(cell_data)
        # wb.save()
        data = cell_data[1:] if cell_data[0][1].strip().lower() == "middle" else cell_data
        result = _construct_query(data)[0]
        print(result)
        print("[To get new Xpath change and save the exel file and press ENTER]")
        input()
        # wb.close()
