@echo off
REM Start uvicorn server batch file
REM Usage: start_server.bat [port]

SET PORT=%1
IF "%PORT%"=="" SET PORT=8000

echo Starting server on port %PORT% ...
uvicorn main:app --reload --host 0.0.0.0 --port %PORT%