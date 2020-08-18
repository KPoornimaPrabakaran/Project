# Copyright 2020 Google, LLC.
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

# [START run_events_pubsub_server_setup]
from cloudevents.http import from_http
import cloudevents.exceptions as cloud_exceptions
import base64
import os

from flask import Flask, request


required_fields = ['Ce-Id', 'Ce-Source', 'Ce-Type', 'Ce-Specversion']

app = Flask(__name__)
# [END run_events_pubsub_server_setup]


# [START run_events_pubsub_handler]
@app.route('/', methods=['POST'])
def index():
    # Create CloudEvent from HTTP headers and body
    try:
        event = from_http(request.headers, request.get_data())

    except cloud_exceptions.MissingRequiredFields as e:
        print(f"cloudevents.exceptions.MissingRequiredFields: {e}")
        return f"Failed to find all required cloudevent fields. ", 400

    except cloud_exceptions.InvalidStructuredJSON as e:
        print(f"cloudevents.exceptions.InvalidStructuredJSON: {e}")
        return f"Could not deserialize the payload as JSON. ", 400

    except cloud_exceptions.InvalidRequiredFields as e:
        print(f"cloudevents.exceptions.InvalidRequiredFields: {e}")
        return f"Request contained invalid required cloudevent fields. ", 400

    envelope = event.data

    if not envelope:
        msg = 'no Pub/Sub message received'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        msg = 'invalid Pub/Sub message format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    pubsub_message = envelope['message']

    name = 'World'
    if isinstance(pubsub_message, dict) and 'data' in pubsub_message:
        name = base64.b64decode(pubsub_message['data']).decode('utf-8').strip()

    resp = f'Hello, {name}! ID: {event['id']}'
    print(resp)
    return (resp, 200)
# [END run_events_pubsub_handler]


# [START run_events_pubsub_server]
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# [END run_events_pubsub_server]
