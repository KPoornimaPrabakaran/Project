# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import google.auth

# HTTP Queues are currently in public beta
from google.cloud import tasks_v2beta3 as tasks

import pytest

import update_http_queue


HOST = "example.com"
LOCATION = "us-central1"


@pytest.fixture
def q():
    # Use the default project and a random name for the test queue
    _, project = google.auth.default()
    name = uuid.uuid4().hex

    http_target = {
        "uri_override": {
            "host": HOST,
            "uri_override_enforce_mode": 2,  # ALWAYS use this endpoint
        }
    }

    # Use the client to send a CreateQueueRequest.
    client = tasks.CloudTasksClient()
    queue = client.create_queue(
        tasks.CreateQueueRequest(
            parent=client.common_location_path(project, LOCATION),
            queue={
                "name": f"projects/{project}/locations/{LOCATION}/queues/{name}",
                "http_target": http_target,
            },
        )
    )

    yield queue

    try:
        client.delete_queue(name=queue.name)
    except Exception as e:
        print(f"Tried my best to clean up, but could not: {e}")


def test_update_http_queue(q) -> None:
    print(f"Queue name is {q.name}")
    q = update_http_queue.update_http_queue(q, uri="https://example.com/somepath")
    assert q.http_target.uri_override.scheme != 1
    assert q.http_target.uri_override.path_override.path == "/somepath"

    print(f"Queue name is {q.name}")
    q = update_http_queue.update_http_queue(q, max_per_second=5.0, max_attempts=2)
    assert q.rate_limits is not None
    assert q.rate_limits.max_dispatches_per_second == 5.0
    assert q.retry_config.max_attempts == 2
