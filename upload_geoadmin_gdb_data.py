import glob
import os

from config import db_host, db_port, db_user, db_name

for folder in glob.glob('data/geoadmin/*.gdb'):
    os.system(f'ogr2ogr -f "PostgreSQL" PG:"host={db_host} port={db_port} dbname={db_name} user={db_user}" -overwrite -progress {folder}')