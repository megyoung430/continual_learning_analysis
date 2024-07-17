import sys
sys.path.insert(0,'/Users/megyoung/continual_learning_analysis/bpodautopy/bpodautopy')
from db import Engine, Connection
from pathlib import Path
import pandas as pd
import numpy as np
import json

dbc = Connection()
dbe = Engine()

