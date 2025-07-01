import logging
from zuto import Zuto
import sys

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

x = Zuto("tests/ymlSources")

x.start()

input("Press Enter to exit...")
