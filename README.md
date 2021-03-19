# geohackmin-swiss-solar-potential
Geo.Hackmin Week solar potential project


# Instructions

1) Clone existing solar panel detection model

`git clone https://github.com/dbaofd/solar-panels-detection`

2) Download & extract EPFL article data

````shell
python download_epfl_data.py
python upload_epfl_data.py
````

3) Download & extract geo.admin.ch data

````shell
python download_geoadmin_data.py
python upload_geoadmin_gdb_data.py
````

4) Merge data into combined tables

`python extract relevant data`

4) Download swissimage data (follow instructions in python file)

`python download_swissimage_data.py filename.csv`

5) Run solar panel detection script on swissimage data

`python detect_solar_panels.py`

6) Run demo

`python app.py`


