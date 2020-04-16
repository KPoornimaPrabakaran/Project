# Copyright 2020 Google LLC
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
# See the License for the specific ladnguage governing permissions and
# limitations under the License.

import os
import set_endpoint

PROJECT_ID = os.environ['GCLOUD_PROJECT']
INPUT_URI = 'gs://cloud-samples-data/documentai/invoice.pdf'


def test_set_endpoint(capsys):
    set_endpoint.set_endpoint(PROJECT_ID, INPUT_URI)
    out, _ = capsys.readouterr()
    assert 'Entity type' in out
    assert 'Mention text' in out
