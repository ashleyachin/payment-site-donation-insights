@echo off
cd /d "%~dp0"
title Payment Site Donation Insights
echo.
echo   Open in your browser:  http://127.0.0.1:8080/
echo   Keep this window open while you use the dashboard.
echo.
python -m http.server 8080
pause
