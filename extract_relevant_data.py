import pandas as pd

from sqlalchemy import select

import sqlalchemy

from tqdm import tqdm

from config import engine, conn

meta = sqlalchemy.MetaData()
dach = sqlalchemy.Table('solkat_ch_dach', meta, autoload_with=engine)

epfl = sqlalchemy.Table('rooftop_pv_ch_annual_by_building', meta, autoload_with=engine)
cantons = sqlalchemy.Table('tlm_kantonsgebiet', meta, autoload_with=engine)
municipalities = sqlalchemy.Table('tlm_hoheitsgebiet', meta, autoload_with=engine)

df_epfl = pd.read_sql(epfl.select(), conn).set_index('sb_uuid')

df_muni = pd.read_json('data/Solarenergiepotenziale_Gemeinden_Daecher_und_Fassaden.json')

mapping = df_muni.set_index(['MunicipalityName'])['Canton']

t2 = municipalities
for name, shape in tqdm(pd.read_sql(select(t2.c.name, t2.c.shape.ST_AsText()), conn).values):
    df = pd.read_sql(
        select(dach.c.df_uid, dach.c.sb_uuid, dach.c.gstrahlung, dach.c.flaeche).where(dach.c.shape.intersects(shape)),
        conn)
    if df.shape[0] == 0:
        continue
    df['municipality'] = name
    df['canton'] = mapping.get(name, '-')
    df_buildings = df.groupby('sb_uuid').sum()[['gstrahlung', 'flaeche']]
    df_buildings['municipality'] = name
    df_buildings['canton'] = mapping.get(name, '-')
    df_epfl_sub = df_epfl.reindex(index=df_buildings.index)

    for c1, c2 in zip(['epv_kwh_a', 'apv', 'gt_kwh_m2_a', 'epv_kwh_m2roof_a'],
                      ['epfl_potential', 'epfl_area', 'epfl_radiation', 'epfl_potential_per_m2']):
        df_buildings[c2] = df_epfl_sub[c1]
    df_buildings.to_sql('buildings', conn, if_exists='append')
    df.to_sql('roofs', conn, if_exists='append')