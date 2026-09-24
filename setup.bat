@echo off
set "PYTHON_EXE=C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set "SCRIPT_DIR=%~dp0"
"%PYTHON_EXE%" "%SCRIPT_DIR%Setup.py"