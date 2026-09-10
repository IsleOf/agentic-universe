@echo off
REM Regenerates the Agentic Universe fleet dashboard and opens it.
REM Installed to run at Windows logon via Task Scheduler
REM (task name: AgenticUniverseDashboard).
wsl python3 /home/dev/.agentic/dashboard.py
start "" "\\wsl$\Ubuntu\home\dev\.agentic\dashboard.html"
