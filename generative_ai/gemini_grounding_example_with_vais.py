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

# [START generativeaionvertexai_gemini_grounding_with_vais]
from typing import Optional

import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
    grounding,
    Tool,
)


def generate_text_with_grounding(
    project_id: str, location: str, data_store_path: str
) -> GenerationResponse:
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    # Load the model
    model = GenerativeModel(model_name="gemini-1.0-pro")

    # Use Vertex AI Search data store
    # Format: projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}
    tool = Tool.from_retrieval(
        grounding.Retrieval(grounding.VertexAISearch(datastore=data_store_path))
    )

    prompt = "When is the next total solar eclipse in US?"
    response = model.generate_content(prompt, 
                                    tools=[tool], 
                                    generation_config=GenerationConfig(
                                        temperature=0.0,
                                    ))

    print(response)

    # [END generativeaionvertexai_gemini_grounding_with_vais]
    return response
