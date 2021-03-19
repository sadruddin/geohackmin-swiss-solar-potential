import glob
import os
import zipfile

urls = ['https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill/gdb/2056/ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill.zip',
        'https://data.geo.admin.ch/ch.bfe.solarenergie-eignung-daecher/gdb/2056/ch.bfe.solarenergie-eignung-daecher.zip',
        'https://data.geo.admin.ch/ch.bfe.solarenergie-eignung-daecher/gdb/2056/ch.bfe.solarenergie-eignung-daecher_monatswerte.zip'
        ]

for url in urls:
    os.system(f'wget -P data/geoadmin -c {url}')

for filename in glob.glob('data/geoadmin/*.zip'):
    print(f'Extracting zipfile {filename}')
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('data/geoadmin')