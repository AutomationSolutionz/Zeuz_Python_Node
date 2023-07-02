import os
import subprocess
from AndroidSetup_Windows import Add_To_Path

is_pytesseract = subprocess.run('pip list | findstr "pytesseract"', shell=True, capture_output=True, text=True)

if is_pytesseract.stdout:
    print('Pytesseractt is already installed')
else:
    print('Installing Pytesseract')
    os.system('pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pytesseract')


reg_query_cmd = ['reg', 'query', r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall', '/s']
findstr_cmd = ['findstr', '/B', '.*DisplayName']
tesseract_cmd = ['findstr', 'Tesseract-OCR']

reg_query_process = subprocess.Popen(reg_query_cmd, stdout=subprocess.PIPE)
findstr_process = subprocess.Popen(findstr_cmd, stdin=reg_query_process.stdout, stdout=subprocess.PIPE)
tesseract_process = subprocess.Popen(tesseract_cmd, stdin=findstr_process.stdout, stdout=subprocess.PIPE)

is_pytesseract_exe, _ = tesseract_process.communicate()

if is_pytesseract_exe:
    print('Pytesseract executable file is alreday installed')
else:
    print('Starting installation of Pytesseract executable file')
    install_process = subprocess.Popen(['winget', 'install', 'Tesseract-OCR - open source OCR engine'], text=True)
    stdout, stderr = install_process.communicate()
    if stdout is not None:
        print(stdout)
    if stderr is not None:
        print(stderr)
    else:
        print('Tesseract installation is complete!')



    
