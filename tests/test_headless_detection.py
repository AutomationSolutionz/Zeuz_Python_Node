import os
import unittest
from unittest.mock import patch
from Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions import is_headless_environment


class TestHeadlessEnvironment(unittest.TestCase):
    def test_docker_detected(self):
        """Test that Docker container is detected as headless"""
        os.environ['DOCKER_CONTAINER'] = 'true'
        self.assertTrue(is_headless_environment())
        del os.environ['DOCKER_CONTAINER']

    def test_aws_codebuild_detected(self):
        """Test that AWS CodeBuild environment is detected as headless"""
        os.environ['CODEBUILD_BUILD_ID'] = 'abc123'
        self.assertTrue(is_headless_environment())
        del os.environ['CODEBUILD_BUILD_ID']

    def tearDown(self):
        for var in ['DOCKER_CONTAINER', 'CODEBUILD_BUILD_ID']:
            if var in os.environ:
                del os.environ[var]


if __name__ == '__main__':
    unittest.main()