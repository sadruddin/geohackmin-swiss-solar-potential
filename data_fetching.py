import random

import pandas as pd

import sqlalchemy
from sqlalchemy import select

from config import engine, conn

meta = sqlalchemy.MetaData()
dach = sqlalchemy.Table('solkat_ch_dach', meta, autoload_with=engine)
dach_monat = sqlalchemy.Table('solkat_ch_dach_monat', meta, autoload_with=engine)
#fass = sqlalchemy.Table('solkat_ch_fass', meta, autoload_with=engine)
#fass_monat = sqlalchemy.Table('solkat_ch_fass_monat', meta, autoload_with=engine)

municipalities = sqlalchemy.Table('tlm_hoheitsgebiet', meta, autoload_with=engine)
cantons = sqlalchemy.Table('tlm_kantonsgebiet', meta, autoload_with=engine)

buildings = sqlalchemy.Table('buildings', meta, autoload_with=engine)
roofs = sqlalchemy.Table('roofs', meta, autoload_with=engine)


t1 = municipalities
t2 = cantons

df = pd.read_json('/data/geo.admin.ch/Solarenergiepotenziale_Gemeinden_Daecher_und_Fassaden.json')
potential_muni = df.set_index(['Canton', 'MunicipalityName'])['Scenario2_RoofsOnly_PotentialSolarElectricity_GWh']
potential_canton = df.groupby('Canton').sum()['Scenario2_RoofsOnly_PotentialSolarElectricity_GWh']


def get_actual_monthly_production(year):
    # Link to actual production number
    return pd.Series([random.random()*10 for x in range(12)], index=range(1, 13))


def get_detected_solar_panels(rectangle=None, municipality=None, canton=None):
    t = sqlalchemy.Table('detected_solar_panels', meta, autoload_with=engine)

    if rectangle is not None:
        x1, y1, x2, y2 = rectangle
        polygon = tuple(x*1000 for x in [x1, y1, x1, y2, x2, y2, x2, y1, x1, y1])
        polygon = 'POLYGON((%f %f,%f %f,%f %f,%f %f,%f %f))' % polygon
        shapes = [polygon]
    elif municipality is not None:
        shapes = pd.read_sql(select(municipalities.c.shape.ST_AsText()).where(municipalities.c.name == municipality), conn).values[0]
    elif canton is not None:
        shapes = pd.read_sql(select(cantons.c.shape.ST_AsText()).where(cantons.c.name == canton), conn).values[0]
    result = []
    for shape in shapes:
        s = select(t.c.geometry.ST_AsText(), t.c.x, t.c.y).where(t.c.geometry.intersects(shape))
        df = pd.read_sql(s, conn)
        def convert_cluster(cluster):
            return [[float(y) for y in x.split()] for x in cluster.replace('MULTIPOINT(', '').replace(')', '').split(',')]
        result += df[df.columns[0]].apply(convert_cluster).to_list()
    return result


def get_surfaces(t, x1, y1, x2=None, y2=None):
    if x2 is None:
        x2 = x1 + 1
    if y2 is None:
        y2 = y1 + 1

    polygon = tuple(x * 1000 for x in [x1, y1, x1, y2, x2, y2, x2, y1, x1, y1])
    s = select(t.c.shape.ST_AsText(), t.c.sb_uuid, t.c.df_uid, t.c.gstrahlung, t.c.flaeche).where(
        t.c.shape.intersects('POLYGON((%u %u,%u %u,%u %u,%u %u,%u %u))' % polygon)).limit(1000)
    df = pd.read_sql(s, conn)

    def convert_elem(elem):
        l = [[y.replace('(', '').replace(')', '').split() for y in x.split(',')] for x in
             elem.replace('MULTIPOLYGON((', '').replace('))', '').split('),(')]
        return [[(float(cx) - x1 * 1000, float(cy) - y1 * 1000) for cx, cy in y] for y in l]

    df['shape'] = df[df.columns[0]].apply(convert_elem)
    return df.iloc[:, 1:]


def get_roofs(*args):
    return get_surfaces(dach, *args)


#def get_facades(*args):
#    return get_surfaces(fass, *args)


def get_roof_monthly(df_uid):
    s = dach_monat.select().where(dach_monat.c.df_uid == df_uid)
    return pd.read_sql(s, conn)


def get_building_potential(sb_uuid):
    return pd.read_sql(select(buildings).where(buildings.c.sb_uuid == sb_uuid), conn).iloc[0, :]