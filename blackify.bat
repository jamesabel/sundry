call venv\Scripts\activate.bat
python -m black -l 192 sundry test_sundry setup.py
deactivate
