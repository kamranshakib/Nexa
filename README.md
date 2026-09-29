# NEXA

*"Your computer remembers. You just continue."*

NEXA is a modern, fast, lightweight, elegant personal desktop productivity environment for Windows. Built with Python and PyQt6 using Fluent Design (WinUI 3 equivalent).

## Current Development Phase: PHASE 1 (Core & Foundation)
- [x] Project Structure (Python Clean Architecture)
- [x] Main Entry Point (`nexa/main.py`)
- [x] UI Shell with Fluent Widgets (`nexa/ui/app.py`)
- [x] Home Dashboard View
- [x] Global Launcher View
- [x] Workspaces View
- [x] Settings View
- [x] Database Configuration (SQLite + SQLAlchemy)

## Setup Instructions
1. Install Python 3.10+
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   .\venv\Scripts\python.exe -m pip install PyQt6 PyQt6-Fluent-Widgets SQLAlchemy loguru
   ```
4. Run the application:
   ```bash
   .\venv\Scripts\python.exe nexa\main.py
   ```
