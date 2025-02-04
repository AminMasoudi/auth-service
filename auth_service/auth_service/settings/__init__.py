
import os, sys
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.environ.get("DEBUG", "True") == "True" 
if DEBUG == True:
    from .debug import *
else:
    from .prod import *


TEST_MODE = "test" in sys.argv
if TEST_MODE:
    from.test_settings import *