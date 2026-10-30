@echo off
setlocal

rem Convenience entry point for Command Prompt. Pass any PowerShell options through.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-research-chrome.ps1" %*
exit /b %ERRORLEVEL%
