import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "insurance_agent.settings")

from insurance_agent.wsgi import application

app = application