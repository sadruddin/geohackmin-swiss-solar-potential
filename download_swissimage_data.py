"""
Generate a CSV file using the data access form under:
https://www.swisstopo.admin.ch/en/geodata/images/ortho/swissimage10.html

The scope could be a specific municipality, canton or the whole country (total size 2TB)

python download_swissimage_data.py filename.csv

Downloaded images will be saved in the data/swissimage folder
"""

import os
import sys

import pandas as pd

df = pd.read_csv(sys.argv[1], header=None)

for link in df[0]:
    os.system('wget -P data/swissimage -c %s' % link)
