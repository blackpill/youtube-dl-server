import os
import importlib

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Import all modules that are not __init__.py
for filename in os.listdir(current_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]
        module = importlib.import_module('.' + module_name, package=__name__)