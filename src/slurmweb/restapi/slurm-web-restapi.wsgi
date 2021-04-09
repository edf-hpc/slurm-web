import logging, sys
logging.basicConfig(stream=sys.stderr)
from slurm_web_restapi.slurmrestapi import app as application

