@echo off
echo Setting up Python environment...
set PATH=%PATH%;C:\Users\Administrator\AppData\Local\Programs\Python\Python311;C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Scripts

echo Creating virtual environment...
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe -m venv venv

echo Activating virtual environment...
call .\venv\Scripts\activate

echo Installing requirements...
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt

echo Running main script...
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe main.py

echo Done!
pause 