#!/usr/bin/env python

# Copyright 2018 Google LLC
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

"""
Google Cloud Vision API Python Beta Snippets

Example Usage:
python beta_snippets.py -h
python beta_snippets.py object-localization INPUT_IMAGE
python beta_snippets.py object-localization-uri gs://...
python beta_snippets.py handwritten-ocr INPUT_IMAGE
python beta_snippets.py handwritten-ocr-uri gs://...


For more information, the documentation at
https://cloud.google.com/vision/docs.
"""

import argparse
import io


# [START vision_localize_objects_beta]
def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision_v1p3beta1 as vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
# [END vision_localize_objects_beta]


# [START vision_localize_objects_gcs_beta]
def localize_objects_uri(uri):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision_v1p3beta1 as vision
    client = vision.ImageAnnotatorClient()

    image = vision.types.Image()
    image.source.image_uri = uri

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
# [END vision_localize_objects_gcs_beta]


# [START vision_handwritten_ocr_beta]
def detect_handwritten_ocr(path):
    """Detects handwritten characters in a local image.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision_v1p3beta1 as vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Language hint codes for handwritten OCR:
    # en-t-i0-handwrit, mul-Latn-t-i0-handwrit
    # Note: Use only one language hint code per request for handwritten OCR.
    image_context = vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])

    response = client.document_text_detection(image=image,
                                              image_context=image_context)

    print('Full Text: {}'.format(response.full_text_annotation.text))
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))
# [END vision_handwritten_ocr_beta]


# [START vision_handwritten_ocr_gcs_beta]
def detect_handwritten_ocr_uri(uri):
    """Detects handwritten characters in the file located in Google Cloud
    Storage.

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision_v1p3beta1 as vision
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    # Language hint codes for handwritten OCR:
    # en-t-i0-handwrit, mul-Latn-t-i0-handwrit
    # Note: Use only one language hint code per request for handwritten OCR.
    image_context = vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])

    response = client.document_text_detection(image=image,
                                              image_context=image_context)

    print('Full Text: {}'.format(response.full_text_annotation.text))
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))
# [END vision_handwritten_ocr_gcs_beta]


# [START vision_fulltext_detection_pdf_beta]
def detect_document_features(path):
    """Detects document features in a PDF/TIFF/GIF file.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision_v1p4beta1 as vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as pdf_file:
        content = pdf_file.read()

    # Other supported mime_types: image/tiff' or 'image/gif'
    mime_type = 'application/pdf'
    input_config = vision.types.InputConfig(
        content=content, mime_type=mime_type)

    feature = vision.types.Feature(
        type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)
    # Annotate the first two pages and the last one (max 5 pages)
    # First page starts at 1, and not 0. Last page is -1.
    pages = [1, 2, -1]

    online_one_request = vision.types.AnnotateFileRequest(
        input_config=input_config,
        features=[feature],
        pages=pages)

    response = client.batch_annotate_files(requests=[online_one_request])

    for image_response in response.responses[0].responses:
        for page in image_response.full_text_annotation.pages:
            for block in page.blocks:
                print('\nBlock confidence: {}\n'.format(block.confidence))
                for par in block.paragraphs:
                    print('\tParagraph confidence: {}'.format(par.confidence))
                    for word in par.words:
                        symbol_texts = [symbol.text for symbol in word.symbols]
                        word_text = ''.join(symbol_texts)
                        print('\t\tWord text: {} (confidence: {})'.format(
                            word_text, word.confidence))
                        for symbol in word.symbols:
                            print('\t\t\tSymbol: {} (confidence: {})'.format(
                                symbol.text, symbol.confidence))
# [END vision_fulltext_detection_pdf_beta]


# [START vision_fulltext_detection_pdf_gcs_beta]
def detect_document_features_uri(gcs_uri):
    """Detects document features in a PDF/TIFF/GIF  file.

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision_v1p4beta1 as vision
    client = vision.ImageAnnotatorClient()

    # Other supported mime_types: image/tiff' or 'image/gif'
    mime_type = 'application/pdf'
    input_config = vision.types.InputConfig(
        gcs_source=vision.types.GcsSource(uri=gcs_uri), mime_type=mime_type)

    feature = vision.types.Feature(
        type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)
    # Annotate the first two pages and the last one (max 5 pages)
    # First page starts at 1, and not 0. Last page is -1.
    pages = [1, 2, -1]

    online_one_request = vision.types.AnnotateFileRequest(
        input_config=input_config,
        features=[feature],
        pages=pages)

    response = client.batch_annotate_files(requests=[online_one_request])

    for image_response in response.responses[0].responses:
        for page in image_response.full_text_annotation.pages:
            for block in page.blocks:
                print('\nBlock confidence: {}\n'.format(block.confidence))
                for par in block.paragraphs:
                    print('\tParagraph confidence: {}'.format(par.confidence))
                    for word in par.words:
                        symbol_texts = [symbol.text for symbol in word.symbols]
                        word_text = ''.join(symbol_texts)
                        print('\t\tWord text: {} (confidence: {})'.format(
                            word_text, word.confidence))
                        for symbol in word.symbols:
                            print('\t\t\tSymbol: {} (confidence: {})'.format(
                                symbol.text, symbol.confidence))
# [END vision_fulltext_detection_pdf_gcs_beta]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')

    object_parser = subparsers.add_parser(
        'object-localization', help=localize_objects.__doc__)
    object_parser.add_argument('path')

    object_uri_parser = subparsers.add_parser(
        'object-localization-uri', help=localize_objects_uri.__doc__)
    object_uri_parser.add_argument('uri')

    handwritten_parser = subparsers.add_parser(
        'handwritten-ocr', help=detect_handwritten_ocr.__doc__)
    handwritten_parser.add_argument('path')

    handwritten_uri_parser = subparsers.add_parser(
        'handwritten-ocr-uri', help=detect_handwritten_ocr_uri.__doc__)
    handwritten_uri_parser.add_argument('uri')

    doc_features_parser = subparsers.add_parser(
        'doc-features', help=detect_document_features.__doc__)
    doc_features_parser.add_argument('path')

    doc_features_uri_parser = subparsers.add_parser(
        'doc-features-uri', help=detect_document_features_uri.__doc__)
    doc_features_uri_parser.add_argument('uri')

    args = parser.parse_args()

    if 'uri' in args.command:
        if 'object-localization-uri' in args.command:
            localize_objects_uri(args.uri)
        elif 'handwritten-ocr-uri' in args.command:
            detect_handwritten_ocr_uri(args.uri)
        elif 'doc-features' in args.command:
            detect_handwritten_ocr_uri(args.uri)
    else:
        if 'object-localization' in args.command:
            localize_objects(args.path)
        elif 'handwritten-ocr' in args.command:
            detect_handwritten_ocr(args.path)
        elif 'doc-features' in args.command:
            detect_handwritten_ocr(args.uri)
