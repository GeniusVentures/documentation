@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."

pushd "%REPO_ROOT%"
call "%SCRIPT_DIR%cf-build.bat"
if errorlevel 1 (
  popd
  exit /b 1
)

where wrangler >nul 2>nul
if errorlevel 1 (
  call npm install
  if errorlevel 1 (
    popd
    exit /b 1
  )
)

call npx wrangler pages deploy site --project-name=gnus-ai-docs --commit-dirty=true
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
