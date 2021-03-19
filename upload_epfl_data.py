import glob
import os

import pandas as pd

from tqdm import tqdm

from config import conn

# Upload files in DB
for filename in glob.glob('data/epfl/*.csv'):
    df = pd.read_csv(filename)
    df.columns = [x.lower() for x in df.columns]
    df = df.set_index('sb_uuid')
    table_name = os.path.basename(filename).lower()[:-4]
    for i in tqdm(range(23)):
        size = 100000
        df.iloc[i*size:(i+1)*size, :].to_sql(table_name, conn, if_exists='append', chunksize=10000)
    del df