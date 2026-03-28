#!/usr/bin/env python
"""Run script for Kotizo backend"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        print("Error: Django not installed. Run: pip install django")
        sys.exit(1)
    
    execute_from_command_line(['manage.py', 'runserver'])

if __name__ == '__main__':
    main()
