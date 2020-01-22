# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START vision_batch_annotate_files_gcs]

from google.cloud import vision_v1
from google.cloud.vision_v1 import enums


def sample_batch_annotate_files(
    storage_uri="gs://cloud-samples-data/vision/document_understanding/kafka.pdf",
):
    """
    Perform batch file annotation

    Args:
      storage_uri Cloud Storage URI to source image in the format
        gs://[bucket]/ [file]
    """
    # [START vision_batch_annotate_files_gcs_core]
    mime_type = "application/pdf"

    client = vision_v1.ImageAnnotatorClient()

    # storage_uri = (
    #    "gs://cloud-samples-data/vision/document_understanding/kafka.pdf"
    # )

    gcs_source = {"uri": storage_uri}
    input_config = {"gcs_source": gcs_source, "mime_type": mime_type}
    type_ = enums.Feature.Type.DOCUMENT_TEXT_DETECTION
    features_element = {"type": type_}
    features = [features_element]

    # The service can process up to 5 pages per document file.
    # Here we specify the first, second, and last page of the document to be
    # processed.
    pages_element = 1
    pages_element_2 = 2
    pages_element_3 = -1
    pages = [pages_element, pages_element_2, pages_element_3]
    requests_element = {
        "input_config": input_config,
        "features": features,
        "pages": pages,
    }
    requests = [requests_element]

    response = client.batch_annotate_files(requests)
    for image_response in response.responses[0].responses:
        print(u"Full text: {}".format(image_response.full_text_annotation.text))
        for page in image_response.full_text_annotation.pages:
            for block in page.blocks:
                print(u"\nBlock confidence: {}".format(block.confidence))
                for par in block.paragraphs:
                    print(u"\tParagraph confidence: {}".format(par.confidence))
                    for word in par.words:
                        print(u"\t\tWord confidence: {}".format(word.confidence))
                        for symbol in word.symbols:
                            print(
                                u"\t\t\tSymbol: {}, (confidence: {})".format(
                                    symbol.text, symbol.confidence
                                )
                            )

    # [END vision_batch_annotate_files_gcs_core]


# [END vision_batch_annotate_files_gcs]
