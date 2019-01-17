set PYTHON_EXE="\Program Files\Python37\python.exe"
%PYTHON_EXE% -m venv --clear venv
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip3 install -U setuptools
venv\Scripts\pip3 install -U -r requirements.txt
