# deploy.py - Simplified entry point
import subprocess
import sys

# Install dependencies
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Import and run the app
from app import main

if __name__ == "__main__":
    main()
