@echo off
echo This script will package all files into a zip ready for distribution
PAUSE

echo Creating temporary directory
mkdir .\temp

echo Packaging Client
pyinstaller --onefile --noconsole Client.py

echo Copying Files
copy .\dist\Client.exe .\temp
copy .\config.json .\temp
copy .\updates.txt .\temp

echo Preparing for Ziping
rename temp Disbroad_Client

echo Ziping Files
7z a -tzip Client.zip Disbroad_Client

echo Cleaning up
rmdir .\build /s /q
rmdir .\dist /s /q
rmdir .\Disbroad_Client /s /q
del .\Client.spec

echo Done!
PAUSE 
