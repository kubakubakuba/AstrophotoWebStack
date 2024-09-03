import sys
import os

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, '/var/www/AstrophotoWebStack')

activate_this = '/path/to/venv/bin/activate_this.py'

with open(activate_this) as file:
        exec(file.read(), dict(__file__=activate_this))

from app import app as application
