#!/usr/bin/env python

# Copyright 2019 Google, Inc
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

import backoff
from google.api_core.exceptions import DeadlineExceeded
import pytest

import create_annotation_spec_set
import testing_lib


PROJECT_ID = os.getenv('GCLOUD_PROJECT')


@pytest.fixture(scope='module')
def cleaner():
    resource_names = []

    yield resource_names

    for resource_name in resource_names:
        testing_lib.delete_annotation_spec_set(resource_name)


def test_create_annotation_spec_set(cleaner, capsys):

    @backoff.on_exception(backoff.expo, DeadlineExceeded, max_time=60)
    def run_sample():
        return create_annotation_spec_set.create_annotation_spec_set(PROJECT_ID)

    response = run_sample()

    # For cleanup
    cleaner.append(response.name)

    out, _ = capsys.readouterr()
    assert 'The annotation_spec_set resource name:' in out
