import sys
import os
from pathlib import Path

sys.path.append(str(Path("../")))
sys.path.append(str(Path("../Framework/")))

from Projects.Sample_Amazon_Testing.Local_run import main as LocalRun
import unittest
import traceback

class AppTest(unittest.TestCase):
    """Basis for all test cases"""

    def test_5251(self):
        result = None
        try:
            result = LocalRun("AWS Local Run Android")
        except:
            print("Failed to run test case TEST-5251")
            traceback.print_exc()
            result = "failed"

        assert result == "passed"

    def tearDown(self):
        pass
        # self.driver.quit()
