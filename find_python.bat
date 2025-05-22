@echo off
echo Searching for Python installations...
where python
echo.
echo Checking common Python locations:
if exist "C:\Python311\python.exe" echo Found Python at C:\Python311\python.exe
if exist "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe" echo Found Python at C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe
if exist "C:\Program Files\Python311\python.exe" echo Found Python at C:\Program Files\Python311\python.exe
if exist "C:\Program Files (x86)\Python311\python.exe" echo Found Python at C:\Program Files (x86)\Python311\python.exe
pause 