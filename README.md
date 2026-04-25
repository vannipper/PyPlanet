# PyPlanet

Procedural planet and star visualization built with Python, pygame, and OpenGL.

## Prerequisites

- Windows 10/11
- Conda (Anaconda or Miniconda)
- VS Code
- VS Code Python extension: ms-python.python

## First-time setup

1. Clone the repository.
2. Open the repository folder in VS Code.
3. Create or update the project environment:

```powershell
conda env update --prefix ./env --file environment.yml --prune
```

4. Select the interpreter in VS Code:
- Command Palette -> Python: Select Interpreter
- Choose ${workspaceFolder}\\env\\python.exe

## Running the app

### Terminal (sanity check)

```powershell
conda run -p .\env python .\main.py
```

### VS Code

- Open main.py.
- Use Run Python File (top-right play button), or
- Use Run and Debug with the Python Debugger: PyPlanet profile.

Run and debug are configured to use the same interpreter and PATH behavior.

## Development workflow

When dependencies change in environment.yml, update the environment:

```powershell
conda env update --prefix ./env --file environment.yml --prune
```

If interpreter or package state looks stale, reload VS Code:

- Command Palette -> Developer: Reload Window

## Why .vscode files are tracked

This repository intentionally tracks shared project configuration files:

- .vscode/extensions.json
- .vscode/launch.json
- .vscode/settings.json
- .vscode/tasks.json

These files provide consistent onboarding and reduce run/debug environment mismatch issues for new developers.

## Troubleshooting

### Play button fails but debug works

1. Confirm interpreter is ${workspaceFolder}\\env\\python.exe.
2. Open a new terminal after settings changes.
3. Reload the VS Code window.

### ModuleNotFoundError: pkg_resources

This project currently relies on dependencies that still use pkg_resources, so setuptools<81 is pinned in environment.yml.

### Native import crash with numpy/pygame on Windows

This is typically environment activation or PATH related. Use one of these:

- Run through VS Code using the committed workspace settings, or
- Run from terminal using conda run -p .\env ...
