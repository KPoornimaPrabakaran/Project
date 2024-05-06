# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import eval_pairwise_summarization_quality
import eval_rouge

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
REGION = "us-central1"
MODEL_ID = "gemini-1.5-pro-preview-0409"

def test_eval_pairwise_summarization_quality() -> None:
    response = eval_pairwise_summarization_quality.generate_content(PROJECT_ID, REGION)
    assert response

def test_eval_rouge() -> None:
    response = eval_rouge.generate_content(PROJECT_ID, REGION)
    assert response