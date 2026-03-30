"""
PyInstaller Runtime Hook for Debug Build
This script runs BEFORE main.py when bundled via tsp_auto_debug.spec.
Sets environment variable so logger.py enables debug + file logging automatically.
"""
import os

os.environ['TSP_AUTO_DEBUG'] = '1'
