REM Manual release to PyPI. The preferred path is the "Publish to PyPI" GitHub workflow (create a GitHub release);
REM this script is the fallback for publishing from a local checkout.
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist
if exist sundry.egg-info rmdir /S /Q sundry.egg-info
call venv\Scripts\activate.bat
python -m build
python -m twine check dist/*
python -m twine upload dist/*
deactivate
