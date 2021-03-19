import os

urls = ['https://zenodo.org/record/3609833/files/rooftop_PV_CH_annual_by_building.csv',
        'https://zenodo.org/record/3609833/files/rooftop_PV_CH_EPV_W_by_building.csv',
        'https://zenodo.org/record/3609833/files/rooftop_PV_CH_EPV_W_std_by_building.csv',
        'https://zenodo.org/record/3609833/files/rooftop_PV_CH_Gt_W_m2_by_building.csv',
        'https://zenodo.org/record/3609833/files/rooftop_PV_CH_Gt_W_m2_std_by_building.csv']

# Only process the high-level file for now
urls = urls[:1]

# Download files
for url in urls:
    os.system(f'wget -P data/epfl -c {url}')