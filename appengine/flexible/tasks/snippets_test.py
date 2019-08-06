# Copyright 2019 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest
import uuid

import snippets

TEST_PROJECT_ID = os.getenv('GCLOUD_PROJECT')
TEST_LOCATION = os.getenv('TEST_QUEUE_LOCATION', 'us-central1')
QUEUE_NAME_1 = "queue-{}".format(uuid.uuid4())
QUEUE_NAME_2 = "queue-{}".format(uuid.uuid4())

@pytest.mark.order1
def test_create_queue():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_2)
    result = snippets.create_queue(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1, QUEUE_NAME_2)
    assert name in result.name


@pytest.mark.order2
def test_update_queue():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    result = snippets.update_queue(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    assert name in result.name


@pytest.mark.order3
def test_create_task():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    result = snippets.create_task(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    assert name in result.name


@pytest.mark.order4
def test_create_task_with_data():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    result = snippets.create_tasks_with_data(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    assert name in result.name


@pytest.mark.order5
def test_create_task_with_name():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    result = snippets.create_task_with_name(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1, 'foo')
    assert name in result.name


@pytest.mark.order6
def test_delete_task():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    result = snippets.delete_task(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    assert name in result.name


@pytest.mark.order8
def test_delete_queue():
    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    result = snippets.delete_queue(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_1)
    assert None == result

    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_2)
    result = snippets.delete_queue(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME_2)
    assert None == result


@pytest.mark.order7
def test_retry_task():
    QUEUE_NAME = []
    for i in range(3):
        QUEUE_NAME.append("queue-{}".format(uuid.uuid4()))

    name = "projects/{}/locations/{}/queues/{}".format(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME[2])
    result = snippets.retry_task(
        TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME[0], QUEUE_NAME[1], QUEUE_NAME[2])
    assert name in result.name

    for i in range(3):
        snippets.delete_queue(
            TEST_PROJECT_ID, TEST_LOCATION, QUEUE_NAME[i])
