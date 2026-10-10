@echo off
rem Double-click to start KawTeam (backend and frontend) in this one window.
cd /d "%~dp0"
node scripts\dev.mjs
if errorlevel 1 pause
