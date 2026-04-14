@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."

pushd "%REPO_ROOT%" || exit /b 1
set "REPO_ROOT=%CD%"
set "SG_DOCS_DIR=%REPO_ROOT%\sg-docs"
for %%I in ("%REPO_ROOT%\..\SuperGenius") do set "SUPERGENIUS_ROOT=%%~fI"

if exist ".gitmodules" (
  call git submodule sync --recursive || goto :error
  call git submodule update --init --recursive || goto :error
)

set "OUTPUT_DIR=%REPO_ROOT%\docs\SuperGenius"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if exist "%OUTPUT_DIR%\src" rmdir /s /q "%OUTPUT_DIR%\src"

if not exist "%SG_DOCS_DIR%\doxygen" mkdir "%SG_DOCS_DIR%\doxygen"

pushd "%SUPERGENIUS_ROOT%" || goto :error
set "DOXY_OVERRIDE_FILE=%SG_DOCS_DIR%\.cf-doxygen.Doxyfile"
(
  echo @INCLUDE = %SG_DOCS_DIR%\Doxyfile
  echo FULL_PATH_NAMES = NO
  echo OUTPUT_DIRECTORY = %SG_DOCS_DIR%\doxygen
) > "%DOXY_OVERRIDE_FILE%"

call doxygen "%DOXY_OVERRIDE_FILE%" || goto :error_sg
if exist "%DOXY_OVERRIDE_FILE%" del /f /q "%DOXY_OVERRIDE_FILE%"
popd

call doxybook2 --input sg-docs/doxygen/xml/ --output "%OUTPUT_DIR%" -c scripts/doxybook.json || goto :error
call python3 scripts/build_navigation.py "%OUTPUT_DIR%" || goto :error

call python3 -m venv .venv || goto :error
call .venv\Scripts\activate.bat || goto :error
call pip install --upgrade pip setuptools wheel || goto :error
call pip install -r requirements.txt || goto :error
call mkdocs build || goto :error

@REM set "INDEX_FILE=site\search\search_index.json"
@REM if exist "%INDEX_FILE%" (
@REM   powershell -NoProfile -ExecutionPolicy Bypass -Command "$in='site\search\search_index.json';$out=$in+'.gz';$fi=[IO.File]::OpenRead($in);try{$fo=[IO.File]::Create($out);try{$gz=New-Object IO.Compression.GzipStream($fo,[IO.Compression.CompressionLevel]::Optimal);try{$fi.CopyTo($gz)}finally{$gz.Dispose()}}finally{$fo.Dispose()}}finally{$fi.Dispose()}" || goto :error
@REM   move /y "%INDEX_FILE%.gz" "%INDEX_FILE%" >nul || goto :error
@REM
@REM   set "HEADERS_FILE=site\_headers"
@REM   findstr /b /c:"/search/search_index.json" "%HEADERS_FILE%" >nul 2>nul
@REM   if errorlevel 1 (
@REM     >> "%HEADERS_FILE%" echo(
@REM     >> "%HEADERS_FILE%" echo /search/search_index.json
@REM     >> "%HEADERS_FILE%" echo   Content-Type: application/json; charset=utf-8
@REM     >> "%HEADERS_FILE%" echo   Content-Encoding: gzip
@REM   )
@REM )

popd
exit /b 0

:error_sg
if exist "%DOXY_OVERRIDE_FILE%" del /f /q "%DOXY_OVERRIDE_FILE%"
popd

:error
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
