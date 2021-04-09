import logging, sys
logging.basicConfig(stream=sys.stderr)
from slurmweb.confdashboard.slurmwebconf import app as application
