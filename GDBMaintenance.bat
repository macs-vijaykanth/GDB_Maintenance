@echo off
set "PYTHON_EXE=C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
set "SCRIPT_DIR=%~dp0"
cd %SCRIPT_DIR%
"%PYTHON_EXE%" "%SCRIPT_DIR%main.py"