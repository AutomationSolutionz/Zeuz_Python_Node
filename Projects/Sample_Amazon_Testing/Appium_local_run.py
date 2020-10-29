from Framework.Built_In_Automation.Sequential_Actions.sequential_actions import Sequential_Actions

# step_data =\
# [
#     [
#         ['id', 'element parameter', 'com.android.contacts:id/floating_action_button'],
#         ['wait', 'optional parameter', '10'],
#         ['true', 'appium conditional action', '4,6,pass'],
#         ['false', 'appium conditional action', '5,6']
#     ],
#     [
#         ['package', 'element parameter', 'com.android.contacts'],
#         ['launch', 'appium action', 'launch']
#     ],
#     [
#         ['resource-id', 'element parameter', 'com.android.contacts:id/floating_action_button'],
#         ['class', 'element parameter', 'android.widget.ImageButton'],
#         ['click', 'appium action', 'click']
#     ],
#     [
#         ['log 2', 'utility action', '........ pai nai']
#     ],
#     [
#         ['sleep', 'common action', '20']
#     ],
#     [
#         ['teardown', 'appium action', 'teardown']
#     ]
# ]
# Test_Case =\
# {
#     "TestCases":
#         [
#             {
#                 "Title": "muhib 2nd android",
#                 "Folder": "Muhib Rough Tests",
#                 "Feature": "testtest",
#                 "Dependencies": {"Mobile": ["Android"]},
#                 "Steps":
#                     [
#                         {
#                             "Step name": "Asus contacts",
#                             "Step description": "muhib Sample Step",
#                             "Step expected": "muhib Sample Step",
#                             "Step actions":
#                                 [
#                                     {
#                                         "Action name": "None",
#                                         "Action data":
#                                             [
#                                                 ["teardown", "appium action", "teardown"]
#                                             ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["package", "element parameter", "com.google.android.contacts"],
#                                             ["launch", "appium action", "launch"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["sleep", "common action", "3"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["id", "element parameter", "search_edit_text"],
#                                             ["wait", "appium action", "10"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["id", "element parameter", "search_edit_text"],
#                                             ["click", "appium action", "click"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["sleep", "common action", "4"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["keypress", "appium action", "raw=62"]
#                                         ]
#                                     },
#                                     {"Action name": "None",
#                                      "Action data": [
#                                          ["sleep", "common action", "1"]
#                                      ]
#                                      },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["keypress", "appium action", "long press spacebar"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["sleep", "common action", "4"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["keypress", "appium action", "long press raw=26"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["sleep", "common action", "7"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["keypress", "appium action", "longpress raw=26"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None",
#                                         "Action data": [
#                                             ["sleep", "common action", "6"]
#                                         ]
#                                     },
#                                     {
#                                         "Action name": "None", "Action data": [["keypress", "appium action", "long press power"]]}, {"Action name": "None", "Action data": [["sleep", "common action", "5"]]}, {"Action name": "None", "Action data": [["keypress", "appium action", "longpress power"]]}, {"Action name": "None", "Action data": [["sleep", "common action", "4"]]}, {"Action name": "None", "Action data": [["teardown", "appium action", "teardown"]]}]}, {"Step name": "Emulator contact", "Step description": "Emulator contact", "Step expected": "Emulator contact", "Step actions": [{"Action name": "None", "Action data": [["id", "element parameter", "com.android.contacts:id/floating_action_button"], ["wait", "optional parameter", "10"], ["true", "appium conditional action", "4,6,pass"], ["false", "appium conditional action", "5,6"]]}, {"Action name": "None", "Action data": [["package", "element parameter", "com.android.contacts"], ["launch", "appium action", "launch"]]}, {"Action name": "None", "Action data": [["resource-id", "element parameter", "com.android.contacts:id/floating_action_button"], ["class", "element parameter", "android.widget.ImageButton"], ["click", "appium action", "click"]]}, {"Action name": "None", "Action data": [["log 2", "utility action", "........ pai nai"]]}, {"Action name": "None", "Action data": [["teardown", "appium action", "teardown"]]}]}]}]}
#

dependency = {'Mobile': 'Android'}
device_info =\
    {'device 1':
         {'id': 'emulator-5554',
          'type': 'Android',
          'osver': '10',
          'model': 'Android SDK built for x86',
          'devname': 'sdk_gphone_x86',
          'mfg': 'Google',
          'imei': '358240051111110'}
    }
Test_Case2 = \
{
    "TestCases":
        [
            {
                "Title": "muhib appium local run",
                "Folder": "Muhib Rough Tests",
                "Feature": "testtest",
                "Dependencies": {"Mobile": ["Android"]},
                "Steps":
                    [
                        {
                            "Step name": "Launch app",
                            "Step description": "muhib Sample Step",
                            "Step expected": "muhib Sample Step",
                            "Step actions":
                                [
                                    {
                                        "Action name": "None",
                                        "Action data":
                                            [
                                                ["package", "element parameter", "com.android.contacts"],
                                                ["launch", "appium action", "launch"]
                                            ]
                                    }
                                ]
                        }
                        ,
                        {
                            "Step name": "Click Emulator element",
                            "Step description": "Click Emulator element",
                            "Step expected": "Click Emulator element",
                            "Step actions":
                                [
                                    {
                                        "Action name": "None",
                                        "Action data":
                                            [
                                                ["resource-id", "element parameter", "com.android.contacts:id/floating_action_button"],
                                                ["click", "appium action", "click"]
                                            ]
                                    },
                                    {
                                        "Action name": "None",
                                        "Action data":
                                            [
                                                ["sleep", "common action", "10"]
                                            ]
                                    }
                                ]
                        },
                        {
                            "Step name": "Teardown Emulator app",
                            "Step description": "Teardown Emulator",
                            "Step expected": "Teardown Emulator",
                            "Step actions":
                                [
                                    {
                                        "Action name": "None",
                                        "Action data":
                                            [
                                                ["teardown", "appium action", "teardown"]
                                            ]
                                    }
                                ]
                        }
                    ]
            }
        ]
}

if __name__ == "__main__":
    step_data = []
    for i in Test_Case2["TestCases"][0]["Steps"]:
        all_actions = i["Step actions"]
        for j in all_actions:
            step_data.append(j["Action data"])
    print(step_data)

    result = Sequential_Actions(
        step_data=step_data,
        _dependency=dependency,
        _device_info=device_info
    )
    print(result)
