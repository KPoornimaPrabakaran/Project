#!/bin/python
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START containeranalysis_delete_occurrence]
from google.cloud.devtools import containeranalysis_v1


def delete_occurrence(occurrence_id: str, project_id: str) -> None:
    """Removes an existing occurrence from the server."""
    # occurrence_id = basename(occurrence.name)
    # project_id = 'my-gcp-project'

    client = containeranalysis_v1.ContainerAnalysisClient()
    grafeas_client = client.get_grafeas_client()
    parent = f"projects/{project_id}/occurrences/{occurrence_id}"
    grafeas_client.delete_occurrence(name=parent)


# [END containeranalysis_delete_occurrence]
