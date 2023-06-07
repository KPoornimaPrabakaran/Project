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

# [START eventarc_audit_storage_server]
import os

from flask import Flask, request
from cloudevents.http import from_http
from google.protobuf import json_format
from google.events.cloud.storage import StorageObjectData

app = Flask(__name__)
# [END eventarc_storage_server]


# [START eventarc_storage_handler]
@app.route("/", methods=["POST"])
def index():
    print("HEADERS:")
    event = from_http(request.headers, request.get_data())

    # Gets the GCS bucket name from the CloudEvent header
    # Example: "storage.googleapis.com/projects/_/buckets/my-bucket"
    bucket = event.get("subject")

    storage_obj = StorageObjectData(event.data)

    gcs_object = os.path.join(storage_obj.bucket, storage_obj.name)
    update_time = storage_obj.updated
    return (f"Cloud Storage object changed: {gcs_object} updated at {update_time}", 200)


# [END eventarc_audit_storage_handler]


# [START eventarc_audit_storage_server]
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
# [END eventarc_audit_storage_server]
