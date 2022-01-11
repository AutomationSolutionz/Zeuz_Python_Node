import unittest, os
from Framework.Utilities.CommonUtil import path_parser
class Test_path_parser(unittest.TestCase):
    def test_path(self):
        compare = {
            r"~\Downloads": r"C:\Users\ASUS\Downloads",
            r"~\**download": r"C:\Users\ASUS\Downloads",
            r"C:\Users\ASUS\Downloads": r"C:\Users\ASUS\Downloads",
            r"C:\Users\ASUS\**download": r"C:\Users\ASUS\Downloads",
            r"~": r"C:\Users\ASUS",
            r"C:": r"C:",
        }
        for i in compare:
            self.assertEqual(path_parser(i), compare[i])
        p = path_parser(r"~\Downloads\*.pdf")
        self.assertTrue(os.path.exists(p) and p.endswith(".pdf") and p.startswith(r"C:\Users\ASUS\Downloads"))
        p = path_parser(r"~\Downloads\*pdf.pdf")
        self.assertTrue(os.path.exists(p) and p.endswith(".pdf") and p.startswith(r"C:\Users\ASUS\Downloads"))
        p = path_parser(r"~\Downloads\*")
        self.assertTrue(os.path.exists(p))

if __name__ == "__main__":
    unittest.main()

    r"""
        print(path_parser(r"~\Downloads"))                          C:\Users\ASUS\Downloads
    print(path_parser(r"~\**download"))                         C:\Users\ASUS\Downloads
    print(path_parser(r"C:\Users\ASUS\Downloads"))              C:\Users\ASUS\Downloads
    print(path_parser(r"C:\Users\ASUS\**download"))             C:\Users\ASUS\Downloads
    print(path_parser(r"~"))                                    C:\Users\ASUS
    print(path_parser(r"C:"))                                   C:
    print(path_parser(r"~\Downloads\*.pdf"))                    C:\Users\ASUS\Downloads\FF.pdf
    
    """