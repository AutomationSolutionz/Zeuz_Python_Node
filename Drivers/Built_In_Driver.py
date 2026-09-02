"""
Created on May 15, 2016

@author: RizDesktop
"""

import sys
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa


def sequential_actions(
    step_data,
    test_action_info,
    temp_q,
    debug_actions=None,
):
    try:
        sTestStepReturnStatus = sa.Sequential_Actions(
            step_data,
            test_action_info,
            debug_actions,
        )
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
