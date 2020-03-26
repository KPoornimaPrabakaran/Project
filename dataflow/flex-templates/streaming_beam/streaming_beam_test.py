# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import multiprocessing as mp
import os
import subprocess as sp
import tempfile
import time

from google.cloud import bigquery
from google.cloud import pubsub

PROJECT = os.environ["GCLOUD_PROJECT"]
DATASET = 'beam_samples'
TABLE = 'streaming_beam_sql'
TOPIC = 'messages'
SUBSCRIPTION = 'messages'


def create_topic_path():
    publisher_client = pubsub.PublisherClient()
    topic_path = publisher_client.topic_path(PROJECT, TOPIC)
    try:
        publisher_client.delete_topic(topic_path)
    except Exception:
        pass
    response = publisher_client.create_topic(topic_path)
    return response.name


def create_subscription(topic_path):
    subscriber = pubsub.SubscriberClient()
    sub_path = subscriber.subscription_path(PROJECT, SUBSCRIPTION)
    try:
        subscriber.delete_subscription(sub_path)
    except Exception:
        pass
    response = subscriber.create_subscription(sub_path, topic_path)
    return response.name


def _infinite_publish_job(topic_path):
    publisher_client = pubsub.PublisherClient()
    while True:
        future = publisher_client.publish(
            topic_path,
            b'{"url": "https://beam.apache.org/", "review": "positive"}')
        future.result()
        time.sleep(10)


def test_dataflow_flex_templates_pubsub_to_bigquery():
    # Create BigQuery client and dataset.
    bigquery_client = bigquery.Client(project=PROJECT)
    dataset_id = '{}.{}'.format(PROJECT, DATASET)
    dataset = bigquery.Dataset(dataset_id)
    dataset = bigquery_client.create_dataset(dataset, exists_ok=True)

    # Create Pubsub topic and subscription.
    topic_path = create_topic_path()
    sub_path = create_subscription(topic_path)

    # Use one process to publish messages to a topic.
    publish_process = mp.Process(target=lambda: _infinite_publish_job(topic_path))

    # Use another process to run the streaming pipeline that should write one
    # row to BigQuery every minute (according to the default window size).
    pipeline_process = mp.Process(target=lambda: sp.call([
        'python',
        'streaming_beam.py',
        '--project',
        PROJECT,
        '--runner',
        'DirectRunner',
        '--temp_location',
        tempfile.mkdtemp(),
        '--input_subscription',
        sub_path,
        '--output_table',
        '{}:{}.{}'.format(PROJECT, DATASET, TABLE),
    ]))

    publish_process.start()
    pipeline_process.start()

    pipeline_process.join(timeout=90)
    publish_process.join(timeout=0)

    pipeline_process.terminate()
    publish_process.terminate()

    # Check for output data in BigQuery.
    time.sleep(10)
    query = 'SELECT * FROM beam_samples.streaming_beam_sql'
    query_job = bigquery_client.query(query)
    rows = query_job.result()
    assert rows.total_rows > 0
    for row in rows:
        assert row['score'] == 1

    # Clean up.
    bigquery_client.delete_table(
        'beam_samples.streaming_beam_sql', not_found_ok=True)
    bigquery_client.delete_dataset(DATASET, not_found_ok=True)
    pubsub.PublisherClient().delete_topic(topic_path)
    pubsub.SubscriberClient().delete_subscription(sub_path)


# TODO:Testcase using Teststream currently does not work as intended.
# The first write to BigQuery fails. Have filed a bug. The test case
# to be changed once the bug gets fixed.
'''
@mock.patch("apache_beam.Pipeline", TestPipeline)
@mock.patch(
    "apache_beam.io.ReadFromPubSub",
    lambda subscription: (
        TestStream()
        .advance_watermark_to(0)
        .advance_processing_time(60)
        .add_elements([TimestampedValue(
            b'{"url": "https://beam.apache.org/", "review": "positive"}',
                1575937195)])
        .advance_processing_time(60)
        .add_elements([TimestampedValue(
            b'{"url": "https://beam.apache.org/", "review": "positive"}',
                1575937255)])
        .advance_watermark_to_infinity()
    ),
)
def test_dataflow_flex_templates_pubsub_to_bigquery():

    # Create BigQuery client, dataset and table.
    bigquery_client = bigquery.Client(project=PROJECT)
    dataset_id = '{}.{}'.format(PROJECT, DATASET)
    dataset = bigquery.Dataset(dataset_id)
    dataset = bigquery_client.create_dataset(dataset, exists_ok=True)

    streaming_beam.run(
        args=[
            "--project",
            PROJECT,
            "--runner",
            "DirectRunner"
        ],
        #input_subscription="unused",
        input_subscription="projects/google.com:clouddfe/subscriptions/messages",
        output_table=PROJECT+":beam_samples.streaming_beam_sql",
    )

    # Check for output data in BigQuery.
    query = 'SELECT * FROM beam_samples.streaming_beam_sql'
    query_job = bigquery_client.query(query)
    rows = query_job.result()
    assert rows.total_rows > 0

    # Clean up.
    bigquery_client.delete_table("beam_samples.streaming_beam_sql", not_found_ok=True)
    bigquery_client.delete_dataset(DATASET, not_found_ok=True)
'''
