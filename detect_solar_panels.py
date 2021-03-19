import math
import sys

import numpy as np
import geopandas
import tensorflow as tf

from tqdm import tqdm
from shapely.geometry import MultiPoint


from config import conn

def get_model():
    spd_path = 'solar-panels-detection'
    sys.path.append(spd_path)

    from model_application.model_list import segnet_0

    BATCH_SIZE= 16
    INPUT_SHAPE= (256, 256, 3)

    MODEL_PATH = f"{spd_path}/trained_models/"
    TRAINED_MODELS=["fast_scnn_1.h5",
                    "fast_scnn_2.h5",
                    "seg_resnet_1.h5",
                    "seg_resnet_2.h5",
                    "segnet_1.h5",
                    "segnet_2.h5",
                    "segnet_original.h5",
                    "fast_scnn_original.h5"]
    model_0 = segnet_0.segnet_original(input_shape=INPUT_SHAPE, batch_size=BATCH_SIZE, n_labels=2, model_summary=False)
    model_0.load_weights(MODEL_PATH+TRAINED_MODELS[6])
    return model_0


offset = ((1024*10) - 10000)/9

model_0 = get_model()


def detect_solar_panels(img):
    size = img.shape[0]//256
    boxes = np.zeros((size ** 2, 4))
    count = 0
    for i in range(size):
        for j in range(size):
            boxes[count, :] = i / size, j / size, (i + 1) / size, (j + 1) / size
            count += 1
    arr = img.reshape((1,) + img.shape)
    imgs = tf.image.crop_and_resize(arr, boxes, [0 for x in boxes], [256, 256])

    subset = imgs/255.0
    result = model_0(subset)
    # subset = np.array(subset, dtype=int)
    rows = []
    for i in range(size):
        col = []
        for j in range(size):
            col.append(result[i * size + j])
        rows.append(np.concatenate(col, axis=1))
    result = np.concatenate(rows, axis=0)
    return result


def detect_by_tile(maptile):
    rows = []
    for i in tqdm(range(10)):
        col = []
        for j in range(10):
            dx = math.floor((1024 - offset)*i)
            dy = math.floor((1024 - offset)*j)
            img = np.array(maptile[dx:dx+256*4, dy:dy+256*4,:], int)

            solar = detect_solar_panels(img)
            sx = (10000 - dx) % 1000
            sy = (10000 - dy) % 1000
            col.append(solar[sx:sx+1000, sy:sy+1000])
        rows.append(np.concatenate(col, axis=1))
    return np.concatenate(rows, axis=0)


def process_maptile(mapfile):
    image = tf.keras.preprocessing.image.load_img(
        mapfile, grayscale=False, color_mode="rgb", target_size=None, interpolation="nearest"
    )
    maptile = tf.keras.preprocessing.image.img_to_array(image)
    solar = detect_by_tile(maptile)
    matches = np.nonzero(solar[:, :, 1] > 0.5)
    matches = np.array(matches).T

    from sklearn.cluster import DBSCAN

    if matches.shape[0] == 0:
        return []

    db = (DBSCAN(eps=40, min_samples=20, algorithm='ball_tree', metric = 'euclidean').fit(matches))

    result = []
    for label in np.unique(db.labels_):
        if label == -1:
            continue
        result.append(matches[db.labels_ == label, :])
    return result


if __name__ == '__main__':
    import glob

    for mapfile in tqdm(glob.glob('data/swissimage/*.tif')):
        x, y = map(int, mapfile[-22:-13].split('-'))
        clusters = process_maptile(mapfile)

        def get_shape_from_cluster(cluster):
            return MultiPoint([(x2/10 + x*1000, -x1/10 + (y + 1)*1000) for x1, x2 in cluster])

        df = geopandas.GeoDataFrame({'geometry': map(get_shape_from_cluster, clusters), 'x': x, 'y': y}, crs='EPSG:2056')
        df.to_postgis('detected_solar_panels', conn, if_exists='append', index=False)