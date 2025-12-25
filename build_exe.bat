@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building EXE file...
python -m PyInstaller --onefile --windowed --name "Autoclicker" autoclicker.py

echo.
echo Done! Your EXE file is in the 'dist' folder.
pause

