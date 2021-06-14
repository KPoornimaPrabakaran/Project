# Copyright 2021 Google LLC
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

from functools import reduce
from typing import Any, Dict, Tuple

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers.experimental import preprocessing


# Time steps before and after a point to consider for prediction.
PADDING = 24

INPUTS_SPEC = {
    "distance_from_port": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
    "speed": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
    "course": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
    "lat": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
    "lon": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
}

OUTPUTS_SPEC = {
    "is_fishing": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
}


def validated(
    tensor_dict: Dict[str, tf.Tensor],
    spec_dict: Dict[str, tf.TypeSpec],
) -> Dict[str, tf.Tensor]:
    for field, spec in spec_dict.items():
        if field not in tensor_dict:
            raise KeyError(
                f"missing field '{field}', got={tensor_dict.keys()}, expected={spec_dict.keys()}"
            )
        if not spec.dtype.is_compatible_with(tensor_dict[field].dtype):
            raise TypeError(
                f"incompatible type in '{field}', got={tensor_dict[field].dtype}, expected={spec.dtype}"
            )
        if not spec.shape.is_compatible_with(tensor_dict[field].shape):
            raise ValueError(
                f"incompatible shape in '{field}', got={tensor_dict[field].shape}, expected={spec.shape}"
            )
    return tensor_dict


def serialize(value_dict: Dict[str, Any]) -> bytes:
    spec_dict = {**INPUTS_SPEC, **OUTPUTS_SPEC}
    tensor_dict = {
        field: tf.convert_to_tensor(value, spec_dict[field].dtype)
        for field, value in value_dict.items()
    }
    validated_tensor_dict = validated(tensor_dict, spec_dict)

    example = tf.train.Example(
        features=tf.train.Features(
            feature={
                field: tf.train.Feature(
                    bytes_list=tf.train.BytesList(
                        value=[tf.io.serialize_tensor(value).numpy()]
                    )
                )
                for field, value in validated_tensor_dict.items()
            }
        )
    )
    return example.SerializeToString()


def deserialize(
    serialized_example: bytes,
) -> Tuple[Dict[str, tf.Tensor], Dict[str, tf.Tensor]]:
    features = {
        field: tf.io.FixedLenFeature(shape=(), dtype=tf.string)
        for field in [*INPUTS_SPEC.keys(), *OUTPUTS_SPEC.keys()]
    }
    example = tf.io.parse_example(serialized_example, features)

    def parse_tensor(bytes_value: bytes, spec: tf.TypeSpec) -> tf.Tensor:
        tensor = tf.io.parse_tensor(bytes_value, spec.dtype)
        tensor.set_shape(spec.shape)
        return tensor

    def parse_features(spec_dict: Dict[str, tf.TypeSpec]) -> Dict[str, tf.Tensor]:
        tensor_dict = {
            field: parse_tensor(bytes_value, spec_dict[field])
            for field, bytes_value in example.items()
            if field in spec_dict
        }
        return validated(tensor_dict, spec_dict)

    return parse_features(INPUTS_SPEC), parse_features(OUTPUTS_SPEC)


def build_dataset(files_pattern: str, batch_size: int = 64) -> tf.data.Dataset:
    file_names = tf.io.gfile.glob(files_pattern)
    return (
        tf.data.TFRecordDataset(file_names, compression_type="GZIP")
        .map(deserialize, num_parallel_calls=tf.data.AUTOTUNE)
        .cache()
        .shuffle(batch_size * 100)
        .batch(batch_size)
        .prefetch(tf.data.AUTOTUNE)
    )


def build_model(train_dataset: tf.data.Dataset) -> keras.Model:
    input_layers = {
        field: keras.layers.Input(shape=spec.shape, dtype=spec.dtype, name=field)
        for field, spec in INPUTS_SPEC.items()
    }

    def normalize(field: str):
        layer = preprocessing.Normalization(name=f"{field}_normalized")
        layer.adapt(train_dataset.map(lambda inputs, outputs: inputs[field]))
        return layer(input_layers[field])

    def geo_point(lat_field: str, lon_field: str):
        # https://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates
        class GeoPoint(keras.layers.Layer):
            def call(self, latlon):
                lat, lon = latlon
                x = tf.cos(lon) * tf.sin(lat)
                y = tf.sin(lon) * tf.sin(lat)
                z = tf.cos(lat)
                return tf.concat([x, y, z], axis=-1)

        lat_input = input_layers[lat_field]
        lon_input = input_layers[lon_field]
        return GeoPoint(name=f"{lat_field}_{lon_field}")((lat_input, lon_input))

    def sequential_layers(first_layer, *layers) -> keras.layers.Layer:
        return reduce(lambda layer, result: result(layer), layers, first_layer)

    preprocessed_inputs = [
        normalize("distance_from_port"),
        normalize("speed"),
        normalize("course"),
        geo_point("lat", "lon"),
    ]

    output_layers = {
        "is_fishing": sequential_layers(
            keras.layers.concatenate(preprocessed_inputs, name="deep_layers"),
            keras.layers.Conv1D(
                filters=8,
                kernel_size=PADDING + 1 + PADDING,
                data_format="channels_last",
                activation="relu",
            ),
            keras.layers.Dense(16, "relu"),
            keras.layers.Dense(4, "relu"),
            keras.layers.Dense(1, "sigmoid", name="is_fishing"),
        )
    }
    return keras.Model(input_layers, output_layers)


def run(
    train_files: str,
    eval_files: str,
    model_dir: str,
    tensorboard_dir: str,
    train_steps=1000,
    eval_steps=100,
) -> None:
    # Create the training and evaluation datasets from the TFRecord files.
    train_dataset = build_dataset(train_files)
    eval_dataset = build_dataset(eval_files)

    # Build and compile the model.
    model = build_model(train_dataset)
    model.compile(
        optimizer="adam",
        loss={"is_fishing": "binary_crossentropy"},
        metrics={"is_fishing": ["accuracy"]},
    )

    # Train the model.
    model.fit(
        train_dataset.repeat(),
        steps_per_epoch=train_steps,
        validation_data=eval_dataset.repeat(),
        validation_steps=eval_steps,
        callbacks=[keras.callbacks.TensorBoard(tensorboard_dir, update_freq="batch")],
    )

    # Save the trained model.
    model.save(model_dir)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("--trian-files", required=True)
    parser.add_argument("--eval-files", required=True)
    parser.add_argument("--model-dir", default=os.environ.get("AIP_MODEL_DIR", "model"))
    parser.add_argument("--tensorboard-dir", default="tensorboard")
    args = parser.parse_args()

    run(
        train_files=args.train_files,
        eval_files=args.eval_files,
        model_dir=args.output_dir,
        tensorboard_dir=args.tensorboard_dir,
    )
