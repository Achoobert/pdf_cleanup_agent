@echo off
echo Creating PDF Power Converter Portable Distribution...
echo.

REM Clean up any existing portable directory first
echo Cleaning up existing portable directory...
python clean_portable.py

REM Run the portable setup script
echo Creating portable distribution...
python portable_setup.py

if errorlevel 1 (
    echo.
    echo Error creating portable distribution.
    echo Try running clean_portable.py manually and then try again.
    pause
    exit /b 1
)

REM Run tests to verify everything works
echo.
echo Testing portable distribution...
python test_portable.py

if errorlevel 1 (
    echo.
    echo Warning: Some tests failed. Check the output above.
)

echo.
echo Portable distribution created successfully!
echo.
echo Would you like to create a ZIP file for distribution? (y/n)
set /p create_zip=

if /i "%create_zip%"=="y" (
    echo Creating ZIP file...
    powershell -command "Compress-Archive -Path 'portable_dist\*' -DestinationPath 'PDF_Power_Converter_Portable_Fixed.zip' -Force"
    if errorlevel 1 (
        echo Error creating ZIP file.
    ) else (
        echo ZIP file created: PDF_Power_Converter_Portable_Fixed.zip
    )
)

echo.
echo Done! You can now distribute the portable version.
echo Location: portable_dist\
echo ZIP file: PDF_Power_Converter_Portable_Fixed.zip
pause