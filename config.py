from sqlalchemy import create_engine
import geoalchemy2

db_host = 'localhost'
db_port = 5432
db_user = 'sad'
db_name = 'geohackmin'

engine = create_engine(f'postgresql://{db_user}@{db_host}:{db_port}/{db_name}')
conn = engine.connect()