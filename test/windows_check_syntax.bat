SET CURDIR=%~dp0
SET PYSCRIPT=%~1\Scripts
SET SRCDIR=%2

if "%SRCDIR%" == "" (
	"%PYSCRIPT%\pep8" --config="%CURDIR%pep8.cfg" . >..\reports\pep8.out   
) else (
    "%PYSCRIPT%\pep8" --config="%CURDIR%pep8.cfg" %SRCDIR% >reports\pep8.out
)

exit /B 0