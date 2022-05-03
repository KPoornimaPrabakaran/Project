# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import io
from typing import Dict, List, Optional

import apache_beam as beam
from apache_beam.io.filesystems import FileSystems
from apache_beam.options.pipeline_options import PipelineOptions
import ee
from google.api_core import exceptions, retry
import google.auth
import numpy as np
import requests


def ee_init() -> None:
    credentials, project = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/earthengine",
        ]
    )
    ee.Initialize(
        credentials,
        project=project,
        opt_url="https://earthengine-highvolume.googleapis.com",
    )


def sentinel2_image(start_date: str, end_date: str) -> ee.Image:
    def mask_sentinel2_clouds(image: ee.Image) -> ee.Image:
        CLOUD_BIT = 10
        CIRRUS_CLOUD_BIT = 11
        bit_mask = (1 << CLOUD_BIT) | (1 << CIRRUS_CLOUD_BIT)
        mask = image.select("QA60").bitwiseAnd(bit_mask).eq(0)
        return image.updateMask(mask)

    return (
        ee.ImageCollection("COPERNICUS/S2")
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(mask_sentinel2_clouds)
        .median()
    )


@retry.Retry()
def get_patch(
    image: ee.Image,
    lat: float,
    lon: float,
    bands: List[str],
    patch_size: int,
    scale: int,
) -> np.ndarray:
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(scale * patch_size / 2, 1).bounds(1)
    url = image.getDownloadURL(
        {
            "region": region,
            "dimensions": [patch_size, patch_size],
            "format": "NPY",
            "bands": bands or image.bandNames().getInfo(),
        }
    )

    response = requests.get(url)
    if response.status_code == 429:
        raise exceptions.TooManyRequests(response.text)
    response.raise_for_status()

    print(f"Got patch for {(lat, lon)}")
    return np.load(io.BytesIO(response.content), allow_pickle=True)


def get_prediction_patch(
    region: Dict, bands: List[str] = [], patch_size: int = 256
) -> np.ndarray:
    ee_init()
    lat = float(region["lat"])
    lon = float(region["lon"])
    year = int(region["year"])

    filename = f"{region['name']}/{year}"
    image = sentinel2_image(f"{year}-1-1", f"{year + 1}-1-1")
    patch = get_patch(image, lat, lon, bands, patch_size, scale=10)
    return (filename, patch)


def predict(filename: str, patch: np.ndarray, model_path: str = "model") -> Dict:
    import tensorflow as tf

    model = tf.keras.models.load_model(model_path)
    inputs = np.stack([patch[name] for name in patch.dtype.names], axis=-1)
    probabilities = model.predict(np.stack([inputs]))[0]
    outputs = np.argmax(probabilities, axis=-1)
    return {
        "name": filename,
        "inputs": patch,
        "outputs": outputs,
    }


def write_to_numpy(results: Dict, predictions_prefix: str = "predictions") -> str:
    filename = f"{predictions_prefix}/{results['name']}.npz"
    with FileSystems.create(filename) as f:
        np.savez_compressed(f, inputs=results["inputs"], outputs=results["outputs"])
    return filename


def run(
    regions_file: str = "data/prediction-locations.csv",
    model_path: str = "model",
    predictions_prefix: str = "predictions",
    patch_size: int = 256,
    beam_args: Optional[List[str]] = None,
) -> None:
    import trainer

    with open(regions_file) as f:
        regions = [dict(row) for row in csv.DictReader(f)]

    bands = trainer.INPUT_BANDS
    beam_options = PipelineOptions(beam_args, save_main_session=True)
    with beam.Pipeline(options=beam_options) as pipeline:
        (
            pipeline
            | "Create regions" >> beam.Create(regions)
            | "Get patch" >> beam.Map(get_prediction_patch, bands, patch_size)
            | "Predict" >> beam.MapTuple(predict, model_path)
            | "Write to NumPy" >> beam.Map(write_to_numpy, predictions_prefix)
        )


if __name__ == "__main__":
    import argparse
    import logging

    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--regions-file",
        default="data/prediction-locations.csv",
        help="CSV file with the locations and years to predict.",
    )
    parser.add_argument(
        "--model-path",
        default="model",
        help="Local or Cloud Storage path of the trained model to use.",
    )
    parser.add_argument(
        "--predictions-prefix",
        default="predictions",
        help="Local or Cloud Storage path prefix to save the prediction results.",
    )
    parser.add_argument(
        "--patch-size",
        default=256,
        type=int,
        help="Length of the patch square for each region to predict.",
    )
    args, beam_args = parser.parse_known_args()

    run(**vars(args), beam_args=beam_args)
